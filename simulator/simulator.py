import random
import math

import pandas as pd
import matplotlib.pyplot as plt

import argparse

# clear data in elastic
from elastic import Elastic  # needs to be changed to from simulator.elastic import Elastic when run from project root dir
Elastic.clear_data('covid_df')
Elastic.clear_data('stats_df')
Elastic.clear_data('eco_df')


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


def initalize_simulation_dataframes(N, x_limit, y_limit, motion_factor=5):
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
    covid_df = pd.DataFrame(columns='X,Y,Covid-19,Day'.split(','))

    for i in range(N):
        covid_df.loc[i, 'X'], covid_df.loc[i, 'Y'] = point(x_limit, y_limit)
        covid_df.loc[i, 'Covid-19'] = 0

    sample_size = math.floor(motion_factor)
    movers_list = covid_df.sample(n=sample_size).index.values.tolist()

    # Dataframe to keep track of daily statistics
    stats_df = pd.DataFrame(
        columns=
        'simulationID,Day,Healthy,Covid-19(+),Hospitalized,Cured,Dead,Work'.
        split(','))
    return covid_df, stats_df, movers_list


def assign_working_status(covid_df, status_type):
    """
    Add working status for every person
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid-19,Day]
    """

    print(covid_df.head())

    N = len(covid_df)
    status_list = []
    working_hours = []
    for status, prob in status_type.items():
        status_list.extend([status] * int(prob * N))
        if status == 'Working':
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

    covid_df['status'] = status_list
    covid_df['working_hours'] = working_hours
    return covid_df


def get_working_hours(covid_df):
    """
    Add working status for every person
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid-19,Day, status, working_hours]
    """
    return covid_df['working_hours'].sum()


def update_working_hours(covid_df):
    """
    Add working status for every person
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid-19,Day,status, working_hours]
    """
    print(covid_df.columns)
    mask = (covid_df['Covid-19'] == 1)
    covid_df['working_hours'][mask] = 0
    mask1 = covid_df['Covid-19'] == 7
    mask2 = covid_df['status'] == 'Working'
    covid_df['working_hours'][mask1 & mask2] = 40

    return covid_df


def infect(df, day, person):
    """
    Infect a random person from the population
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid-19,Day]
    day -- current day
    person -- person_id to infect
    """
    assert isinstance(df, pd.core.frame.DataFrame)
    assert isinstance(day, int)
    assert isinstance(person, int)
    assert person < len(df)

    if random.random() > 0.25 and day > 3:
        return df

    ## If the person is not already infected, infect him/her and record the day of infection
    if df.loc[person, 'Covid-19'] == 0:
        df.loc[person, 'Covid-19'], df.loc[person, 'Day'] = 1, day

    return df


def update_stats_for_day(covid_df, stats_df, day, initial_working_hours):
    """
    Update the statistics for the given day
    Keyword arguments:
    covid_df -- covid dataframe [X,Y,Covid-19,Day]
    stats_df -- stats dataframe [Healthy,Covid-19(+),Hospitalized,Cured,Dead]
    day -- current day
    """

    assert isinstance(covid_df, pd.core.frame.DataFrame)
    assert isinstance(stats_df, pd.core.frame.DataFrame)
    assert isinstance(day, int)

    covid_list = list(covid_df['Covid-19'])

    stats_df.loc[day, 'Day'] = day
    stats_df.loc[day, 'Healthy'] = covid_list.count(0)
    stats_df.loc[day, 'Covid-19(+)'] = covid_list.count(1)
    stats_df.loc[day, 'Hospitalized'] = covid_list.count(115)
    stats_df.loc[day, 'Cured'] = covid_list.count(7)
    stats_df.loc[day, 'Dead'] = covid_list.count(666)

    stats_df.loc[day, 'Work'] = (get_working_hours(covid_df) /
                                 initial_working_hours) * 100

    return covid_df, stats_df


def kill(df, kill_prob=0.005):
    """
    Kill a fraction of population given by kill_prob
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid-19,Day]
    kill_prob -- kill people by kill_prob (default: 0.005)
    """

    assert isinstance(df, pd.core.frame.DataFrame)
    assert isinstance(kill_prob, float)
    assert kill_prob >= 0
    assert kill_prob <= 1

    samplesize = math.floor(
        len(df[df['Covid-19'] == 1]) * kill_prob +
        len(df[df['Covid-19'] == 115]) * kill_prob)
    if samplesize > len(df[df['Covid-19'] == 1]): return
    df.loc[df[df['Covid-19'] == 1].sample(n=samplesize).index.values.tolist(),
           'Covid-19'] = 666
    return df


def hospitalize(df, hosp_prob=0.03):
    """
    Hospitalize a fraction of population given by hosp_prob
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid-19,Day]
    hosp_prob -- Hospitalize people by hosp_prob (default: 0.03)
    """

    assert isinstance(df, pd.core.frame.DataFrame)
    assert isinstance(hosp_prob, float)
    assert hosp_prob >= 0
    assert hosp_prob <= 1

    samplesize = math.floor(len(df[df['Covid-19'] == 1]) * hosp_prob)
    if samplesize > len(df[df['Covid-19'] == 1]): return
    df.loc[df[df['Covid-19'] == 1].sample(n=samplesize).index.values.tolist(),
           'Covid-19'] = 115
    return df


def cure(df, day):
    """
    Cure people after their quarantine is finished
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid-19,Day]
    day -- current day
    """

    assert isinstance(df, pd.core.frame.DataFrame)
    assert isinstance(day, int)

    df.loc[(df['Day'] < day - 10) & (df['Covid-19'] == 1), 'Covid-19'] = 7
    df.loc[(df['Day'] < day - 21) & (df['Covid-19'] == 115), 'Covid-19'] = 7
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
    for i in movers_list:
        if (df.loc[i, 'Covid-19'] == 115) or (df.loc[i, 'Covid-19'] == 666):
            movers_list.remove(i)

        df.loc[i, 'X'], df.loc[i, 'Y'] = (
            df.loc[i, 'X'] + random.uniform(1, x_limit / 3)) % x_limit, (
                df.loc[i, 'Y'] + random.uniform(1, y_limit / 3)) % y_limit

    return df, movers_list


def simulate_next_day(covid_df, stats_df, day, movers_list, x_limit, y_limit):
    """
    Simulates the next day given current day data
    Keyword arguments:
    covid_df -- covid dataframe [X,Y,Covid-19,Day]
    stats_df -- stats dataframe [Healthy,Covid-19(+),Hospitalized,Cured,Dead]
    day -- current day
    """

    assert isinstance(covid_df, pd.core.frame.DataFrame)
    assert isinstance(stats_df, pd.core.frame.DataFrame)
    assert isinstance(day, int)

    day += 1
    covid_df = kill(covid_df)
    covid_df = hospitalize(covid_df)
    covid_df = cure(covid_df, day)
    covid_df, movers_list = random_walk(covid_df, movers_list, x_limit,
                                        y_limit)

    return covid_df, stats_df, day, movers_list


def check(covid_df, i, j, yesterday_patients, dist_limit):
    """
    Checks if two people are close enough to infect eachother
    Keyword arguments:
    covid_df -- covid dataframe [X,Y,Covid-19,Day]
    i -- first person
    j -- second person
    yesterday_patients -- List of covud(+) people until yesterday
    dist_limit -- csafe social distance limit
    """

    assert isinstance(covid_df, pd.core.frame.DataFrame), type(covid_df)
    assert isinstance(i, int)
    assert isinstance(j, int)
    assert isinstance(yesterday_patients, list)
    assert isinstance(dist_limit, float)

    dist = math.sqrt((covid_df.loc[i, 'X'] - covid_df.loc[j, 'X'])**2 +
                     (covid_df.loc[i, 'Y'] - covid_df.loc[j, 'Y'])**2)
    flag = ((yesterday_patients[i] == 1) ^
            (yesterday_patients[j] == 1)) and dist < dist_limit
    return flag


def interact(covid_df, day, yesterday_patients, dist_limit):
    """
    Infect people who interact with oneanother
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid-19,Day]
    day -- current day
    """
    assert isinstance(covid_df, pd.core.frame.DataFrame)
    assert isinstance(day, int)

    for i in range(len(covid_df)):
        for j in range(i):
            if check(covid_df, i, j, yesterday_patients, dist_limit):
                if (covid_df.loc[i, 'Covid-19'] == 0):
                    covid_df = infect(covid_df, day, i)
                else:
                    covid_df = infect(covid_df, day, j)
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
        if df.loc[l, 'Covid-19'] == 1:  # Infected
            cols.append('red')
        elif df.loc[l, 'Covid-19'] == 666:  # Dead
            cols.append('black')
        elif df.loc[l, 'Covid-19'] == 115:  # Hospitalized
            cols.append('yellow')
        elif df.loc[l, 'Covid-19'] == 7:  # Cured
            cols.append('green')
        else:
            cols.append('blue')  # Healthy
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
        if i == 'Covid-19(+)':  # Infected
            cols.append('red')
        elif i == 'Dead':  # Dead
            cols.append('black')
        elif i == 'Hospitalized':  # Hospitalized
            cols.append('yellow')
        elif i == 'Cured':  # Cured
            cols.append('green')
        elif i == 'Healthy':
            cols.append('blue')  # Healthy
    return cols


def plot_day(df,
             fig,
             axs,
             stats_df,
             day,
             movers_list,
             show=False,
             savefig=False):
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

    ld = ['Healthy', 'Covid-19(+)', 'Hospitalized', 'Cured', 'Death Toll']
    axs[0].cla()
    axs[0].scatter(df['X'], df['Y'], s=4, c=cols)
    for i in movers_list:
        axs[0].scatter(df.loc[i, 'X'],
                       df.loc[i, 'Y'],
                       s=1,
                       facecolors='none',
                       edgecolors='black')
        axs[0].text(df.loc[i, 'X'] + 0.02,
                    df.loc[i, 'Y'] + 0.02,
                    str(i),
                    fontsize=5)

    cols = get_covid_stat_plt_color(stats_df)
    day_string = str(day)
    title = 'Day' + day_string

    axs[0].set_title(title, loc='left')
    axs[0].set_yticklabels([])
    axs[0].set_xticklabels([])
    axs[0].tick_params(
        which='both',  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        right=False,  # ticks along the right edge are off
        left=False,  # ticks along the left edge are off
        labelbottom=False)  # labels along the bottom edge are off

    axs[1].cla()
    axs[1].plot(stats_df.Healthy, label=ld[0], color=cols[0])
    axs[1].plot(stats_df['Covid-19(+)'], label=ld[1], color=cols[1])
    axs[1].plot(stats_df.Hospitalized, label=ld[2], color=cols[2])
    axs[1].plot(stats_df.Cured, label=ld[3], color=cols[3])
    axs[1].plot(stats_df.Dead, label=ld[4], color=cols[4])

    axs[1].legend(bbox_to_anchor=(0, 1), loc='upper left', borderaxespad=0.)

    axs[2].cla()
    axs[2].plot(stats_df.Work, label='Economic Impact', color=cols[0])
    axs[2].plot([50] * day,
                '--',
                label='Economic danger threshold',
                color=cols[1])
    axs[2].legend(loc='upper left', borderaxespad=0.)

    plt.ylim(top=100, bottom=0)

    plt.xlabel('Days')
    if show:
        plt.pause(0.05)

    if day < 10: day_string = '0' + day_string
    title = 'output/Day' + day_string + '.png'
    if savefig:
        plt.savefig(title)


def run_simulation(N,
                   x_limit,
                   y_limit,
                   dist_limit,
                   motion_factor=0.1,
                   SHOW_PLOT_FLAG=False,
                   SAVE_PLOT_FLAG=False,
                   simulation_id="sim_id_random"):  ## SIMULATION PARAMETERS
    assert N is not None
    assert x_limit is not None
    assert y_limit is not None
    assert dist_limit is not None
    assert simulation_id is not None

    dist_limit = float(dist_limit)

    MOTION_FACTOR = float(motion_factor) * N
    day = 0

    SHOW_PLOT_FLAG = bool(SHOW_PLOT_FLAG)
    SAVE_PLOT_FLAG = bool(SAVE_PLOT_FLAG)

    print(f"Running Simulation with ID: {simulation_id}")

    covid_df, stats_df, movers_list = initalize_simulation_dataframes(
        N, x_limit, y_limit, motion_factor=MOTION_FACTOR)
    print(f"covid_df: {covid_df}\n")
    print(f"stats_df: {stats_df}\n")
    print(f"movers_list: {movers_list}\n")

    status_type = {'Student': 0.1, 'Working': 0.7, 'Child': 0.1, 'Old': 0.1}

    covid_df = assign_working_status(covid_df, status_type)
    initial_working_hours = get_working_hours(covid_df)

    ## Start the simulation by infecting a random person
    random_person = random.randrange(N)
    covid_df = infect(covid_df, day, random_person)

    print("-" * 20)
    print(f"Random Person: {random_person}")
    print(f"covid_df (After infecting a person): {covid_df}")
    print(f"{covid_df.loc[random_person]}")

    covid_df = update_working_hours(covid_df)

    ## Plot the static graph
    print("-" * 20)
    print("PLOTTING FIGURE")
    fig, axs = plt.subplots(3)
    fig.suptitle('Covid-19 Epidemic Sample Model', fontsize=16)
    plot_day(covid_df,
             fig,
             axs,
             stats_df,
             day,
             movers_list,
             show=SHOW_PLOT_FLAG,
             savefig=SAVE_PLOT_FLAG)

    ## Plot the static graph
    print("-" * 20)
    covid_df, stats_df = update_stats_for_day(covid_df, stats_df, day,
                                              initial_working_hours)
    covid_df = update_working_hours(covid_df)

    yesterday_patients = list(covid_df['Covid-19'])
    covid_df, stats_df, day, movers_list = simulate_next_day(
        covid_df, stats_df, day, movers_list, x_limit, y_limit)
    covid_df = interact(covid_df, day, yesterday_patients, dist_limit)

    ## Day 1
    Elastic.load_sim_data(covid_df, stats_df)
    plot_day(covid_df,
             fig,
             axs,
             stats_df,
             day,
             movers_list,
             show=SHOW_PLOT_FLAG,
             savefig=SAVE_PLOT_FLAG)
    covid_df, stats_df = update_stats_for_day(covid_df, stats_df, day,
                                              initial_working_hours)

    count_sames = 0
    stats_df['simulationID'] = simulation_id
    while stats_df.loc[day, 'Healthy'] > 0 and day < 100:
        if (list(stats_df.loc[day]) == list(stats_df.loc[day - 1])):
            count_sames += 1
            if count_sames > 8:
                break
        else:
            count_sames = 0

        yesterday_patients = list(covid_df['Covid-19'])
        covid_df, stats_df, day, movers_list = simulate_next_day(
            covid_df, stats_df, day, movers_list, x_limit, y_limit)
        covid_df = interact(covid_df, day, yesterday_patients, dist_limit)
        covid_df = update_working_hours(covid_df)
        working_hours = get_working_hours(covid_df)
        Elastic.load_sim_data(covid_df, stats_df)
        plot_day(covid_df,
                 fig,
                 axs,
                 stats_df,
                 day,
                 movers_list,
                 show=SHOW_PLOT_FLAG,
                 savefig=SAVE_PLOT_FLAG)
        covid_df, stats_df = update_stats_for_day(covid_df, stats_df, day,
                                                  initial_working_hours)
        stats_df['simulationID'] = simulation_id

        print(31 * '-')
        print('Day:', day)
        print(8 * '- - ')
        print("----------------")
        # print(f"Covid DF: {covid_df}")
        print(f"Stats DF : {stats_df}")
        print(f"Total Working Hours: {working_hours}")

    plt.show()
    # plt.savefig('Stat')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Arguments for the COVID-19 Simulation')
    parser.add_argument('-simID',
                        action="store",
                        dest="simID",
                        help='Simulation ID',
                        default="sim_id_random")
    parser.add_argument(
        '-N',
        action="store",
        dest="N",
        type=int,
        default=300,
        help=
        'Population Size to simulate (Note: Large N can slow down computations)'
    )
    parser.add_argument('-x_limit',
                        action="store",
                        dest="x_limit",
                        type=int,
                        default=30,
                        help='X-axis limit of 2D canvas')
    parser.add_argument('-y_limit',
                        action="store",
                        dest="y_limit",
                        type=int,
                        default=30,
                        help='Y-axis limit of 2D canvas')
    parser.add_argument('-dist_thres',
                        action="store",
                        dest="dist_limit",
                        default=1.5,
                        help='Distance threshold to infect another person')
    parser.add_argument(
        '-mov_rate',
        action="store",
        dest="mov_rate",
        default=0.15,
        help='Rate of infection spread, correlated with the motion')
    parser.add_argument('-show_plot',
                        action="store_true",
                        default="False",
                        dest='show_plot',
                        help='Shows plot, Keep it false on a server')
    parser.add_argument('-save_plot',
                        action="store_true",
                        default="False",
                        dest='save_plot',
                        help='Saves plot on the disk')

    args = parser.parse_args()

    run_simulation(N=args.N,
                   x_limit=args.x_limit,
                   y_limit=args.y_limit,
                   dist_limit=args.dist_limit,
                   motion_factor=args.mov_rate,
                   simulation_id=args.simID,
                   SHOW_PLOT_FLAG=args.show_plot,
                   SAVE_PLOT_FLAG=args.save_plot)
