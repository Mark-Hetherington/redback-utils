import os
import json
import datetime

# Produces an "average" day from all the data.

output_directory = "output"
data_directory = "data"

data = None

def timeofday(point):
    date = datetime.datetime.fromisoformat(point['Date'])
    daystart = datetime.datetime(year=date.year, month=date.month, day=date.day)
    return date-daystart

for filename in os.listdir(data_directory):
    with open(os.path.join(data_directory, filename)) as f:
        content = f.read()
    file_data = json.loads(content)
    if 'data' in file_data and 'PlotPoints' in file_data['data'] and file_data['data']['PlotPoints']:
        file_data = file_data['data']['PlotPoints']
        if data is None:
            data = file_data
        else:
            # Merge data based on timestamps
            for point in file_data:
                point_timeofday = timeofday(point)
                match = next([d for d in data if timeofday(data) == point_timeofday])

# TODO: Convert total and count to average


if not os.path.exists(output_directory):
    os.mkdir(output_directory)

with open(os.path.join(output_directory, "average.json"), "w") as f:
    f.write(json.dumps(data))
