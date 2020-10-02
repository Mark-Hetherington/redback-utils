POWERSHOP_EV_TARIFF = [
    {'hour_from': 0, 'hour_to': 24, 'day_from': 6, 'day_to': 7, 'cost': 16.42},  # Weekends
    {'hour_from': 0, 'hour_to': 4, 'day_from': 0, 'day_to': 7, 'cost': 29.37},  # Shoulder 2
    {'hour_from': 4, 'hour_to': 7, 'day_from': 0, 'day_to': 7, 'cost': 16.42},  # Off peak
    {'hour_from': 7, 'hour_to': 17, 'day_from': 0, 'day_to': 7, 'cost': 24.93},  # Shoulder 1
    {'hour_from': 17, 'hour_to': 20, 'day_from': 0, 'day_to': 7, 'cost': 29.37},  # Peak
    {'hour_from': 20, 'hour_to': 22, 'day_from': 0, 'day_to': 7, 'cost': 29.37},  # Shoulder 1
    {'hour_from': 22, 'hour_to': 24, 'day_from': 0, 'day_to': 7, 'cost': 16.42},  # Off peak
    {'hour_from': 0, 'hour_to': 24, 'day_from': 0, 'day_to': 7, 'cost': 29.37}  # catch all!
]