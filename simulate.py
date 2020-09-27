from utils import load_all_data
import matplotlib.pyplot as plt

multiply_PV = 2  # Increase solar by a factor of 2
battery_capacity = 50000  # Set battery capacity at 50kwh
export_limit = 5000  # Export limit is 5kw
battery_charge_limit = 8000  # battery charge rate is limited to 8kw
data = load_all_data(limit=5)

# for each minute of data, extrapolate new values

for index, row in data.iterrows():
    max_pv_power = row['PV.P'] * 2
    battery_power = max_pv_power - row['ACLoad.P']
    battery_power = 0 # min(battery_power, battery_charge_limit)
    # TODO: Factor in battery capacity and calculate new capacity
    grid_power = max_pv_power - row['ACLoad.P'] - battery_power
    grid_power = max(grid_power, -export_limit)
    pv_power = battery_power + grid_power + row['ACLoad.P']
    pv_spill = max_pv_power - pv_power
    data.at[index, 'simulation.PV.P'] = pv_power
    data.at[index, 'simulation.Battery.P'] = battery_power
    data.at[index, 'simulation.Grid.P'] = grid_power
    data.at[index, 'simulation.Spill.P'] = pv_spill
    #print(row)

data["simulation.PV.P"].plot()
data["PV.P"].plot()
plt.legend()
plt.show()
