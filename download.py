import requests
import datetime
from datetime import timedelta
import sys, getopt
from bs4 import BeautifulSoup
import os
import time

from constants import data_directory, login_url, data_url

command_text = """
{0} -e <email> -p <password> -s <serial> [-f 2019-01-01] -t [2020-01-01]
e.g. {0} -e test@example.org -p 12345678 -s RB17123456789012
    -e, --email     Specify email
    -p, --password  Specify password
    -s, --serial    Specify inverter serial number
    -f, --from      Specify from date
    -t, --to        Specify to date
    
    By default, the last 365 days of data will be retrieved.
"""

command_text = command_text.format(sys.argv[0])

class Extractor:
    email = None
    password = None
    serial = None

    def __init__(self, email, password, serial):
        self.email = email
        self.password = password
        self.serial = serial
        self._session = None


        # Spoof user agent
        # self.s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36"


    @property
    def session(self):
        if not self._session:
            self._session = requests.Session()
            self.login()
        return self._session

    def get_data(self, from_date=None, to_date=None):
        if from_date:
            from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d")
            if not to_date:
                to_date = datetime.date.today()
            else:
                to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d")
            dates = [(from_date + datetime.timedelta(days=x)).date() for x in range(0, (to_date-from_date).days)]
        else:
            dates = [(datetime.date.today() - timedelta(days=x)).date() for x in range(0, 365)]
        if not os.path.exists(data_directory):
            os.mkdir(data_directory)
        for date in dates:
            self.getforDate(date)

    def login(self):
        r = self.session.get(login_url)
        soup = BeautifulSoup(r.content)
        form = soup.find("form", class_="login-form")
        hidden_input = form.find("input", type="hidden")
        token = hidden_input.attrs['value']
        r = self.session.post(login_url, data={"Email": self.email, "Password": self.password, "RememberMe": "False",
                                         "__RequestVerificationToken": token})
        r.raise_for_status()

    def getforDate(self, date):
        print("Downloading {}".format(date))
        url = data_url.format(date, date, self.serial, time.time())
        r = self.session.get(url)

        if len(r.content) > 2000:
            with open(os.path.join(data_directory, "{:%Y-%m-%d}.json".format(date)), "w") as f:
                f.write(r.content.decode())
        else:
            print("Skipping - data length: %d" % len(r.content))


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "he:p:s:f:t:", ["email=", "password=", "serial=", "from=", "to="])
    except getopt.GetoptError as err:
        print(err)
        print(command_text)
        sys.exit(2)

    from_date = None
    to_date = None

    for opt, arg in opts:
        if opt == '-h':
            print(command_text)
            sys.exit()
        elif opt in ("-e", "--email"):
            email = arg
        elif opt in ("-p", "--password"):
            password = arg
        elif opt in ("-s", "--serial"):
            serial = arg
        elif opt in ("-f", "--from"):
            from_date = arg
        elif opt in ("-t", "--to"):
            to_date = arg

    if not email or not password or not serial:
        print(command_text)
        sys.exit()
    extractor = Extractor(email=email, password=password, serial=serial)
    extractor.get_data(from_date, to_date)

