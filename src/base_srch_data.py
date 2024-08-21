import requests
from bs4 import BeautifulSoup

class BaseSrchData:
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