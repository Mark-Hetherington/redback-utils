import os

from constants import data_directory
from utils import load_all_json_data, convert_columns_types, resample_dataframe

data = load_all_json_data()
print("Converting column types")
convert_columns_types(data)
print("Writing complete data set")
data.to_hdf(os.path.join(data_directory, "all.h5"), 'table')
print("Resampling to by minute samples")
data = resample_dataframe(data, 'T')
print("Writing by minute samples")
data.to_hdf(os.path.join(data_directory, "byminute.h5"), 'table')
print("Writing interpolated samples")
data = data.interpolate(method='index')
data.to_hdf(os.path.join(data_directory, "byminute-interpolated.h5"), 'table')
