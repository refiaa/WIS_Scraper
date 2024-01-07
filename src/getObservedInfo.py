import requests
from bs4 import BeautifulSoup

class ObservedInfoScraper:
    def __init__(self, js_detail):
        self.base_url = "http://www1.river.go.jp/cgi-bin/SiteInfo.exe?ID="
        self.js_detail = js_detail

    def scrape(self):
        url = self.base_url + self.js_detail
        response = requests.get(url)
        response.encoding = 'EUC-JP'
        soup = BeautifulSoup(response.text, 'html.parser')

        data = []
        for img_tag in soup.find_all('img'):
            alt_text = img_tag.get('alt')
            if alt_text and alt_text not in ["位置図", "観測所詳細諸元", "リアルタイム雨量", "川の防災情報", "雨量・水位ランキング検索", "リアルタイム水位", "リアルタイムダム諸量検索"]:
                data.append(alt_text)

        return data

