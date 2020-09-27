import os
import json

from constants import *
# Produces an "average" day from all the data.
from utils import load_pandas, load_all_data
import pandas as pd


data = load_all_data(limit=60)
by_time = data.groupby(data.index.time).mean()

if not os.path.exists(output_directory):
    os.mkdir(output_directory)

by_time.to_json(os.path.join(output_directory, "average.json"))
