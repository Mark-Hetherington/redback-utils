import requests
import datetime
from datetime import timedelta
import sys, getopt
from bs4 import BeautifulSoup
import os

login_url = "https://portal.redbacktech.com/Account/Login"
data_url = "https://portal.redbacktech.com/charts/GetDataBands?StartDate={:%d/%m/%Y}&EndDate={:%d/%m/%Y}&serialNumber={}&timezone=AUS%20Eastern%20Standard%20Time"

data_directory = "data"

command_text = """
{0} -e <email> -p <password> -s <serial>
e.g. {0} -e test@example.org -p 12345678 -s RB17123456789012
"""

command_text = command_text.format(sys.argv[0])

class Extractor:
    email = None
    password = None
    serial = None

    def __init__(self, argv):
        try:
            opts, args = getopt.getopt(argv, "he:p:s:", ["email=", "password=", "serial="])
        except getopt.GetoptError as err:
            print(err)
            print(command_text)
            sys.exit(2)

        for opt, arg in opts:
            if opt == '-h':
                print(command_text)
                sys.exit()
            elif opt in ("-e", "--email"):
                self.email = arg
            elif opt in ("-p", "--password"):
                self.password = arg
            elif opt in ("-s", "--serial"):
                self.serial = arg

        if not self.email or not self.password or not self.serial:
            print(command_text)
            sys.exit()

        self.s = requests.Session()
        # Spoof user agent
        # self.s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36"
        self.login()
        if not os.path.exists(data_directory):
            os.mkdir(data_directory)
        for i in range(1, 366):
            date = datetime.date.today() - timedelta(days=i)
            print("Downloading {}".format(date))
            result = self.getforDate(datetime.date.today())
            with open(os.path.join(data_directory, "data/{:%Y-%m-%d}.json".format(date)), "w") as f:
                f.write(result.decode())


    def login(self):
        r = self.s.get(login_url)
        soup = BeautifulSoup(r.content)
        form = soup.find("form", class_="login-form")
        hidden_input = form.find("input", type="hidden")
        token = hidden_input.attrs['value']
        r = self.s.post(login_url, data={"Email": self.email, "Password": self.password, "RememberMe": "False",
                                         "__RequestVerificationToken": token})
        r.raise_for_status()

    def getforDate(self, date):
        url = data_url.format(date, date, self.serial)
        r = self.s.get(url)
        return r.content


if __name__ == "__main__":
    Extractor(sys.argv[1:])
