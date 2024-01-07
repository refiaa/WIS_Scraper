import sys
import datetime
import json
import re
import requests
import markdown

from functools import lru_cache
from PyQt5.QtWidgets import (
                            QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                            QTableWidget, QTableWidgetItem, QTextEdit, QSplitter, QLineEdit,
                            QLabel, QComboBox, QMessageBox, QTabWidget, QTabBar, 
                            QDialog, QGroupBox, QSizePolicy
                            )
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QUrl
from PyQt5.QtGui import QColor, QPixmap, QDesktopServices

from getWISInfo import RiverDataScraper
from getDetailInfo import DetailInfoScraper, MapImageScraper, SiteHtmlChecker
from getObservedInfo import ObservedInfoScraper
from WIS_DetailInfoWindow import DetailInfoWindow  

class CrawlerThread(QThread):
    dataFetched = pyqtSignal(list, bool)
    updateLog = pyqtSignal(str)

    def __init__(self, ken_code, suikei_code, komoku_code, scraper):
        super().__init__()
        self.ken_code = ken_code
        self.suikei_code = suikei_code
        self.komoku_code = komoku_code
        self.scraper = scraper

    def run(self):
        try:
            if not self.is_server_connected():
                self.updateLog.emit("ERROR - Unable to Connect to the Server")
                return

            self.updateLog.emit("INFO - Connected Successfully to the Server")

            start_time = datetime.datetime.now()
            self.updateLog.emit(f"INFO - Data request at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

            self.scraper.scrape_data(self.ken_code, self.suikei_code, self.komoku_code)
            data_empty = len(self.scraper.data) == 0
            self.dataFetched.emit(self.scraper.data, data_empty) 

            end_time = datetime.datetime.now()
            self.updateLog.emit(f"INFO - Ended at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            self.updateLog.emit(f"INFO - Exited with : {(end_time - start_time)}")

        except Exception as e:
            self.updateLog.emit(f"ERROR - Data Fetching Failed: {e}")

    def is_server_connected(self):
        try:
            response = requests.get("http://www1.river.go.jp", timeout=5)
            return True if response.status_code == 200 else False
        
        except requests.ConnectionError:
            return False
        
class DetailCrawlerThread(QThread):
    detailFetched = pyqtSignal(dict, str)

    def __init__(self, js_detail, river_name):
        super().__init__()
        self.js_detail = js_detail
        self.river_name = river_name

    def run(self):
        scraper = DetailInfoScraper(self.js_detail)
        data = scraper.scrape()
        self.detailFetched.emit(data, self.river_name)

class ObservedInfoCrawlerThread(QThread):
    observedInfoFetched = pyqtSignal(list)

    def __init__(self, js_detail):
        super().__init__()
        self.js_detail = js_detail

    def run(self):
        scraper = ObservedInfoScraper(self.js_detail)
        data = scraper.scrape()
        self.observedInfoFetched.emit(data)

class LegalNoticeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Legal Notice")
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        with open('OPEN_SOURCE_LICENSES.md', 'r') as file:
            license_text = file.read()
            html_text = markdown.markdown(license_text)

        licenseLabel = QTextEdit()
        licenseLabel.setReadOnly(True)
        licenseLabel.setFontFamily("monospace")
        licenseLabel.setHtml(html_text)
        
        layout.addWidget(licenseLabel)

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Water Information System Info Viewer'
        self.left = 100
        self.top = 100
        self.width = 700
        self.height = 650
        self.searchResults = []  
        self.searchIndex = -1 
        self.logViewer = QTextEdit()
        self.logViewer.setMinimumHeight(int(self.height * 0.25))
        self.scraper = RiverDataScraper("http://www1.river.go.jp/cgi-bin/SrchSite.exe", 
                                        "./json/ken_values.json", "./json/suikei_values.json", "./json/komoku_values.json")
        self.version = self.read_version_file()

        self.pageNumberLabel = QLabel("1")

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.tabWidget = QTabWidget()
        self.createCrawlingTab()

        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(self.tabWidget)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.tabWidget)

        logAndBottomTextContainer = QWidget()
        logAndBottomTextLayout = QVBoxLayout(logAndBottomTextContainer)

        logAndBottomTextLayout.addWidget(self.logViewer)

        bottomTextLayout = QHBoxLayout()

        leftLayout = QHBoxLayout()
        
        textLabel = QLabel('Copyright (c) 2023-2024 <a href="https://github.com/refiaa">Refiaa</a>')
        textLabel.setOpenExternalLinks(False)
        textLabel.linkActivated.connect(self.onTextLabelLinkClicked)

        legalNoticeButton = QPushButton("Legal Notice")
        legalNoticeButton.clicked.connect(self.openLegalNoticeDialog)

        legalNoticeButton.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                text-decoration: underline;
            }
            QPushButton:pressed {
                color: red;
            }
        """)

        leftLayout.addWidget(textLabel)
        leftLayout.addWidget(legalNoticeButton)

        rightLayout = QHBoxLayout()
        rightTextLabel = QLabel(f"{self.version}")
        rightLayout.addWidget(rightTextLabel)

        bottomTextLayout.addLayout(leftLayout)
        bottomTextLayout.addStretch(1) 
        bottomTextLayout.addLayout(rightLayout)

        logAndBottomTextLayout.addLayout(bottomTextLayout)

        splitter.addWidget(logAndBottomTextContainer)

        splitter.setSizes([int(self.height * 0.77), int(self.height * 0.23)])

        mainLayout.addWidget(splitter)

        self.setLayout(mainLayout)
        self.show()
        
    def addCrawlingComponents(self, layout):
        self.kenComboBox = QComboBox()
        self.suikeiComboBox = QComboBox()
        self.komokuComboBox = QComboBox()
        
        self.loadComboBoxData() 

        layout.addWidget(self.kenComboBox)
        layout.addWidget(self.suikeiComboBox)
        layout.addWidget(self.komokuComboBox) 

        self.startButton = QPushButton('実行')
        self.startButton.clicked.connect(self.on_start_button_clicked)
        self.startButton.setFixedWidth(60)
        layout.addWidget(self.startButton)

        self.resetSearchButton = QPushButton('クリア')
        self.resetSearchButton.clicked.connect(self.reset_search)
        self.resetSearchButton.setFixedWidth(60)
        layout.addWidget(self.resetSearchButton)

        rightLayout = QHBoxLayout()

        databaseButton = QPushButton("水文水質データベース")
        databaseButton.clicked.connect(self.openDatabaseLink)

        databaseButton.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                text-decoration: underline;
            }
            QPushButton:pressed {
                color: red;
            }
        """)

        rightLayout.addWidget(databaseButton)

        layout.addStretch(1)
        layout.addLayout(rightLayout)

    def createCrawlingTab(self):
        crawlingTab = QWidget()
        layout = QVBoxLayout(crawlingTab)

        topLayout = QHBoxLayout()
        self.addCrawlingComponents(topLayout)
        layout.addLayout(topLayout)

        splitter = QSplitter(Qt.Vertical)

        outputContainer = QWidget()
        outputLayout = QHBoxLayout(outputContainer)
        self.addCrawlingTableAndLog(outputLayout)

        splitter.addWidget(outputContainer)

        bottomLayout = QHBoxLayout()

        searchLayout = QHBoxLayout()

        self.searchField = QLineEdit()
        self.searchField.setPlaceholderText("ページ内検索...")
        searchLayout.addWidget(self.searchField)

        self.searchButton = QPushButton('検索')
        self.searchButton.clicked.connect(self.on_search)
        self.searchButton.setFixedWidth(60)
        searchLayout.addWidget(self.searchButton)

        self.prevButton = QPushButton('<')
        self.prevButton.clicked.connect(self.on_prev_search)
        self.prevButton.setFixedWidth(25)
        searchLayout.addWidget(self.prevButton)

        self.nextButton = QPushButton('>')
        self.nextButton.clicked.connect(self.on_next_search)
        self.nextButton.setFixedWidth(25)
        searchLayout.addWidget(self.nextButton)

        self.clearSearchButton = QPushButton('X')
        self.clearSearchButton.clicked.connect(self.clear_search)
        self.clearSearchButton.setFixedWidth(25)
        searchLayout.addWidget(self.clearSearchButton)

        self.searchCountLabel = QLabel('')
        searchLayout.addWidget(self.searchCountLabel)
        
        bottomLayout.addLayout(searchLayout)
        bottomLayout.addStretch(1)

        pageNumberContainer = QWidget()
        pageNumberContainerLayout = QVBoxLayout()

        self.pageNumberLabel = QLabel("1")

        pageNumberContainerLayout.addWidget(self.pageNumberLabel)
        pageNumberContainer.setLayout(pageNumberContainerLayout)
        pageNumberContainer.setStyleSheet("background-color: white;")

        bottomLayout.addWidget(pageNumberContainer)

        prev_page = QPushButton('前')
        prev_page.setFixedWidth(40)

        next_page = QPushButton('次')
        next_page.setFixedWidth(40)

        prev_page.clicked.connect(self.on_prev_page)
        next_page.clicked.connect(self.on_next_page)

        bottomLayout.addWidget(prev_page)
        bottomLayout.addWidget(next_page)

        bottomContainer = QWidget()
        bottomContainer.setLayout(bottomLayout)
        bottomContainer.setFixedHeight(50)
        splitter.addWidget(bottomContainer)

        self.logViewer = QTextEdit()
        self.logViewer.setReadOnly(True)
        splitter.addWidget(self.logViewer)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)
        self.tabWidget.addTab(crawlingTab, "WIS Info Searcher")

    def addCrawlingTableAndLog(self, layout):
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(['項目', '水系名', '河川名', '観測所名', '所在地', '詳細'])
        layout.addWidget(self.tableWidget) 

    def loadComboBoxData(self):
        self.kenData = self.loadJsonData('./json/ken_values.json')
        for ken in self.kenData:
            self.kenComboBox.addItem(ken)

        self.suikeiData = self.loadJsonData('./json/suikei_values.json')
        for suikei in self.suikeiData:
            self.suikeiComboBox.addItem(suikei)

        self.komokuData = self.loadJsonData('./json/komoku_values.json')
        for komoku in self.komokuData:
            self.komokuComboBox.addItem(komoku) 

    @staticmethod
    @lru_cache(maxsize=128)
    def loadJsonData(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def on_click(self):
        selected_ken = self.kenComboBox.currentText()
        selected_suikei = self.suikeiComboBox.currentText()
        selected_komoku = self.komokuComboBox.currentText()
        ken_code = self.kenData[selected_ken]
        suikei_code = self.suikeiData[selected_suikei]
        komoku_code = self.komokuData[selected_komoku] 
        
        self.crawlerThread = CrawlerThread(ken_code, suikei_code, komoku_code, self.scraper)
        self.crawlerThread.dataFetched.connect(self.updateTable)
        self.crawlerThread.updateLog.connect(self.updateLog)
        self.crawlerThread.start()

    def updateTable(self, data, data_empty):
        if data_empty:
            QMessageBox.information(self, "No Data", "データが存在しません")
            if self.scraper.page_number > 0:
                self.scraper.decrement_page()
                self.update_page_number_label()
                self.on_click()
            return

        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(['項目', '水系名', '河川名', '観測所名', '所在地', '詳細'])

        row_count = 0
        valid_data_found = False

        for row_data in data:
            javascript_detail = row_data[7] if len(row_data) > 7 else None

            if javascript_detail and any(row_data[1:6]):
                valid_data_found = True
                self.tableWidget.insertRow(row_count)
                for j in range(1, 6):
                    item = QTableWidgetItem(str(row_data[j]))
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.tableWidget.setItem(row_count, j - 1, item)

                btn = QPushButton('詳細情報')
                btn.clicked.connect(lambda checked, js_detail=javascript_detail: self.onDetailButtonClicked(js_detail))
                self.tableWidget.setCellWidget(row_count, 5, btn)
                row_count += 1

        if not valid_data_found:
            QMessageBox.information(self, "No Data", "データが存在しません")
            if self.scraper.page_number > 0:
                self.scraper.decrement_page()
                self.update_page_number_label()
                self.on_click()


    def onDetailButtonClicked(self, javascript_detail):
        execute_time = datetime.datetime.now()
        current_row = self.tableWidget.currentRow()
        river_name_item = self.tableWidget.item(current_row, 2)
        river_name = river_name_item.text() if river_name_item else "Unknown"
        observation_site_name_item = self.tableWidget.item(current_row, 3)
        observation_site_name = observation_site_name_item.text() if observation_site_name_item else "Unknown"

        tabTitle = f"詳細情報 - {river_name} ({observation_site_name})"
        self.updateLog(f"INFO - Access to {river_name} ({observation_site_name}) at: {execute_time.strftime('%Y-%m-%d %H:%M:%S')} ")

        for i in range(self.tabWidget.count()):
            if self.tabWidget.tabText(i) == tabTitle:
                self.tabWidget.setCurrentIndex(i)
                return

        detailTab = QWidget()
        detailLayout = QVBoxLayout(detailTab)

        detailViewer = QTextEdit()
        detailViewer.setReadOnly(True)

        self.detailCrawlerThread = DetailCrawlerThread(javascript_detail, river_name)
        self.detailCrawlerThread.detailFetched.connect(lambda data, _: self.displayDetailData(data, detailViewer))
        self.detailCrawlerThread.start()

        self.observedInfoCrawlerThread = ObservedInfoCrawlerThread(javascript_detail)
        self.observedInfoCrawlerThread.observedInfoFetched.connect(lambda data: self.displayObservedInfo(data, javascript_detail))
        self.observedInfoCrawlerThread.start()

        detailLayout.addWidget(detailViewer)

        index = self.tabWidget.addTab(detailTab, tabTitle)

        tabCloseButton = QPushButton(' ✕')
        tabCloseButton.setStyleSheet("background-color: transparent; border: none; padding: 0px; font-size: 10pt;")
        tabCloseButton.clicked.connect(lambda: self.closeTab(tabTitle))
        self.tabWidget.tabBar().setTabButton(index, QTabBar.RightSide, tabCloseButton)

        self.tabWidget.setCurrentIndex(index)

    def displayDetailData(self, data, detailViewer):
        formatted_data = "<table border='1' cellspacing='0' cellpadding='5'>"
        for key, value in data.items():
            formatted_data += f"<tr><td><b>{key}</b></td><td>{value}</td></tr>"
        formatted_data += "</table>"

        javascript_detail = data.get('観測所記号', '')
        checker = SiteHtmlChecker(javascript_detail)
        has_image = checker.check_for_image()

        imageGroupBox = QGroupBox("位置図")
        imageLayout = QVBoxLayout()
        
        image_label = QLabel()
        pixmap = QPixmap()

        if has_image:
            coord_string = data.get('緯度経度', '')
            latitude, longitude = self.extractCoords(coord_string)
            map_image_scraper = MapImageScraper(javascript_detail, latitude, longitude)
            image_url = map_image_scraper.scrape_image_url()
        else:
            image_url = "./img/noImage.png"

        image_label = QLabel()
        pixmap = QPixmap()

        desired_width = 400  
        desired_height = 300 

        if has_image:
            response = requests.get(image_url)
            if response.status_code == 200:
                pixmap.loadFromData(response.content)
                pixmap = pixmap.scaled(QSize(desired_width, desired_height), Qt.KeepAspectRatio)
        else:
            pixmap.load(image_url)
            pixmap = pixmap.scaled(QSize(desired_width, desired_height), Qt.KeepAspectRatio)

        image_label.setPixmap(pixmap)
        imageLayout.addWidget(image_label)
        imageGroupBox.setLayout(imageLayout)

        layout = QVBoxLayout()
        layout.addWidget(imageGroupBox)
        layout.addWidget(QLabel(formatted_data))

        detailViewer.setLayout(layout)

    @staticmethod
    def extractCoords(coord_string):
        degrees = [int(match) for match in re.findall(r'(\d+)度', coord_string)]
        minutes = [int(match) for match in re.findall(r'(\d+)分', coord_string)]
        seconds = [int(match) for match in re.findall(r'(\d+)秒', coord_string)]

        latitude = f"{str(degrees[0]).zfill(3)}{str(minutes[0]).zfill(2)}{str(seconds[0]).zfill(2)}000"
        longitude = f"{str(degrees[1]).zfill(3)}{str(minutes[1]).zfill(2)}{str(seconds[1]).zfill(2)}000"

        return latitude, longitude

    def displayObservedInfo(self, data, javascript_detail):
        currentTabIndex = self.tabWidget.currentIndex()
        currentTab = self.tabWidget.widget(currentTabIndex)

        splitter = QSplitter()

        detailViewer = currentTab.layout().itemAt(0).widget()

        observedInfoTable = QTableWidget()
        observedInfoTable.setColumnCount(2)
        observedInfoTable.setHorizontalHeaderLabels(['観測情報名', '詳細観測情報'])
        observedInfoTable.setRowCount(len(data))

        observedInfoTable.setColumnWidth(0, 150)
        observedInfoTable.setColumnWidth(1, 100)

        for i, item in enumerate(data):
            keyItem = QTableWidgetItem(item)
            keyItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            keyItem.setTextAlignment(Qt.AlignCenter)
            observedInfoTable.setItem(i, 0, keyItem)
            testButton = QPushButton('観測情報')

            testButton.clicked.connect(lambda checked, key=item, js_detail=javascript_detail: self.onStatusButtonClicked(key, js_detail))
            observedInfoTable.setCellWidget(i, 1, testButton)
            
        splitter.addWidget(detailViewer)
        splitter.addWidget(observedInfoTable)

        splitter.setSizes([int(self.width * 0.5), int(self.width * 0.5)])
        splitter.setHandleWidth(0)

        currentTab.layout().addWidget(splitter)

    def onStatusButtonClicked(self, key, javascript_detail):
        dialog = DetailInfoWindow(self, key, javascript_detail)
        dialog.exec_()

    def reset_search(self):
        execute_time = datetime.datetime.now()

        self.searchField.clear()
        self.tableWidget.setRowCount(0)
        self.searchResults = []
        self.update_search_count()

        self.updateLog(f"INFO - Table Reset at: {execute_time.strftime('%Y-%m-%d %H:%M:%S')} ")

    def closeTab(self, tabTitle):
        for i in range(self.tabWidget.count()):
            if self.tabWidget.tabText(i) == tabTitle:
                widget = self.tabWidget.widget(i)
                self.tabWidget.removeTab(i)
                widget.deleteLater()

    def closeTabByTitle(self, tabTitle):
        for i in range(self.tabWidget.count()):
            if self.tabWidget.tabText(i) == tabTitle:
                self.tabWidget.removeTab(i)
                break

    def updateLog(self, message):
        self.logViewer.append(message)

    def on_search(self):
        search_text = self.searchField.text().lower()
        if not search_text:
            return

        self.searchResults = []
        self.searchIndex = -1
        match_found = False

        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                if column == 5:
                    continue
                item = self.tableWidget.item(row, column)
                if item and search_text in item.text().lower():
                    self.searchResults.append((row, column))
                    item.setBackground(QColor('yellow'))
                    match_found = True
                elif item:
                    item.setBackground(QColor('white'))

        if not match_found:
            QMessageBox.information(self, "No Results", "一致なし")
        else:
            self.jump_to_first_search_result()

        self.update_search_count()

    def jump_to_first_search_result(self):
        if self.searchResults:
            self.searchIndex = 0
            self.highlight_search_result()

    def on_prev_search(self):
        if self.searchResults and self.searchIndex > 0:
            self.searchIndex -= 1
            self.highlight_search_result()

    def on_next_search(self):
        if self.searchResults and self.searchIndex < len(self.searchResults) - 1:
            self.searchIndex += 1
            self.highlight_search_result()

    def highlight_search_result(self):
        for row, column in self.searchResults:
            self.tableWidget.item(row, column).setBackground(QColor('white'))

        row, column = self.searchResults[self.searchIndex]
        
        self.tableWidget.item(row, column).setBackground(QColor('yellow'))
        self.tableWidget.scrollToItem(self.tableWidget.item(row, column))
        self.update_search_count()

    def update_search_count(self):
        if self.searchResults:
            self.searchCountLabel.setText(f"{self.searchIndex + 1}/{len(self.searchResults)}")
        else:
            self.searchCountLabel.setText("")

    def clear_search(self):
        self.searchField.clear()
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item:
                    item.setBackground(QColor('white'))
        self.searchResults = []
        self.update_search_count()

    def on_prev_page(self):
        self.scraper.decrement_page()
        self.update_page_number_label()
        self.reset_search()

        self.on_click()

    def on_next_page(self):
        self.scraper.increment_page()
        self.update_page_number_label()
        self.reset_search()

        self.on_click()

    def on_start_button_clicked(self):
        self.scraper.reset_page_number()
        self.update_page_number_label()

        self.on_click()

    def decrement_page_and_reload(self):
        if self.scraper.page_number > 0:
            self.scraper.decrement_page()
            self.update_page_number_label()
            self.on_click()

    def update_page_number_label(self):
        self.pageNumberLabel.setText(f"{self.scraper.page_number + 1}")

    def openLegalNoticeDialog(self):
        dialog = LegalNoticeDialog(self)
        dialog.exec_()

    def openDatabaseLink(self):
        reply = QMessageBox.question(self, '外部リンク', 
                                    "外部のウェブサイトに移動します",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            QDesktopServices.openUrl(QUrl("http://www1.river.go.jp"))

    def onTextLabelLinkClicked(self, link):
        reply = QMessageBox.question(self, '外部リンク', 
                                    "外部のウェブサイトに移動します",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            QDesktopServices.openUrl(QUrl(link))

    def read_version_file(self):

        with open('VERSION', 'r') as file:
            return file.read().strip()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    
    sys.exit(app.exec_())
