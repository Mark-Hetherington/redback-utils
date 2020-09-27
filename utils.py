import pandas
import json
import os

from constants import data_directory


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
    return df


def load_all_data(limit=None):
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
            dfs.append(item.resample('T').mean())
        except KeyError:
            pass  # Probably empty datafile

    data = pandas.concat(dfs)
    return data