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
            #dfs.append(item.resample('10T').mean())
            dfs.append(item)
        except KeyError:
            pass  # Probably empty datafile

    data = pandas.concat(dfs)
    return data


def convert_columns_to_numeric(dataframe):
    dataframe['Battery.P'] = pandas.to_numeric(dataframe['Battery.P'])
    dataframe['Battery.SoC'] = pandas.to_numeric(dataframe['Battery.SoC'])


def resample_dataframe(dataframe, unit):
    convert_columns_to_numeric(dataframe)
    return dataframe.resample('T').mean()


def kW_series_to_kWh(series):
    return series.sum()/1000/60

