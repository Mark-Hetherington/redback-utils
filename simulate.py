import pandas
import os

from constants import output_directory
from tariffs import POWERSHOP_EV_TARIFF
from utils import load_all_json_data, load_json, resample_dataframe, kW_series_to_kWh, print_progress_bar, \
    load_all_byminute_data, load_interpolated_byminute_data, dataset_stats


class Simulator:
    data = None

    def __init__(self, data):
        self.data = data


    def simulate(self, multiply_PV=None, battery_capacity=None, export_limit=None, battery_charge_limit=None,
                 battery_discharge_limit=None, battery_soc_min=None, tariffs=None, feed_in_tariff=None):
        multiply_PV = multiply_PV or 2  # Increase solar by a factor of 2
        battery_capacity = battery_capacity or 10000  # Set battery capacity at 50kwh
        export_limit = export_limit or 5000  # Export limit is 5kw
        battery_charge_limit = battery_charge_limit or 4000  # battery charge rate is limited to 8kw
        battery_discharge_limit = battery_discharge_limit or 4000  # battery charge rate is limited to 8kw
        battery_soc_min = battery_soc_min or 15  # Battery limited to 15% state of charge
        tariffs = tariffs or POWERSHOP_EV_TARIFF
        data = self.data.copy()

        # data = load_all_json_data(limit=10)
        # data = load_pandas('data/2018-12-26.json')
        # data = resample_dataframe(data, 'T')

        simulation_soc = battery_soc_min * battery_capacity / 100  # Assume fully discharged to start simulation

        # for each minute of data, extrapolate new values
        print("Simulating data on %d rows" % data['Epoch'].count())
        row_index = 0
        row_total = data['Epoch'].count()

        for index, row in data.iterrows():
            max_pv_power = row['PV.P'] * multiply_PV
            battery_power = max_pv_power - row['ACLoad.P']
            battery_power = min(max(battery_power, -battery_discharge_limit), battery_charge_limit)
            # TODO: Factor in battery capacity and calculate new capacity
            battery_delta = battery_power / 60  # Convert to Watt hours from watt minutes
            if simulation_soc + battery_delta < (battery_soc_min / 100 * battery_capacity):
                battery_power = 0
            elif simulation_soc + battery_delta > battery_capacity:
                battery_power = 0
            else:
                simulation_soc += battery_delta
            grid_power = max_pv_power - row['ACLoad.P'] - battery_power
            grid_power = min(grid_power, export_limit)

            pv_power = battery_power + grid_power + row['ACLoad.P']
            pv_spill = max_pv_power - pv_power

            # TODO: Calculate energy tariff cost

            grid_Wh = grid_power / 60  # convert to watt hours instead of watt minutes
            grid_kWh = grid_Wh / 1000
            if grid_power < 0:
                # Time of day lookup needed. Assume day of week-hourly resolution is sufficient
                for tariff in tariffs:
                    if tariff['hour_from'] <= index.hour < tariff['hour_to'] \
                            and tariff['day_from'] <= index.dayofweek < tariff['day_to']:
                        cost = tariff['cost'] * -grid_kWh
                        break
                else:
                    raise ValueError("No tariff found")
            else:
                cost = 0

            data.at[index, 'simulation.PV.P'] = pv_power
            data.at[index, 'simulation.Battery.P'] = battery_power
            data.at[index, 'simulation.Battery.SoC'] = simulation_soc / battery_capacity * 100
            data.at[index, 'simulation.Grid.P'] = grid_power
            data.at[index, 'simulation.Spill.P'] = pv_spill
            data.at[index, 'simulation.cost'] = cost
            row_index += 1
            print_progress_bar(row_index, row_total)

        return data


simulations = [
    {
        "name": "Current system",
        "multiply_PV": 1,
        "battery_capacity": 10000,
        "export_limit": 5000,
        "battery_charge_limit": 4000,
        "battery_discharge_limit": 4000,
        "battery_soc_min": 20
    },
    {
        "name": "Add solar only",
        "multiply_PV": 2,
        "battery_capacity": 10000,
        "export_limit": 5000,
        "battery_charge_limit": 4000,
        "battery_discharge_limit": 4000,
        "battery_soc_min": 20
    },
    {
        "name": "Add battery only",
        "multiply_PV": 1,
        "battery_capacity": 50000,
        "export_limit": 5000,
        "battery_charge_limit": 7000,
        "battery_discharge_limit": 7000,
        "battery_soc_min": 20
    },
    {
        "name": "Full upgrade",
        "multiply_PV": 2,
        "battery_capacity": 50000,
        "export_limit": 5000,
        "battery_charge_limit": 7000,
        "battery_discharge_limit": 7000,
        "battery_soc_min": 20
    }
]
simulations = []

for pv_size in range(10, 45, 5):
    for battery_size in range(10000, 210000, 40000):
        # for feed_in_tariff in [7, 14, 21]:
        simulations.append({
            "name": "pv-%.2f-battery-%d" % (pv_size/10.0, battery_size),
            "multiply_PV": pv_size/10.0,
            "battery_capacity": battery_size,
            "export_limit": 5000,
            "battery_charge_limit": 7000 if battery_size > 1000 else 4000,
            "battery_discharge_limit": 7000 if battery_size > 1000 else 4000,
            "battery_soc_min": 20,
            # "feed_in_tariff": feed_in_tariff
        })

if __name__ == "__main__":
    print("Running %d simulations" % len(simulations))
    print("Loading data")
    data = load_interpolated_byminute_data()
    # data = load_all_json_data(limit=10)
    simulator = Simulator(data)
    overall_stats = []
    for simulation in simulations:
        name = simulation.pop('name')
        print("Running simulation '%s'" % name)
        simulated_data = simulator.simulate(**simulation)
        stats = dataset_stats(simulated_data)
        stats['name'] = name
        stats['PV-size'] = simulation['multiply_PV']
        stats['battery-size'] = simulation['battery_capacity']
        overall_stats.append(stats)
        simulated_data.to_hdf(os.path.join(output_directory, "simulation-%s.h5" % name), 'table')
        # # Convert to a mean day
        simulated_data = simulated_data.groupby(data.index.time).mean()
        simulated_data.to_hdf(os.path.join(output_directory, "simulation-mean-day-%s.h5" % name), 'table')

    stats_df = pandas.DataFrame(overall_stats)
    # stats_df.plot.scatter(x='PV-size', y='battery-size', c='cost')
    stats_df.to_json(os.path.join(output_directory, "simulation-stats.json"))
    stats_df.to_csv(os.path.join(output_directory, "simulation-stats.csv"))
