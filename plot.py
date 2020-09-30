# libraries
import matplotlib.pyplot as plt

from constants import data_directory
from utils import load_json
import numpy as np
import pandas as pd
from datetime import date, timedelta
import os

# Data
# df = pd.DataFrame({'x': range(1, 11), 'y1': np.random.randn(10), 'y2': np.random.randn(10) + range(1, 11),
#                    'y3': np.random.randn(10) + range(11, 21)})

df = load_json('output/average.json')
# df = load_pandas('data/2019-09-07.json')
df.index = df.index.time
df['ACLoad.P'].plot(label="ACLOAD", zorder=1)
df['PV.P'].plot(label="PV", zorder=1)
df['Battery.P'].plot(label="Battery", zorder=1)

# multiple line plot
# plt.plot('Date', 'ACLoad.P', data=df)
# plt.plot('Date', 'PV.P', data=df)
# plt.plot('Date', 'Grid.P', data=df)
# plt.plot('Date', 'Battery.P', data=df)
plt.legend()
plt.show()
