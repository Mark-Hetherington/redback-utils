import datetime

redback_time_format = '%Y-%m-%dT%H:%M:%S.%f'
output_directory = "output"
data_directory = "data"
login_url = "https://portal.redbacktech.com/Account/Login"
data_url = "https://portal.redbacktech.com/charts/GetDataBands?StartDate={:%d%%2F%m%%2F%Y}&EndDate={:%d%%2F%m%%2F%Y}&serialNumber={}&timezone=AUS%20Eastern%20Standard%20Time&_={:0}"


def redback_time_parse(time_str):
    return datetime.datetime.strptime(time_str[:-1][:26], redback_time_format)