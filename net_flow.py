import os

import pandas

from constants import data_directory
from utils import load_all_data

data = load_all_data()

# Trim unwanted columns
for column in data:
    if column not in ['ACLoad.P', 'PV.P']:
        del data[column]

# calculate load/solar ratio
# data['load_solar_ratio'] = data['ACLoad.P'] / data['PV.P']
# print(data)

# find daily sample counts
counts = data.resample('D').count()
# print("counts:", counts)

# filter incomplete days
data = data.loc[data.index.floor('D').isin(counts[counts['PV.P'] > 1000].index), :]

# print("filtered:", data)
# Convert to Wh - average for each minute, so we need to divide by 60
data = data.resample('T').mean()
data['ACLoad.P'] = data['ACLoad.P'] / 60
data['PV.P'] = data['PV.P'] / 60
# Whenever there is less than 100W solar, we assume it needs to come from the battery (overnight).
data['overnight_battery'] = data[['ACLoad.P', 'PV.P']].sum(axis=1).where(data['PV.P'] < 100 / 60, 0)
# sum to daily totals of Wh
data = data.resample('D').sum()
# print(data)

# filter days without any (solar) data. These are probably glitched?
data = data[data['PV.P'] != 0]
# print(data)

# calculate daily Wh/Wp
data['wh_per_wp'] = data['PV.P'] / 5000  # We have 5000 W of solar.
# print(data)

# With that we can produce a daily PV sizing ratio - peak watts per Wh of load.
# This tells us how many peak watts of solar we would need to generate the same power used that day.
data['load_solar_ratio'] = data['ACLoad.P'] / data['wh_per_wp']
#
# print(data)
# print(data.nlargest(10,'load_solar_ratio'))
# print(data.nsmallest(10,'load_solar_ratio'))

# the largest solar ratio is the upper bound of solar we can use.
max_solar = data.nlargest(1, 'load_solar_ratio')['load_solar_ratio'][0]
print("Max solar", max_solar)

# The smallest is the easiest day to power with solar
min_solar = data.nsmallest(1, 'load_solar_ratio')['load_solar_ratio'][0]
print("Min solar:", min_solar)

# the overnight battery is the upper bound of battery needed in a single day (consecutive days might add up more).
max_battery = data.nlargest(1, 'overnight_battery')['overnight_battery'][0]
print("Max overnight battery", max_battery)

# The smallest is the easiest day to power with solar
min_battery = data.nsmallest(1, 'overnight_battery')['overnight_battery'][0]
print("Min overnight battery:", min_battery)
solar_sizings = range(int(min_solar), int(max_solar), 5000)
battery_sizings = range(int(min_battery), int(max_battery), 5000)


def calculate_self_sufficiency(solar_size, battery_size):
    battery_charge_level = battery_size
    for index, row in data.iterrows():
        solar_generation = row['wh_per_wp'] * solar_size
        excess_solar = solar_generation - row['ACLoad.P']
        battery_charge = excess_solar
        battery_charge = min(battery_charge, battery_size - battery_charge_level)  # can't charge beyond full
        battery_charge = max(battery_charge, -battery_charge_level)  # can't discharge beyond empty
        battery_charge_level = battery_charge_level + battery_charge
        # negative numbers would be exports, but they don't contribute to self sufficiency.
        imports = max(-excess_solar - battery_charge, 0)

        data.at[index, 'battery_usage'] = battery_charge
        data.at[index, 'battery_charge_level'] = battery_charge_level
        data.at[index, 'import'] = imports

    total_usage = data['ACLoad.P'].sum()
    grid_usage = data['import'].sum()
    solar_usage = total_usage - grid_usage
    return solar_usage / total_usage


summary = pandas.DataFrame(0.0, index=solar_sizings, columns=battery_sizings)
for solar_size in solar_sizings:
    print(solar_size, "/", max_solar)
    for battery_size in battery_sizings:
        summary.at[solar_size, battery_size] = calculate_self_sufficiency(solar_size, battery_size)

data.to_hdf(os.path.join(data_directory, "self_sufficiency.h5"), 'table')
print(summary)
import matplotlib.pyplot as plt
from matplotlib import ticker, colors, cm
import numpy as np

X = summary.columns.values
Y = summary.index.values
Z = summary.values
Xi, Yi = np.meshgrid(X, Y)
# plt.contourf(Yi, Xi, Z, alpha=0.7, cmap=plt.cm.jet)
# plt.show()

fig = plt.figure(figsize=(6, 5))
left, bottom, width, height = 0.1, 0.1, 0.8, 0.8
ax = fig.add_axes([left, bottom, width, height])
# cp = plt.contourf(Xi, Yi, Z, 100, locator=ticker.LogLocator(subs=(9, 90, 99, 999, 999.9)), cmap=cm.PuBu_r)
# cp = ax.contour(X, Y, Z, locator=ticker.LogLocator(subs=(9, 90, 99, 999)))
cp = ax.contour(X/1000, Y/1000, Z, locator=ticker.FixedLocator([0.5,0.6,0.7,0.8, 0.9,0.95, 0.96, 0.97, 0.98, 0.99,0.999, 0.9999, 0.99999]))
#plt.colorbar(cp)
ax.clabel(cp, inline=1, fontsize=10)
ax.set_title('Self sufficiency')
ax.set_xlabel('Battery (kWh)')
ax.set_ylabel('solar (kWp)')
ax.yaxis.grid(True)
ax.xaxis.grid(True)
plt.show()
