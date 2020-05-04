import random
import math

import pandas as pd
import matplotlib.pyplot as plt

from PIL import Image
import glob

from utils import *


## SIMULATION PARAMETERS
N = 1000    # Population Size
x_limit,y_limit = 30, 30
dist_limit = 1.5
day = 0


covid_df, stats_df, movers_list = initalize_simulation_dataframes(N, x_limit, y_limit)
print(f"covid_df: {covid_df}\n")
print(f"stats_df: {stats_df}\n")
print(f"movers_list: {movers_list}\n")


## Start the simulation by infecting a random person
random_person = random.randrange(N)
covid_df.loc[random_person, 'Day']
covid_df = infect(covid_df, day, random_person)

print("-"*20)
print(f"Random Person: {random_person}")
print(f"covid_df (After infecting a person): {covid_df}")
print(f"{covid_df.loc[random_person]}")


## Plot the static graph
print("-"*20)
print("PLOTTING FIGURE")
fig, axs = plt.subplots(2)
fig.suptitle('Covid-19 Epidemic Sample Model', fontsize=16)
plot_day(covid_df, fig, axs, stats_df, day, movers_list, show=True)