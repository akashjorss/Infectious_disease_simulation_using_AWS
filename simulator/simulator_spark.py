import argparse
import math
import random

import matplotlib.pyplot as plt
import pandas as pd
from pyspark import SparkContext
from pyspark.sql import *
from pyspark.sql import functions as F


def point(x_limit, y_limit):
    """
    Generate a random 2D point

    Keyword arguments:
    x_limit -- max range on X-axis
    y_limit -- max range on Y-axis
    """

    assert isinstance(x_limit, int)
    assert isinstance(y_limit, int)

    x = random.uniform(0, x_limit)
    y = random.uniform(0, y_limit)
    return x, y


def initalize_simulation_dataframes(N, x_limit, y_limit, status_type, motion_factor=5):
    """
    Initialize simulation dataframes with random data

    Keyword arguments:
    N -- Population size
    x_limit -- max range on X-axis
    y_limit -- max range on Y-axis
    """

    assert isinstance(N, int)
    assert isinstance(x_limit, int)
    assert isinstance(y_limit, int)

    # Create the covid-19 dataframe, stores the state of all the actors in population
    covid_df = pd.DataFrame(columns="pid,X,Y,Covid19,Day".split(","))

    for i in range(N):
        covid_df.loc[i, "X"], covid_df.loc[i, "Y"] = point(x_limit, y_limit)
        covid_df.loc[i, "pid"] = i
        covid_df.loc[i, "Covid19"] = 0

    sample_size = math.floor(motion_factor)
    movers_list = covid_df.sample(n=sample_size).index.values.tolist()

    covid_df = assign_working_status(covid_df, status_type)

    # data_frame to keep track of daily statistics
    stats_df = pd.DataFrame(columns="Healthy,Covid-19(+),Hospitalized,Cured,Dead,Work".split(","))
    return covid_df, stats_df, movers_list


def assign_working_status(covid_df, status_type):
    """
    Add working status for every person
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid19,Day]
    """

    N = len(covid_df)

    status_list = []
    working_hours = []
    for status, prob in status_type.items():
        status_list.extend([status] * int(prob * N))
        if status == "Working":
            working_hours.extend([40] * int(prob * N))
        else:
            working_hours.extend([0] * int(prob * N))

    if len(status_list) > N:
        status_list = status_list[:N]

    if len(working_hours) > N:
        working_hours = working_hours[:N]

    zip_list = list(zip(status_list, working_hours))

    random.shuffle(zip_list)

    status_list, working_hours = zip(*zip_list)
    covid_df["status"] = status_list
    covid_df["working_hours"] = working_hours
    return covid_df


def get_working_hours(covid_df):
    """
    Add working status for every person
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid-19,Day, status, working_hours]
    """
    return covid_df.groupBy("working_hours").sum().collect()[-1][-1]


def infect(df, day, person):
    """
    Infect a random person from the population
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid-19,Day]
    day -- current day
    person -- person_id to infect
    """
    assert isinstance(day, int)
    assert isinstance(person, int)
    assert person < df.count()

    if random.random() > 0.25 and day > 3:
        return df

    # If the person is not already infected, infect him/her and record the day of infection
    df = df.withColumn("Covid19", F.when(df["pid"] == person, 1).otherwise(df["Covid19"]))
    df = df.withColumn("Day", F.when(df["pid"] == person, day).otherwise(df["Day"]))
    return df


def update_stats_for_day(sc, covid_df, stats_df, day, initial_working_hours):
    """
    Update the statistics for the given day
    Keyword arguments:
    covid_df -- covid dataframe [X,Y,Covid-19,Day]
    stats_df -- stats dataframe [Healthy,Covid-19(+),Hospitalized,Cured,Dead]
    day -- current day
    """
    assert isinstance(day, int)

    covid_count_list = dict(covid_df.groupBy("Covid19").count().collect())

    for value in [1, 0, 115, 7, 666]:
        if value not in covid_count_list.keys():
            covid_count_list[value] = 0

    if day == 0:
        stats_df.loc[day, "Healthy"] = covid_count_list[0]
        stats_df.loc[day, "Covid-19(+)"] = covid_count_list[1]
        stats_df.loc[day, "Hospitalized"] = covid_count_list[115]
        stats_df.loc[day, "Cured"] = covid_count_list[7]
        stats_df.loc[day, "Dead"] = covid_count_list[666]

        stats_df.loc[day, "Work"] = (get_working_hours(covid_df) / initial_working_hours) * 100
    else:
        working_hours = (get_working_hours(covid_df) / initial_working_hours) * 100
        newRow = sc.createDataFrame(
            [
                (
                    covid_count_list[0],
                    covid_count_list[1],
                    covid_count_list[115],
                    covid_count_list[7],
                    covid_count_list[666],
                    working_hours,
                )
            ]
        )

        stats_df = stats_df.union(newRow)

    return covid_df, stats_df


def update_working_hours(covid_df):
    """
    Add working status for every person
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid-19,Day,status, working_hours]
    """

    covid_df = covid_df.withColumn(
        "working_hours", F.when(covid_df["Covid19"] == True, 0).otherwise(covid_df["working_hours"])
    )
    covid_df = covid_df.withColumn(
        "working_hours",
        F.when((covid_df["Covid19"] == 7) & (covid_df["status"] == "Working"), 40).otherwise(covid_df["working_hours"]),
    )
    return covid_df


def kill(df, kill_prob=0.005):
    """
    Kill a fraction of population given by kill_prob
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid-19,Day]
    kill_prob -- kill people by kill_prob (default: 0.005)
    """

    assert isinstance(kill_prob, float)
    assert kill_prob >= 0
    assert kill_prob <= 1

    sample_size = math.floor(df.filter((df["Covid19"] == True) | (df["Covid19"] == 115)).count() * kill_prob)

    try:
        sample_fraction = sample_size / df.filter(df["Covid19"] == True).count()
    except ZeroDivisionError:
        sample_fraction = 0

    if sample_size > df.filter(df["Covid19"] == True).count():
        return df

    df = df.withColumn("survival_chance", F.rand())
    df = df.withColumn(
        "Covid19",
        F.when((df["Covid19"] == True) & (df["survival_chance"] < sample_fraction), 666).otherwise(df["Covid19"]),
    )
    df = df.drop("survival_chance")
    return df


def hospitalize(df, hosp_prob=0.03):
    """
    Hospitalize a fraction of population given by hosp_prob
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid-19,Day]
    hosp_prob -- Hospitalize people by hosp_prob (default: 0.03)
    """

    assert isinstance(hosp_prob, float)
    assert hosp_prob >= 0
    assert hosp_prob <= 1

    sample_size = math.floor(df.filter(df["Covid19"] == True).count() * hosp_prob)
    sample_fraction = sample_size / df.filter(df["Covid19"] == True).count()

    if sample_size > df.filter(df["Covid19"] == True).count():
        return df

    df = df.withColumn("hosp_chance", F.rand())
    df = df.withColumn(
        "Covid19", F.when((df["Covid19"] == True) & (df["hosp_chance"] < sample_fraction), 115).otherwise(df["Covid19"])
    )
    df = df.drop("hosp_chance")
    return df


def cure(df, day):
    """
    Cure people after their quarantine is finished
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid-19,Day]
    day -- current day
    """

    assert isinstance(day, int)

    df = df.withColumn("Covid19", F.when((df["Day"] < day - 10) & (df["Covid19"] == True), 7).otherwise(df["Covid19"]))
    df = df.withColumn("Covid19", F.when((df["Day"] < day - 21) & (df["Covid19"] == 115), 7).otherwise(df["Covid19"]))
    return df


def random_walk(df, movers_list, x_limit, y_limit):
    """
    Talk random steps in the world
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid-19,Day]
    movers_list -- list of people who are moving in the world
    x_limit -- max range on X-axis
    y_limit -- max range on Y-axis
    """

    result = df.collect()
    for i in movers_list:
        if (result[i].Covid19 == 115) or (result[i].Covid19 == 666):
            movers_list.remove(i)

    def get_random(x):
        return random.uniform(1, x / 3)

    udf_get_random = F.udf(get_random)
    df = df.withColumn(
        "X", F.when(df["pid"].isin(movers_list), (df["X"] + udf_get_random(df["X"])) % x_limit).otherwise(df["X"])
    )
    df = df.withColumn(
        "Y", F.when(df["pid"].isin(movers_list), (df["Y"] + udf_get_random(df["Y"])) % y_limit).otherwise(df["Y"])
    )

    # df.filter(df['pid'].isin(movers_list)).show()
    return df, movers_list


def simulate_next_day(covid_df, stats_df, day, movers_list, x_limit, y_limit):
    """
    Simulates the next day given current day data
    Keyword arguments:
    covid_df -- covid dataframe [X,Y,Covid-19,Day]
    stats_df -- stats dataframe [Healthy,Covid-19(+),Hospitalized,Cured,Dead]
    day -- current day
    """

    assert isinstance(day, int)

    day += 1
    covid_df = kill(covid_df)
    covid_df = hospitalize(covid_df)
    covid_df = cure(covid_df, day)
    covid_df, movers_list = random_walk(covid_df, movers_list, x_limit, y_limit)

    return covid_df, stats_df, day, movers_list


def interact(covid_df, day, yesterday_patients, dist_limit):
    """
    Infect people who interact with oneanother
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid-19,Day]
    day -- current day
    """
    assert isinstance(day, int)

    distance_pairs = (
        covid_df["pid", "X", "Y", "Covid19"]
        .crossJoin(covid_df["pid", "X", "Y", "Covid19"])
        .toDF("pid1", "X1", "Y1", "Covid19_1", "pid2", "X2", "Y2", "Covid19_2")
    )

    distance_pairs = distance_pairs.filter(distance_pairs.pid1 != distance_pairs.pid2)

    def get_distance(x1, y1, x2, y2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    udf_get_distance = F.udf(get_distance)

    distance_pairs = distance_pairs.withColumn(
        "EUCLIDEAN_DISTANCE",
        udf_get_distance(distance_pairs.X1, distance_pairs.Y1, distance_pairs.X2, distance_pairs.Y2),
    )

    distance_pairs = distance_pairs.filter(
        (distance_pairs["EUCLIDEAN_DISTANCE"] < dist_limit)
        & (
            ((distance_pairs["Covid19_1"] == 1) & (distance_pairs["Covid19_2"] == 0))
            | ((distance_pairs["Covid19_1"] == 0) & (distance_pairs["Covid19_2"] == 1))
        )
    )

    persons_to_infect = distance_pairs.select("pid1").union(distance_pairs.select("pid2")).distinct()
    persons_to_infect = [row.pid1 for row in persons_to_infect.collect()]

    covid_df = covid_df.withColumn(
        "Covid19", F.when(covid_df["pid"].isin(persons_to_infect), 1).otherwise(covid_df["Covid19"])
    )
    covid_df = covid_df.withColumn(
        "Day", F.when(covid_df["pid"].isin(persons_to_infect), day).otherwise(covid_df["Day"])
    )
    return covid_df


def get_covid_df_plt_color(df):
    """
    Samples colors according to the covid-state of the persn
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid-19,Day]
    """

    assert isinstance(df, pd.core.frame.DataFrame)

    # list to store colors for each person
    cols = []
    for l in df.index:
        if df.loc[l, "Covid19"] == True:  # Infected
            cols.append("red")
        elif df.loc[l, "Covid19"] == 666:  # Dead
            cols.append("black")
        elif df.loc[l, "Covid19"] == 115:  # Hospitalized
            cols.append("yellow")
        elif df.loc[l, "Covid19"] == 7:  # Cured
            cols.append("green")
        else:
            cols.append("blue")  # Healthy
    return cols


def get_covid_stat_plt_color(stats_df):
    """
    Samples colors for stats plots
    Keyword arguments:
    stats_df -- stats dataframe [Healthy,Covid-19(+),Hospitalized,Cured,Dead]
    """

    assert isinstance(stats_df, pd.core.frame.DataFrame)

    cols = []
    for i in stats_df.columns:
        if i == "Covid-19(+)":  # Infected
            cols.append("red")
        elif i == "Dead":  # Dead
            cols.append("black")
        elif i == "Hospitalized":  # Hospitalized
            cols.append("yellow")
        elif i == "Cured":  # Cured
            cols.append("green")
        else:
            cols.append("blue")  # Healthy
    return cols


def plot_day(df, fig, axs, stats_df, day, movers_list, show=False, savefig=False):
    """
    Plot the simulation results for the day
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid-19,Day]
    fig -- matplotlib figure (with 2 subplots)
    stats_df -- stats dataframe [Healthy,Covid-19(+),Hospitalized,Cured,Dead]
    day -- current day (int)
    movers_list -- list of people who are moving
    show -- show plot if True (default: False)
    savefig -- save fig to disk if True (default: False)
    """
    assert isinstance(df, pd.core.frame.DataFrame)
    assert isinstance(stats_df, pd.core.frame.DataFrame)
    assert isinstance(day, int)
    assert day < len(df)
    assert isinstance(movers_list, list)
    assert isinstance(show, bool)
    assert isinstance(savefig, bool)

    cols = get_covid_df_plt_color(df)

    # fig.clf()

    ld = ["Healthy", "Covid-19(+)", "Hospitalized", "Cured", "Death Toll"]
    axs[0].cla()
    axs[0].scatter(df["X"], df["Y"], s=4, c=cols)
    for i in movers_list:
        axs[0].scatter(df.loc[i, "X"], df.loc[i, "Y"], s=1, facecolors="none", edgecolors="black")
        axs[0].text(df.loc[i, "X"] + 0.02, df.loc[i, "Y"] + 0.02, str(i), fontsize=5)

    cols = get_covid_stat_plt_color(stats_df)
    day_string = str(day)
    title = "Day" + day_string

    axs[0].set_title(title, loc="left")
    axs[0].set_yticklabels([])
    axs[0].set_xticklabels([])
    axs[0].tick_params(
        which="both",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        right=False,  # ticks along the right edge are off
        left=False,  # ticks along the left edge are off
        labelbottom=False,
    )  # labels along the bottom edge are off

    axs[1].cla()
    axs[1].plot(stats_df.Healthy, label=ld[0], color=cols[0])
    axs[1].plot(stats_df["Covid-19(+)"], label=ld[1], color=cols[1])
    axs[1].plot(stats_df.Hospitalized, label=ld[2], color=cols[2])
    axs[1].plot(stats_df.Cured, label=ld[3], color=cols[3])
    axs[1].plot(stats_df.Dead, label=ld[4], color=cols[4])

    axs[1].legend(bbox_to_anchor=(0, 1), loc="upper left", borderaxespad=0.0)

    axs[2].cla()
    axs[2].plot(stats_df.Work, label="Economic Impact", color=cols[0])
    axs[2].plot([50] * day, "--", label="Economic danger threshold", color=cols[1])
    axs[2].legend(loc="upper left", borderaxespad=0.0)

    plt.ylim(top=100, bottom=0)

    plt.xlabel("Days")
    if show:
        plt.pause(0.1)

    if day < 10:
        day_string = "0" + day_string
    title = "output/Day" + day_string + ".png"
    if savefig:
        plt.savefig(title)


def run_simulation(
    N, x_limit, y_limit, dist_limit, SHOW_PLOT_FLAG=False, SAVE_PLOT_FLAG=False, simulation_id=0
):  ## SIMULATION PARAMETERS
    assert N is not None
    assert x_limit is not None
    assert y_limit is not None
    assert dist_limit is not None
    assert simulation_id is not None

    dist_limit = float(dist_limit)
    sc = SparkContext()
    sqlContext = SQLContext(sc)

    ## SIMULATION PARAMETERS
    MOTION_FACTOR = min(5, N * 0.1)
    day = 0

    SHOW_PLOT_FLAG = True
    SAVE_PLOT_FLAG = False

    status_type = {"Student": 0.1, "Working": 0.7, "Child": 0.1, "Old": 0.1}

    covid_df, stats_df, movers_list = initalize_simulation_dataframes(
        N, x_limit, y_limit, status_type, motion_factor=MOTION_FACTOR
    )
    print(f"covid_df: {covid_df}\n")
    print(f"stats_df: {stats_df}\n")
    print(f"movers_list: {movers_list}\n")

    covid_df = sqlContext.createDataFrame(covid_df)

    working_hours_today = initial_working_hours = get_working_hours(covid_df)

    ## Start the simulation by infecting a random person
    random_person = random.randrange(N)
    covid_df = infect(covid_df, day, random_person)
    fig, axs = plt.subplots(3)
    fig.suptitle("Covid-19 Epidemic Sample Model", fontsize=16)
    # plot_day(covid_df.toPandas(), fig, axs, stats_df, day, movers_list, show=SHOW_PLOT_FLAG, savefig=SAVE_PLOT_FLAG)

    ## Plot the static graph
    print("-" * 20)
    covid_df, stats_df = update_stats_for_day(sqlContext, covid_df, stats_df, day, initial_working_hours)
    # Now we have some data in stats_df, convert into spark df
    stats_df = sqlContext.createDataFrame(stats_df)

    covid_df = update_working_hours(covid_df)
    yesterday_patients = list(covid_df.toPandas()["Covid19"])
    covid_df = covid_df.withColumn("Covid19", covid_df["Covid19"].cast("int"))
    covid_df, stats_df, day, movers_list = simulate_next_day(covid_df, stats_df, day, movers_list, x_limit, y_limit)
    covid_df = interact(covid_df, day, yesterday_patients, dist_limit)

    ## Day 1
    # plot_day(covid_df.toPandas(), fig, axs, stats_df.toPandas(), day, movers_list, show=SHOW_PLOT_FLAG,
    #          savefig=SAVE_PLOT_FLAG)
    covid_df, stats_df = update_stats_for_day(sqlContext, covid_df, stats_df, day, initial_working_hours)

    count_sames = 0
    healthy = stats_df.select("Healthy").collect()[-1].Healthy

    while healthy > 0 and day < 100:
        if list(stats_df.toPandas().loc[day]) == list(stats_df.toPandas().loc[day - 1]):
            count_sames += 1
            if count_sames > 8:
                break
        else:
            count_sames = 0

        yesterday_patients = list(covid_df.toPandas()["Covid19"])
        covid_df, stats_df, day, movers_list = simulate_next_day(covid_df, stats_df, day, movers_list, x_limit, y_limit)
        covid_df = interact(covid_df, day, yesterday_patients, dist_limit)
        covid_df = update_working_hours(covid_df)
        working_hours = get_working_hours(covid_df)
        # plot_day(covid_df.toPandas(), fig, axs, stats_df.toPandas(), day, movers_list, show=SHOW_PLOT_FLAG,
        #          savefig=SAVE_PLOT_FLAG)
        covid_df, stats_df = update_stats_for_day(sqlContext, covid_df, stats_df, day, initial_working_hours)

        healthy = stats_df.select("Healthy").collect()[-1].Healthy
        print(31 * "-")
        print("Day:", day)
        print("----------------")
        print(f"Stats DF :")
        stats_df.show()
        print(f"Total Working Hours: {working_hours}")

        # stats_df.cache()
        # covid_df.cache()
        # sqlContext.clearCache()
        # sqlContext.clearCache()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments for the COVID-19 Simulation")
    parser.add_argument("-simID", action="store", dest="simID", type=str, help="Simulation ID", default="sim_id_random")
    parser.add_argument(
        "-N",
        action="store",
        dest="N",
        type=int,
        default=300,
        help="Population Size to simulate (Note: Large N can slow down computations)",
    )
    parser.add_argument(
        "-x_limit", action="store", dest="x_limit", type=int, default=30, help="X-axis limit of 2D canvas"
    )
    parser.add_argument(
        "-y_limit", action="store", dest="y_limit", type=int, default=30, help="Y-axis limit of 2D canvas"
    )
    parser.add_argument(
        "-dist_thres",
        action="store",
        dest="dist_limit",
        default=1.5,
        help="Distance threshold to infect another person",
    )
    parser.add_argument(
        "-show_plot", action="store_true", default="False", help="Shows plot, Keep it false on a server"
    )
    parser.add_argument("-save_plot", action="store_true", default="False", help="Saves plot on the disk")

    args = parser.parse_args()

    run_simulation(
        N=args.N, x_limit=args.x_limit, y_limit=args.y_limit, dist_limit=args.dist_limit, simulation_id=args.simID
    )
