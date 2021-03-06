import pandas
import json
import os

import matplotlib.pyplot as plt

from constants import data_directory
import pytz

sydney_tz = pytz.timezone('Australia/Sydney')


def load_json(filename):
    # TODO: We are going to want to translate the data into usable series
    with open(filename) as data_file:
        data = json.load(data_file)
    if 'data' in data:
        data = data['data']['PlotPoints']
        df = pandas.json_normalize(data)
    else:
        df = pandas.read_json(filename)
    df.index = pandas.to_datetime(df['Epoch'], unit='s')
    df.index = df.index.tz_localize(pytz.utc).tz_convert(sydney_tz)

    return df


def load_hdf(filename):
    return pandas.read_hdf(filename, 'table')


def load_file(filename):
    if filename.endswith('.json'):
        return load_json(filename)
    else:
        return load_hdf(filename)


def load_all_data():
    return load_hdf(os.path.join(data_directory, "all.h5"))


def load_all_byminute_data():
    return load_hdf(os.path.join(data_directory, "byminute.h5"))


def load_interpolated_byminute_data():
    return load_hdf(os.path.join(data_directory, "byminute-interpolated.h5"))


def load_all_json_data(limit=None):
    limit = limit + 1 if limit else None
    dfs = []

    for filename in os.listdir(data_directory):
        if filename.endswith(".json"):
            if limit:
                limit -= 1
                if limit == 0:
                    break
            print('Reading {}'.format(filename))
            try:
                item = load_json(os.path.join(data_directory, filename))
                # Resample to minute resolution otherwise timestamps won't line up
                # dfs.append(item.resample('10T').mean())
                dfs.append(item)
            except KeyError:
                pass  # Probably empty datafile

    data = pandas.concat(dfs)
    return data


def convert_columns_types(dataframe):
    numeric_columns = ['ACLoad.Phases', 'BackupLoad.Phases', 'Grid.Phases',
                       'Battery.SoC', 'Battery.I', 'Battery.P',
                       'Battery.V', 'Battery.Phases', 'BatteryCabinet.Temperature',
                       'BatteryCabinet.FanState',
                       'BatteryMeasurements.Phases',
                       'ConnectionStatus.WiFiSignalStrength']
    boolean_columns = ['OuijaBoard.CTComms']
    # unknown_columns = ['Battery.Batteries', 'PV.PVs']
    for column in numeric_columns:
        if column in dataframe:
            dataframe[column] = pandas.to_numeric(dataframe[column])

    for column in boolean_columns:
        if column in dataframe:
            dataframe[column] = dataframe[column].astype('bool')


def resample_dataframe(dataframe, unit='T'):
    convert_columns_types(dataframe)
    return dataframe.resample(unit).mean()


def kW_series_to_kWh(series):
    return series.sum() / 1000 / 60


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd=""):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def dataset_stats(data):
    if 'simulation.PV.P' in data:
        stats = {
            "PV": kW_series_to_kWh(data['simulation.PV.P']),
            'spill': kW_series_to_kWh(data['simulation.Spill.P']),
            'exports': kW_series_to_kWh(data['simulation.Grid.P'].clip(lower=0)),
            'imports': kW_series_to_kWh(data['simulation.Grid.P'].clip(upper=0)),
            'consumption': kW_series_to_kWh(data['ACLoad.P'])
        }
    else:
        stats = {
            "PV": kW_series_to_kWh(data['PV.P']),
            'exports': kW_series_to_kWh(data['Grid.P'].clip(lower=0)),
            'imports': kW_series_to_kWh(data['Grid.P'].clip(upper=0)),
            'consumption': kW_series_to_kWh(data['ACLoad.P'])
        }
    if 'simulation.cost' in data:
        stats['cost'] = data['simulation.cost'].sum()/100
    if 'simulation.self_sufficiency' in data:
        stats['self_sufficiency'] = data['simulation.self_sufficiency'].mean()
    print("PV generation: %d kWh" % stats['PV'])
    if 'spill' in stats:
        print("Total spill: %d kWh" % stats['spill'])
    if 'self_sufficiency' in stats:
        print("Self Sufficiency (by minute): %.2f %%" % (stats['self_sufficiency']*100))
    print("Total exports: %d kWh" % stats['exports'])
    print("Total imports: %d kWh" % stats['imports'])
    if 'cost' in stats:
        print("Total electricity tariffs: $%.2f" % stats['cost'])
    return stats


def plot_simulation(df):
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