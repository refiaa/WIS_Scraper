import requests
import os
import calendar

from bs4 import BeautifulSoup
from base_srch_data import BaseSrchData

class SrchRainData(BaseSrchData):
    def __init__(self, js_detail, kind_value):
        super().__init__(js_detail, kind_value, "SrchRainData")

class SrchRainData_1(SrchRainData):
    def __init__(self, js_detail, kind_value, start_year=None, start_month=None, end_year=None, end_month=None):
        super().__init__(js_detail, kind_value)
        self.start_year = start_year
        self.start_month = start_month
        self.end_year = end_year
        self.end_month = end_month
        self.station_data = self.fetch_station_data()

    def scrape_data_for_months(self):
        for year in range(self.start_year, self.end_year + 1):
            for month in range(1, 13):
                if year == self.start_year and month < self.start_month:
                    continue
                if year == self.end_year and month > self.end_month:
                    break
                self.scrape_data_for_month(year, month)

    def scrape_data_for_month(self, year, month):
        month_str = f"{month:02d}"
        last_day = calendar.monthrange(year, month)[1]
        url = f"{self.BASE_URL}DspRainData.exe?KIND={self.kind_value}&ID={self.js_detail}&BGNDATE={year}{month_str}01&ENDDATE={year}{month_str}{last_day}&KAWABOU=NO"
        response = requests.get(url)
        response.encoding = 'EUC-JP'

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            link_tag = soup.find('a', href=True, target="_blank")
            if link_tag:
                temp_number = link_tag['href'].split('/')[-1].split('.')[0]
                self.download_data_file(temp_number, year, month)

    def download_data_file(self, temp_number, year, month):
        download_url = f"http://www1.river.go.jp/dat/dload/download/{temp_number}.dat"
        response = requests.get(download_url)

        if response.status_code == 200:
            self.save_to_file(response.content, year, month)

    def save_to_file(self, content, year, month):
        directory = f"./Download/SrchRainData_{self.kind_value}_{self.station_data.get('水系名', 'Unknown')}_{self.station_data.get('河川名', 'Unknown')}_{self.station_data.get('観測所名', 'Unknown')}"
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        file_path = os.path.join(directory, f"{year}_{month:02d}.dat")
        with open(file_path, "wb") as file:
            file.write(content)

        
class SrchRainData_2(SrchRainData):
    def __init__(self, js_detail, kind_value, start_year=None, start_month=None, end_year=None, end_month=None):
        super().__init__(js_detail, kind_value)
        self.start_year = start_year
        self.start_month = start_month
        self.end_year = end_year
        self.end_month = end_month
        self.station_data = self.fetch_station_data()

    def scrape_data_for_months(self):
        for year in range(self.start_year, self.end_year + 1):
            for month in range(1, 13):
                if year == self.start_year and month < self.start_month:
                    continue
                if year == self.end_year and month > self.end_month:
                    break
                self.scrape_data_for_month(year, month)

    def scrape_data_for_month(self, year, month):
        month_str = f"{month:02d}"
        url = f"{self.BASE_URL}DspRainData.exe?KIND={self.kind_value}&ID={self.js_detail}&BGNDATE={year}{month_str}01&ENDDATE={year}{month_str}31&KAWABOU=NO"
        response = requests.get(url)
        response.encoding = 'EUC-JP'

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            link_tag = soup.find('a', href=True, target="_blank")
            if link_tag:
                temp_number = link_tag['href'].split('/')[-1].split('.')[0]
                self.download_data_file(temp_number, year, month)

    def download_data_file(self, temp_number, year, month):
        download_url = f"http://www1.river.go.jp/dat/dload/download/{temp_number}.dat"
        response = requests.get(download_url)

        if response.status_code == 200:
            self.save_to_file(response.content, year, month)

    def save_to_file(self, content, year, month):
        directory = f"./Download/SrchRainData_{self.kind_value}_{self.station_data.get('水系名', 'Unknown')}_{self.station_data.get('河川名', 'Unknown')}_{self.station_data.get('観測所名', 'Unknown')}"
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        file_path = os.path.join(directory, f"{year}_{month:02d}.dat")
        with open(file_path, "wb") as file:
            file.write(content)

class SrchRainData_3(SrchRainData):
    def __init__(self, js_detail, kind_value, start_year=None, end_year=None):
        super().__init__(js_detail, kind_value)
        self.start_year = start_year
        self.end_year = end_year

        self.station_data = self.fetch_station_data()

    def scrape_data_for_years(self):
        for year in range(self.start_year, self.end_year + 1):
            self.scrape_data_for_year(year)

    def scrape_data_for_year(self, year):
        url = f"{self.BASE_URL}DspRainData.exe?KIND={self.kind_value}&ID={self.js_detail}&BGNDATE={year}0131&ENDDATE={year}1231&KAWABOU=NO"
        response = requests.get(url)
        response.encoding = 'EUC-JP'

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            link_tag = soup.find('a', href=True, target="_blank")
            if link_tag:
                temp_number = link_tag['href'].split('/')[-1].split('.')[0]
                self.download_data_file(temp_number, year)

    def download_data_file(self, temp_number, year):
        download_url = f"http://www1.river.go.jp/dat/dload/download/{temp_number}.dat"
        response = requests.get(download_url)

        if response.status_code == 200:
            self.save_to_file(response.content, year)

    def save_to_file(self, content, year):
        if self.station_data:
            directory = f"./Download/SrchRainData_{self.kind_value}_{self.station_data.get('水系名', 'Unknown')}_{self.station_data.get('河川名', 'Unknown')}_{self.station_data.get('観測所名', 'Unknown')}"
        else:
            directory = f"./Download/SrchRainData_{self.kind_value}_{self.js_detail}"

        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        file_path = os.path.join(directory, f"{year}.dat")
        with open(file_path, "wb") as file:
            file.write(content)

class SrchRainData_4(SrchRainData):
    def __init__(self, js_detail, kind_value, start_year=None, end_year=None):
        super().__init__(js_detail, kind_value)
        self.start_year = start_year
        self.end_year = end_year
        self.station_data = self.fetch_station_data() 

    def scrape_data_for_period(self):
        url = f"{self.BASE_URL}DspRainData.exe?KIND={self.kind_value}&ID={self.js_detail}&BGNDATE={self.start_year}0131&ENDDATE={self.end_year}1231&KAWABOU=NO"
        response = requests.get(url)
        response.encoding = 'EUC-JP'

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            link_tag = soup.find('a', href=True, target="_blank")
            if link_tag:
                temp_number = link_tag['href'].split('/')[-1].split('.')[0]
                self.download_data_file(temp_number)

    def download_data_file(self, temp_number):
        download_url = f"http://www1.river.go.jp/dat/dload/download/{temp_number}.dat"
        response = requests.get(download_url)

        if response.status_code == 200:
            self.save_to_file(response.content, f"{self.start_year}-{self.end_year}")

    def save_to_file(self, content, period):
        directory = f"./Download/SrchRainData_{self.kind_value}_{self.station_data.get('水系名', 'Unknown')}_{self.station_data.get('河川名', 'Unknown')}_{self.station_data.get('観測所名', 'Unknown')}"
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        file_path = os.path.join(directory, f"{period}.dat")
        with open(file_path, "wb") as file:
            file.write(content)

