# libraries
import matplotlib.pyplot as plt

from constants import data_directory
from utils import load_file, resample_dataframe, simulation_stats
import numpy as np
import pandas as pd
from datetime import date, timedelta
import os

# Data
# df = pd.DataFrame({'x': range(1, 11), 'y1': np.random.randn(10), 'y2': np.random.randn(10) + range(1, 11),
#                    'y3': np.random.randn(10) + range(11, 21)})

#df = load_file('output/average.json')
df = load_file('output/simulation-mean-day-Full upgrade.h5')
if 'simulation.Grid.P' in df:
    simulation_stats(df)
    df["ACLoad.P"].plot(label="Load")
    df["simulation.PV.P"].plot(label="PV")
    # data["PV.P"].plot()
    # data['Grid.P'].plot()
    # data['simulation.Battery.P'].plot(label="Battery")
    df['simulation.Battery.SoC'].plot(label="SoC", secondary_y=True)
    df['simulation.Grid.P'].plot(label="Grid")
    ax = df['simulation.Spill.P'].plot(label="Spill")
    plt.legend()
    ax.legend(loc="upper left")
    plt.show()
else:
    #df.index = df.index.time
    df = resample_dataframe(df, 'T')
    df.groupby(df.index.time).mean()
    df['ACLoad.P'].plot(label="ACLOAD", zorder=1)
    df['PV.P'].plot(label="PV", zorder=1)
    df['Battery.P'].plot(label="Battery", zorder=1)
    plt.legend()
    plt.show()
