import requests
from bs4 import BeautifulSoup
import re

class DetailInfoScraper:
    def __init__(self, js_detail):
        self.base_url = "http://www1.river.go.jp/cgi-bin/SiteInfo.exe?ID="
        self.js_detail = js_detail

    def scrape(self):
        url = self.base_url + self.js_detail
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        data = {}
        table = soup.find('table', {'align': 'CENTER', 'width': '600'})

        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) == 2:
                key = cells[0].text.strip()
                value = cells[1].text.strip()
                data[key] = value

        return data

    def save_to_file(self, data, file_name='detail_info.txt'):
        with open(file_name, 'w', encoding='utf-8') as file:
            for key, value in data.items():
                file.write(f"{key}: {value}\n")

class MapImageScraper:
    def __init__(self, js_detail, latitude, longitude):
        self.js_detail = js_detail
        self.latitude = latitude
        self.longitude = longitude
        self.base_url = "http://www1.river.go.jp/cgi-bin/"

    def scrape_image_url(self):
        url = f"{self.base_url}DspMapPosition.exe?MODE=01&MAP=0&ID={self.js_detail}&SIDO={self.latitude}&SKEIDO={self.longitude}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        image_element = soup.find('img', alt="拡大図1")
        if image_element:
            return self.base_url + image_element['src']

        return None
    
class SiteHtmlChecker:
    def __init__(self, js_detail):
        self.base_url = "http://www1.river.go.jp/cgi-bin/SiteInfo.exe?ID="
        self.js_detail = js_detail
        self.check_img = False

    def check_for_image(self):
        url = self.base_url + self.js_detail
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        image_element = soup.find('img', {'src': '/img/btn_view_pos.png'})
        self.check_img = bool(image_element)

        return self.check_img
