import os
import json

from constants import *
# Produces an "average" day from all the data.

data = None
avg_keys = ('ACLoad', 'BackupLoad', 'Grid', 'BatteryMeasurements')

def timeofday(point):
    date = redback_time_parse(point['Date'])
    daystart = datetime.datetime(year=date.year, month=date.month, day=date.day)
    return date-daystart


for filename in os.listdir(data_directory):
    print('Reading {}'.format(filename))
    with open(os.path.join(data_directory, filename)) as f:
        content = f.read()
    file_data = json.loads(content)
    if 'data' in file_data and 'PlotPoints' in file_data['data'] and file_data['data']['PlotPoints']:
        file_data = file_data['data']['PlotPoints']
        if data is None:
            data = file_data
            for d in data:
                d['time_of_day'] = timeofday(d)
                d['count'] = 1
        else:
            # Merge data based on timestamps
            for point in file_data:
                point_timeofday = timeofday(point)
                match = next((d for d in data if d['time_of_day'] == point_timeofday))
                if match:
                    match['count'] += 1
                    for key in avg_keys:
                        for k in match[key]:
                            if isinstance(match[key][k], float) and isinstance(point[key][k], float):
                                match[key][k] += point[key][k]
                else:
                    point['count'] = 1
                    point['time_of_day'] = timeofday(point)
                    d.append(point)

#  Convert total and count to average
for point in data:
    point['time_of_day'] = str(point['time_of_day'])
    for key in avg_keys:
        for k in point[key]:
            if isinstance(point[key][k], float):
                point[key][k] = point[key][k] / point['count']

if not os.path.exists(output_directory):
    os.mkdir(output_directory)

with open(os.path.join(output_directory, "average.json"), "w") as f:
    f.write(json.dumps(data))
