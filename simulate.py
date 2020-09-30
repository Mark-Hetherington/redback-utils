from utils import load_all_data, load_pandas, resample_dataframe, kW_series_to_kWh, print_progress_bar
import matplotlib.pyplot as plt

multiply_PV = 2  # Increase solar by a factor of 2
battery_capacity = 50000  # Set battery capacity at 50kwh
export_limit = 5000  # Export limit is 5kw
battery_charge_limit = 8000  # battery charge rate is limited to 8kw
battery_discharge_limit = 8000  # battery charge rate is limited to 8kw
battery_soc_min = 15  # Battery limited to 15% state of charge
data = load_all_data()
# data = load_pandas('data/2018-12-26.json')
data = resample_dataframe(data, 'T')
data = data.interpolate(method='index')

simulation_soc = battery_soc_min * battery_capacity/100  # Assume fully discharged to start simulation

# for each minute of data, extrapolate new values
print("Simulating data on %d rows" % data['Epoch'].count())
row_index = 0
row_total = data['Epoch'].count()

for index, row in data.iterrows():
    max_pv_power = row['PV.P'] * 2
    battery_power = max_pv_power - row['ACLoad.P']
    battery_power = min(max(battery_power, -battery_discharge_limit), battery_charge_limit)
    # TODO: Factor in battery capacity and calculate new capacity
    battery_delta = battery_power/60  # Convert to Watt hours from watt minutes
    if simulation_soc + battery_delta < (battery_soc_min/100 * battery_capacity):
        battery_power = 0
    elif simulation_soc + battery_delta > battery_capacity:
        battery_power = 0
    else:
        simulation_soc += battery_delta
    grid_power = max_pv_power - row['ACLoad.P'] - battery_power
    grid_power = min(grid_power, export_limit)
    pv_power = battery_power + grid_power + row['ACLoad.P']
    pv_spill = max_pv_power - pv_power
    data.at[index, 'simulation.PV.P'] = pv_power
    data.at[index, 'simulation.Battery.P'] = battery_power
    data.at[index, 'simulation.Battery.SoC'] = simulation_soc/battery_capacity*100
    data.at[index, 'simulation.Grid.P'] = grid_power
    data.at[index, 'simulation.Spill.P'] = pv_spill
    row_index += 1
    print_progress_bar(row_index, row_total)

print("PV generation: %d kWh" % kW_series_to_kWh(data['PV.P']))
print("Total spill: %d kWh" % kW_series_to_kWh(data['simulation.Spill.P']))
print("Total exports: %d kWh" % kW_series_to_kWh(data['simulation.Grid.P'].clip(lower=0)))
print("Total imports: %d kWh" % kW_series_to_kWh(data['simulation.Grid.P'].clip(upper=0)))
# Convert to an mean day
data = data.groupby(data.index.time).mean()
data["ACLoad.P"].plot(label="Load")
data["simulation.PV.P"].plot(label="PV")
# data["PV.P"].plot()
# data['Grid.P'].plot()
# data['simulation.Battery.P'].plot(label="Battery")
data['simulation.Battery.SoC'].plot(label="SoC", secondary_y=True)
data['simulation.Grid.P'].plot(label="Grid")
ax = data['simulation.Spill.P'].plot(label="Spill")
plt.legend()
ax.legend(loc="upper left")
plt.show()
