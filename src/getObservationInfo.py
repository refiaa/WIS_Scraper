import requests
import re

from bs4 import BeautifulSoup

class ObservationDataMatcher:
    def __init__(self, js_detail, name):
        self.base_url = "http://www1.river.go.jp/cgi-bin/SiteInfo.exe"
        self.js_detail = js_detail
        self.name = name

    def check_name_in_page(self):
        response = requests.get(f"{self.base_url}?ID={self.js_detail}")
        response.encoding = 'EUC-JP'

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            images = soup.find_all('img', alt=self.name)

            for img in images:
                parent_a_tag = img.find_parent('a')
                if parent_a_tag and 'href' in parent_a_tag.attrs:
                    href = parent_a_tag['href']
                    kind_match = re.search(r'KIND=(\d+)', href)
                    if kind_match:
                        return True, kind_match.group(1)
            return False, None
        else:
            return False, None

    def check_data_type(self):
        response = requests.get(f"{self.base_url}?ID={self.js_detail}")
        response.encoding = 'EUC-JP'

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)

            for link in links:
                if 'SrchRainData' in link['href']:
                    return 0
                
                elif 'SrchWaterData' in link['href']:
                    return 1
                
                elif 'SrchWquaData' in link['href']:
                    return 2

                elif 'SrchUWaterData' in link['href']:
                    return 3
                
                elif 'SrchDamData' in link['href']:
                    return 4
                
                elif 'SrchKaisyoData'in link['href']:
                    return 5
                
                elif 'SrchSnowData'in link['href']:
                    return 6

            return None
        
        else:
            return None

class ObservationDataCrawler:
    BASE_URL = "http://www1.river.go.jp/cgi-bin/SrchRainData.exe"

    def __init__(self, js_detail, value):
        self.js_detail = js_detail
        self.value = value

    def fetch_data(self):
        params = {
            'ID': self.js_detail,
            'KIND': self.value,
            'PAGE': 0
        }

        response = requests.get(self.BASE_URL, params=params)

        if response.status_code == 200:
            response.encoding = 'EUC-JP'
            return self.parse_html(response.text)
        
        else:
            return "Error: Unable to fetch data"

    @staticmethod
    def parse_html(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        target_text = soup.find('font', size="+2").get_text(strip=True)

        return target_text
