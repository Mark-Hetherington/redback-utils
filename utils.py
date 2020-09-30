import pandas
import json
import os

from constants import data_directory
import pytz

sydney_tz = pytz.timezone('Australia/Sydney')


def load_pandas(filename):
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


def load_all_data(limit=None):
    limit = limit + 1 if limit else None
    dfs = []

    for filename in os.listdir(data_directory):
        if limit:
            limit -= 1
            if limit == 0:
                break
        print('Reading {}'.format(filename))
        try:
            item = load_pandas(os.path.join(data_directory, filename))
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


def resample_dataframe(dataframe, unit):
    convert_columns_types(dataframe)
    return dataframe.resample('T').mean()


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
