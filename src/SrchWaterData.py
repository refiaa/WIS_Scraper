import requests
import os
import calendar

from bs4 import BeautifulSoup

class BaseSrchWaterData:
    BASE_URL = "http://www1.river.go.jp/cgi-bin/"

    def __init__(self, js_detail, kind_value, data_type):
        self.js_detail = js_detail
        self.kind_value = kind_value
        self.data_type = data_type

    def fetch_header_value(self):
        url = f"{self.BASE_URL}{self.data_type}.exe?ID={self.js_detail}&KIND={self.kind_value}&PAGE=0"
        response = requests.get(url)
        response.encoding = 'EUC-JP'

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            header_tag = soup.find('font', size="+2")
            return header_tag.get_text(strip=True) if header_tag else "Header not found"
        else:
            return "Error accessing the page"

    def fetch_table_data(self):
        url = f"{self.BASE_URL}{self.data_type}.exe?ID={self.js_detail}&KIND={self.kind_value}&PAGE=0"
        response = requests.get(url)
        response.encoding = 'EUC-JP'

        if response.status_code != 200:
            return "Error accessing the page"

        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')

        data_list = []
        for row in rows:
            cells = row.find_all('td')
            for i, cell in enumerate(cells):
                if cell.get('bgcolor') == "#FFFFCC":
                    current_year = cell.get_text(strip=True).replace('*', '')
                    data_cells = cells[i+1:i+11]
                    for j, data_cell in enumerate(data_cells):
                        img_tag = data_cell.find('img')
                        if img_tag:
                            img_src = img_tag['src']
                            status = 'ari' if 'ari.gif' in img_src else 'nashi'
                            year_data = f"{current_year}{j} - {status}"
                            data_list.append(year_data)
                    break
        return data_list

    def fetch_station_data(self):
        url = f"{self.BASE_URL}{self.data_type}.exe?ID={self.js_detail}&KIND={self.kind_value}&PAGE=0"
        response = requests.get(url)
        response.encoding = 'EUC-JP'

        if response.status_code != 200:
            return "Error accessing the page"

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'border': '1'})
        if not table:
            return "No table found"

        station_data = {}
        rows = table.find_all('tr')[1:]
        for row in rows:
            cells = row.find_all('td')
            if len(cells) == 4:
                station_data = {
                    '観測所名': cells[1].get_text(strip=True),
                    '水系名': cells[2].get_text(strip=True),
                    '河川名': cells[3].get_text(strip=True)
                }
                break

        return station_data

    def filter_years(self):
        data_list = self.fetch_table_data()
        filtered_years = []

        for data in data_list:
            year, status = data.split(' - ')
            if status == 'ari':
                filtered_years.append(year)

        return filtered_years

class SrchWaterData_1(BaseSrchWaterData):
    def __init__(self, js_detail, kind_value, start_year=None, start_month=None, end_year=None, end_month=None):
        super().__init__(js_detail, kind_value, "SrchWaterData")
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
        url = f"{self.BASE_URL}DspWaterData.exe?KIND={self.kind_value}&ID={self.js_detail}&BGNDATE={year}{month_str}01&ENDDATE={year}{month_str}{last_day}&KAWABOU=NO"
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
        directory = f"./Download/SrchWaterData_{self.kind_value}_{self.station_data.get('水系名', 'Unknown')}_{self.station_data.get('河川名', 'Unknown')}_{self.station_data.get('観測所名', 'Unknown')}"
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        file_path = os.path.join(directory, f"{year}_{month:02d}.dat")
        with open(file_path, "wb") as file:
            file.write(content)

class SrchWaterData_2(BaseSrchWaterData):
    def __init__(self, js_detail, kind_value, start_year=None, start_month=None, end_year=None, end_month=None):
        super().__init__(js_detail, kind_value, "SrchWaterData")
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
        url = f"{self.BASE_URL}DspWaterData.exe?KIND={self.kind_value}&ID={self.js_detail}&BGNDATE={year}{month_str}01&ENDDATE={year}{month_str}31&KAWABOU=NO"
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
        directory = f"./Download/SrchWaterData_{self.kind_value}_{self.station_data.get('水系名', 'Unknown')}_{self.station_data.get('河川名', 'Unknown')}_{self.station_data.get('観測所名', 'Unknown')}"
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        file_path = os.path.join(directory, f"{year}_{month:02d}.dat")
        with open(file_path, "wb") as file:
            file.write(content)

class SrchWaterData_3(BaseSrchWaterData):
    def __init__(self, js_detail, kind_value, start_year=None, end_year=None):
        super().__init__(js_detail, kind_value, "SrchWaterData")
        self.start_year = start_year
        self.end_year = end_year

        self.station_data = self.fetch_station_data()

    def scrape_data_for_years(self):
        for year in range(self.start_year, self.end_year + 1):
            self.scrape_data_for_year(year)

    def scrape_data_for_year(self, year):
        url = f"{self.BASE_URL}DspWaterData.exe?KIND={self.kind_value}&ID={self.js_detail}&BGNDATE={year}0131&ENDDATE={year}1231&KAWABOU=NO"
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
            directory = f"./Download/SrchWaterData_{self.kind_value}_{self.station_data.get('水系名', 'Unknown')}_{self.station_data.get('河川名', 'Unknown')}_{self.station_data.get('観測所名', 'Unknown')}"
        else:
            directory = f"./Download/SrchWaterData_{self.kind_value}_{self.js_detail}"

        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        file_path = os.path.join(directory, f"{year}.dat")
        with open(file_path, "wb") as file:
            file.write(content)

class SrchWaterData_4(BaseSrchWaterData):
    def __init__(self, js_detail, kind_value, start_year=None, end_year=None):
        super().__init__(js_detail, kind_value, "SrchWaterData")
        self.start_year = start_year
        self.end_year = end_year
        self.station_data = self.fetch_station_data() 

    def scrape_data_for_period(self):
        url = f"{self.BASE_URL}DspWaterData.exe?KIND={self.kind_value}&ID={self.js_detail}&BGNDATE={self.start_year}0131&ENDDATE={self.end_year}1231&KAWABOU=NO"
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
        directory = f"./Download/SrchWaterData_{self.kind_value}_{self.station_data.get('水系名', 'Unknown')}_{self.station_data.get('河川名', 'Unknown')}_{self.station_data.get('観測所名', 'Unknown')}"
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        file_path = os.path.join(directory, f"{period}.dat")
        with open(file_path, "wb") as file:
            file.write(content)

