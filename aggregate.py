import os

from constants import data_directory
from utils import load_all_json_data, convert_columns_types, resample_dataframe

data = load_all_json_data()
convert_columns_types(data)
data.to_hdf(os.path.join(data_directory, "all.h5"), 'table')
data = resample_dataframe(data, 'T')
data.to_hdf(os.path.join(data_directory, "byminute.h5"), 'table')
