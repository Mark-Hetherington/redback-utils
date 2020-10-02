import matplotlib.pyplot as plt
import os

# Produces an "average" day from all the data.
from constants import output_directory
from utils import load_json, load_all_json_data, resample_dataframe, load_all_data
import pandas


data = load_all_data()
data = resample_dataframe(data, 'T')

by_time = data.groupby(data.index.time).mean()
print("total samples:%d, grouped samples %d" % (len(data.index), len(by_time.index)))

if not os.path.exists(output_directory):
    os.mkdir(output_directory)

by_time.to_json(os.path.join(output_directory, "average.json"))

#df.index = df.index.time
by_time['ACLoad.P'].plot(label="ACLOAD", zorder=1)
by_time['PV.P'].plot(label="PV", zorder=1)
by_time['Grid.P'].plot(label="Grid", zorder=1)
by_time['Battery.P'].plot(label="Battery", zorder=1)

# multiple line plot
# plt.plot('Date', 'ACLoad.P', data=df)
# plt.plot('Date', 'PV.P', data=df)
# plt.plot('Date', 'Grid.P', data=df)
# plt.plot('Date', 'Battery.P', data=df)
plt.legend()
plt.show()


