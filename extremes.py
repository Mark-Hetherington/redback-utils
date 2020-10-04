from utils import load_all_data, resample_dataframe

data = load_all_data()
print(data)

by_day = resample_dataframe(data, 'D')
print(by_day)

#sorted = by_day.sort_values('Grid.P')
#print(sorted)

top = by_day.nsmallest(10, 'Grid.P')
print(top)

