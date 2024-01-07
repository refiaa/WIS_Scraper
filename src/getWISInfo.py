import requests
import csv
import logging
import os
import json
import re

from bs4 import BeautifulSoup

class RiverDataScraper:
    def __init__(self, base_url, ken_file, suikei_file, komoku_file):
        self.base_url = base_url
        self.ken_values = self.load_values(ken_file)
        self.suikei_values = self.load_values(suikei_file)
        self.komoku_values = self.load_values(komoku_file) 
        self.page_number = 0

        self.data = []

    @staticmethod
    def load_values(file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            return json.load(file)

    def scrape_data(self, ken_code, suikei_code, komoku_code):
        response = requests.get(f"{self.base_url}?KOMOKU={komoku_code}&SUIKEI={suikei_code}&KEN={ken_code}&CITY=&PAGE={self.page_number}")
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('tr', align='CENTER')

        self.data = [] 

        for row in rows[1:]:
            cols = row.find_all('td')
            entry = [col.text.strip() for col in cols]

            entry.append(suikei_code)

            js_detail = row.find('a', href=True)
            js_detail_id = re.search(r"SiteDetail1\('(\d+)'\)", str(js_detail)).group(1) if js_detail else ''
            entry.append(js_detail_id)

            pattern = r'^,,,,,,\d+,$'
            if re.match(pattern, ','.join(entry)):
                continue 

            if any(entry):
                self.data.append(entry)

    def save_to_csv(self, file_name):
        output_dir = os.path.join('.', 'output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        full_file_path = os.path.join(output_dir, file_name)
        with open(full_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['No', '項目', '水系名', '河川名', '観測所名', '所在地', 'SUIKEI', 'JavaScriptSiteDetail'])
            writer.writerows(self.data)

    def run(self, ken_name, suikei_name, komoku_name):
        ken_code = self.ken_values.get(ken_name, '-1')
        suikei_code = self.suikei_values.get(suikei_name, '-1')
        komoku_code = self.komoku_values.get(komoku_name, '-1')
        
        self.scrape_data(ken_code, suikei_code, komoku_code)
        self.save_to_csv(f'river_data_{ken_name}_{suikei_name}_{komoku_name}.csv')

    def increment_page(self):
        self.page_number += 1

    def decrement_page(self):
        if self.page_number > 0:
            self.page_number -= 1

    def reset_page_number(self):
        self.page_number = 0