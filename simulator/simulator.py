import random
import math

import pandas as pd
import matplotlib.pyplot as plt

from PIL import Image
import glob

from utils import *

## SIMULATION PARAMETERS
N = 300  # Population Size
MOTION_FACTOR = max(5, N * 0.1)
x_limit, y_limit = 30, 30
dist_limit = 1.5
day = 0

SHOW_PLOT_FLAG = True
SAVE_PLOT_FLAG = False

covid_df, stats_df, movers_list = initalize_simulation_dataframes(
    N, x_limit, y_limit, motion_factor=MOTION_FACTOR)
print(f"covid_df: {covid_df}\n")
print(f"stats_df: {stats_df}\n")
print(f"movers_list: {movers_list}\n")

## Start the simulation by infecting a random person
random_person = random.randrange(N)
covid_df.loc[random_person, "Day"]
covid_df = infect(covid_df, day, random_person)

print("-" * 20)
print(f"Random Person: {random_person}")
print(f"covid_df (After infecting a person): {covid_df}")
print(f"{covid_df.loc[random_person]}")

## Plot the static graph
print("-" * 20)
print("PLOTTING FIGURE")
fig, axs = plt.subplots(2)
fig.suptitle("Covid-19 Epidemic Sample Model", fontsize=16)
plot_day(
    covid_df,
    fig,
    axs,
    stats_df,
    day,
    movers_list,
    show=SHOW_PLOT_FLAG,
    savefig=SAVE_PLOT_FLAG,
)

## Plot the static graph
print("-" * 20)
covid_df, stats_df = update_stats_for_day(covid_df, stats_df, day)

yesterday_patients = list(covid_df["Covid-19"])
covid_df, stats_df, day, movers_list = simulate_next_day(
    covid_df, stats_df, day, movers_list, x_limit, y_limit)
covid_df = interact(covid_df, day, yesterday_patients, dist_limit)

## Day 1
plot_day(
    covid_df,
    fig,
    axs,
    stats_df,
    day,
    movers_list,
    show=SHOW_PLOT_FLAG,
    savefig=SAVE_PLOT_FLAG,
)
covid_df, stats_df = update_stats_for_day(covid_df, stats_df, day)

count_sames = 0
while stats_df.loc[day, "Healthy"] > 0 and day < 100:
    if list(stats_df.loc[day]) == list(stats_df.loc[day - 1]):
        count_sames += 1
        if count_sames > 5:
            break
    else:
        countsames = 0

    yesterday_patients = list(covid_df["Covid-19"])
    covid_df, stats_df, day, movers_list = simulate_next_day(
        covid_df, stats_df, day, movers_list, x_limit, y_limit)
    covif_df = interact(covid_df, day, yesterday_patients, dist_limit)
    plot_day(
        covid_df,
        fig,
        axs,
        stats_df,
        day,
        movers_list,
        show=SHOW_PLOT_FLAG,
        savefig=SAVE_PLOT_FLAG,
    )
    covid_df, stats_df = update_stats_for_day(covid_df, stats_df, day)

    print(31 * "-")
    print("Day:", day)
    print(8 * "- - ")
    print(stats_df.loc[day])

plt.show()
# Png_to_gif()
# Stat.to_excel('Stat.xlsx')
# Stat.plot(title='Statistical Data Vs. Days Passed')
# plt.savefig('Stat')
