import random
import math

import pandas as pd
import matplotlib.pyplot as plt


def point(x_limit, y_limit):
    """
    Generate a random 2D point

    Keyword arguments:
    x_limit -- max range on X-axis
    y_limit -- max range on Y-axis
    """

    assert isinstance(x_limit, int)
    assert isinstance(y_limit, int)
    
    x = random.uniform(0,x_limit)
    y = random.uniform(0,y_limit)
    return x, y


def initalize_simulation_dataframes(N, x_limit, y_limit):
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
        covid_df.loc[i,'X'], covid_df.loc[i,'Y'] = point(x_limit, y_limit)
        covid_df.loc[i,'Covid-19'] = False
    
    sample_size = math.floor(N/100)
    movers_list = covid_df.sample(n = sample_size).index.values.tolist()
    
    # Dataframe to keep track of daily statistics
    stats_df = pd.DataFrame(columns='Healthy,Covid-19(+),Hospitalized,Cured,Dead'.split(','))
    return covid_df , stats_df, movers_list


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
        return

    ## If the person is not already infected, infect him/her and record the day of infection
    if df.loc[person,'Covid-19']==False:
        df.loc[person,'Covid-19'], df.loc[person,'Day'] = True, day

    return df


def get_covid_df_plt_color(df):
    """
    Samples colors according to the covid-state of the persn
    Keyword arguments:
    df -- covid dataframe [X,Y,Covid-19,Day]
    """

    assert isinstance(df, pd.core.frame.DataFrame)

    # list to store colors for each person
    cols=[]
    for l in df.index:
        if df.loc[l,'Covid-19'] == True: #Infected
            cols.append('red')
        elif df.loc[l,'Covid-19'] == 666: #Dead
            cols.append('black')
        elif df.loc[l,'Covid-19'] == 115: #Hospitalized
            cols.append('yellow')
        elif df.loc[l,'Covid-19'] == 7: #Cured
            cols.append('green')
        else:
            cols.append('blue') #Healthy
    return cols


def get_covid_stat_plt_color(stats_df):
    """
    Samples colors for stats plots
    Keyword arguments:
    stats_df -- stats dataframe [Healthy,Covid-19(+),Hospitalized,Cured,Dead]
    """

    assert isinstance(stats_df, pd.core.frame.DataFrame)

    cols=[]
    for i in stats_df.columns:
        if i=='Covid-19(+)': #Infected
            cols.append('red')
        elif i=='Dead': #Dead
            cols.append('black')
        elif i=='Hospitalized': #Hospitalized
            cols.append('yellow')
        elif i=='Cured': #Cured
            cols.append('green')
        else:
            cols.append('blue') #Healthy
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
    
    ld = ['Healthy','Covid-19(+)','Hospitalized','Cured','Death Toll']
    axs[0].cla()
    axs[0].scatter(df['X'],df['Y'],s=4,c=cols)
    for i in movers_list:
        axs[0].scatter(df.loc[i,'X'],df.loc[i,'Y'],s=1,facecolors='none', edgecolors='black')
        axs[0].text(df.loc[i,'X']+0.02, df.loc[i,'Y']+0.02, str(i), fontsize=5)

    cols = get_covid_stat_plt_color(stats_df)
    day_string = str(day)
    title = 'Day' + day_string

    axs[0].set_title(title,loc='left')
    axs[0].set_yticklabels([])
    axs[0].set_xticklabels([])
    axs[0].tick_params(
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        right=False,      # ticks along the right edge are off
        left=False,         # ticks along the left edge are off
        labelbottom=False) # labels along the bottom edge are off

    axs[1].cla()
    axs[1].plot(stats_df.Healthy,label=ld[0],color=cols[0])
    axs[1].plot(stats_df['Covid-19(+)'],label=ld[1],color=cols[1])
    axs[1].plot(stats_df.Hospitalized,label=ld[2],color=cols[2])
    axs[1].plot(stats_df.Cured,label=ld[3],color=cols[3])
    axs[1].plot(stats_df.Dead,label=ld[4],color=cols[4])


    axs[1].legend(bbox_to_anchor=(0, 1), loc='upper left', borderaxespad=0.)
    plt.xlabel('Days')
    if show:
        plt.show()
    if day < 10 : day_string = '0' + day_string
    title = 'Day' + day_string + '.png'
    if savefig:
        plt.savefig(title)