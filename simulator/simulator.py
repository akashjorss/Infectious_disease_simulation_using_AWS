import random
import math

import pandas as pd
import matplotlib.pyplot as plt

from PIL import Image
import glob


def point(x_limit, y_limit):
    x = random.uniform(0,x_limit)
    y = random.uniform(0,y_limit)
    return x,y


def generate(N, x_limit, y_limit):
    df = pd.DataFrame(columns='X,Y,Covid-19,Day'.split(','))
    
    for i in range(N):
        df.loc[i,'X'], df.loc[i,'Y'] = point(x_limit, y_limit)
        df.loc[i,'Covid-19'] = False
    
    sample_size = math.floor(N/100)
    movers_list = df.sample(n = sample_size).index.values.tolist()
    
    stat_of_day = pd.DataFrame(columns='Healthy,Covid-19(+),Hospitalized,Cured,Dead'.split(','))
    return df , stat_of_day, movers_list

def infect(df, day, person):
    if random.random() > 0.25 and day > 3: 
        return

    ## If the person is not already infected, infect him/her and record the day of infection
    if df.loc[person,'Covid-19']==False:
        df.loc[person,'Covid-19'], df.loc[person,'Day'] = True, day

    return df


def get_covid_df_plt_color(df):
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


def get_covid_stat_plt_color(stat_df):
    cols=[]
    for i in stat_df.columns:
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


def plot(df, fig, stat_of_day, day, movers_list, show=False, save_fig=False):
    cols = get_covid_df_plt_color(df)
    
    ld = ['Healthy','Covid-19(+)','Hospitalized','Cured','Death Toll']
    axs[0].cla()
    axs[0].scatter(df['X'],df['Y'],s=4,c=cols)
    for i in movers_list:
        axs[0].scatter(df.loc[i,'X'],df.loc[i,'Y'],s=1,facecolors='none', edgecolors='black')
        axs[0].text(df.loc[i,'X']+0.02, df.loc[i,'Y']+0.02, str(i), fontsize=5)

    cols = get_covid_stat_plt_color(stat_of_day)
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
    axs[1].plot(stat_of_day.Healthy,label=ld[0],color=cols[0])
    axs[1].plot(stat_of_day['Covid-19(+)'],label=ld[1],color=cols[1])
    axs[1].plot(stat_of_day.Hospitalized,label=ld[2],color=cols[2])
    axs[1].plot(stat_of_day.Cured,label=ld[3],color=cols[3])
    axs[1].plot(stat_of_day.Dead,label=ld[4],color=cols[4])


    axs[1].legend(bbox_to_anchor=(0, 1), loc='upper left', borderaxespad=0.)
    plt.xlabel('Days')
    if show:
        plt.show()
    if day < 10 : day_string = '0' + day_string
    title = 'Day' + day_string + '.png'
    if savefig:
        plt.savefig(title)




# LOG_FILE = 'logs/logs.txt'
## SIMULATION PARAMETERS
N = 1000    # Population Size
x_limit,y_limit = 30, 30
dist_limit = 1.5
day = 0

# write_log(31*'-')
# write_log("Here's the Input Data:")
# write_log(8*'- - ') 
# write_log('Numper of Sample:',n)
# write_log('X & Y limites: ',xlimit,', ',ylimit)
# write_log('Distance required for Contamination:', Distlimit)

df, stat_of_day, movers_list = generate(N,x_limit,y_limit)
print(f"df: {df}\n")
print(f"stat_of_day: {stat_of_day}\n")
print(f"movers_list: {movers_list}\n")


## Start the simulation by infecting a random person
random_person = random.randrange(N)
df.loc[random_person, 'Day']
df = infect(df, day, random_person)

print("-"*20)
print(f"Random Person: {random_person}")
print(f"df (After infecting a person): {df}")
print(f"{df.loc[random_person]}")


## Plot the static graph
print("-"*20)
print("PLOTTING FIGURE")
fig, axs = plt.subplots(2)
fig.suptitle('Covid-19 Epidemic Sample Model', fontsize=16)
plot(df, fig, stat_of_day, day, movers_list, show=False)


