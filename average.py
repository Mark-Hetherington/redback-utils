import matplotlib.pyplot as plt

# Produces an "average" day from all the data.
from utils import load_pandas, load_all_data


data = load_all_data(limit=60)
data = data.resample('T').mean()

by_time = data.groupby(data.index.time).mean()
print("total samples:%d, grouped samples %d" % (len(data.index),len(by_time.index)))

#df.index = df.index.time
by_time['ACLoad.P'].plot(label="ACLOAD", zorder=1)
by_time['PV.P'].plot(label="PV", zorder=1)
#by_time['Battery.P'].plot(label="Battery", zorder=1)

# multiple line plot
# plt.plot('Date', 'ACLoad.P', data=df)
# plt.plot('Date', 'PV.P', data=df)
# plt.plot('Date', 'Grid.P', data=df)
# plt.plot('Date', 'Battery.P', data=df)
plt.legend()
plt.show()

# if not os.path.exists(output_directory):
#     os.mkdir(output_directory)
#
# by_time.to_json(os.path.join(output_directory, "average.json"))
