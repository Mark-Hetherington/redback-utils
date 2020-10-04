# libraries
import matplotlib.pyplot as plt
import sys, getopt

from constants import data_directory
from utils import load_file, resample_dataframe, dataset_stats, load_all_data
import numpy as np
import pandas as pd
from datetime import date, timedelta
import os

# Data
# df = pd.DataFrame({'x': range(1, 11), 'y1': np.random.randn(10), 'y2': np.random.randn(10) + range(1, 11),
#                    'y3': np.random.randn(10) + range(11, 21)})

#df = load_file('output/average.json')

command_text = """
{0} -f <file> [-d <date>]
e.g. {0} -f 'output/simulation-Full upgrade.h5' -f '2020-01-01'
    -f, --file      Specify file
    -d, --date      Specify date
"""


try:
    opts, args = getopt.getopt(sys.argv[1:], "f:d:", ["file=", "date="])
except getopt.GetoptError as err:
    print(err)
    print(command_text)
    sys.exit(2)

datafile = None
date = None
for opt, arg in opts:
    if opt == '-h':
        print(command_text)
        sys.exit()
    elif opt in ("-f", "--file"):
        datafile = arg
    elif opt in ("-d", "--date"):
        date = arg

df = load_file(datafile) if datafile else load_all_data()
if hasattr(df.index, 'floor') and date:
    df = df[df.index.floor('D') == date]

dataset_stats(df)

if 'simulation.Grid.P' in df:
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
