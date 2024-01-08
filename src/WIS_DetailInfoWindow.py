from PyQt5.QtWidgets import (
                            QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QLineEdit, QPushButton, QLabel, 
                            QHeaderView, QMessageBox
                            )
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from SrchRainData import SrchRainData_1, SrchRainData_2, SrchRainData_3, SrchRainData_4
from getObservationInfo import ObservationDataMatcher

# SrchRainData3のデータ処理プロセス
# process_data → handle_rain_data → handle_specific_data → SrchRainData_3クラスに移動
#                                 → add_date_input_fields_3 → add_date_input_fields_3 → on_confirm_clicked_3

def date_input_decorator(input_type):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            self.date_input_layout = QHBoxLayout()

            self.start_input = QLineEdit()
            self.end_input = QLineEdit()
            if input_type == 'year':
                self.start_input.setPlaceholderText("Init Year")
                self.end_input.setPlaceholderText("End Year")
            
            # input_type == 'date'
            else:  
                self.start_input.setPlaceholderText("Init Date (YYYY/MM)")
                self.end_input.setPlaceholderText("End Date (YYYY/MM)")

            self.date_input_layout.addWidget(self.start_input)
            self.date_input_layout.addWidget(self.end_input)

            self.confirm_button = QPushButton("Download Data")
            self.confirm_button.clicked.connect(lambda: func(self, *args, **kwargs))
            self.date_input_layout.addWidget(self.confirm_button)

            self.additional_container.addLayout(self.date_input_layout)
        return wrapper
    return decorator

class DetailInfoWindow(QDialog):
    def __init__(self, parent=None, name=None, js_detail=None):
        super().__init__(parent)
        self.name = name
        self.js_detail = js_detail
        self.valid_start_year = None
        self.valid_end_year = None
        self.start_month = None
        self.end_month = None

        self.initUI()
        self.process_data()

    def initUI(self):
        self.setWindowTitle(f"{self.name}-観測情報")
        self.setGeometry(300, 300, 560, 400)

        self.main_layout = QVBoxLayout(self)
        self.header_layout = QHBoxLayout()
        self.additional_container = QVBoxLayout()
        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addLayout(self.additional_container)

    # data_typeの処理
    def process_data(self):
        matcher = ObservationDataMatcher(self.js_detail, self.name)
        is_name_present, kind_value = matcher.check_name_in_page()
        data_type_code = matcher.check_data_type()

        data_type = self.get_data_type(data_type_code)
        kind_value_int = int(kind_value)

        # SrchRainDataの処理　
        # handle_rain_dataに移動
        if data_type == 'SrchRainData':
            self.handle_rain_data(kind_value_int) # SrchRainDataの時だけhandle_rain_dataに移動
        else:
            self.display_message("Not Supported Yet")

    # SrchRainDataのデータ処理、
    # process_dataから移動、handle_specific_dataに移動
    def handle_rain_data(self, kind_value_int):
        if kind_value_int == 1:
            self.handle_specific_data(SrchRainData_1, kind_value_int, self.valid_start_year, self.start_month, self.valid_end_year, self.end_month)
            self.add_date_input_fields_1()
            
        elif kind_value_int == 2:
            self.handle_specific_data(SrchRainData_2, kind_value_int, self.valid_start_year, self.start_month, self.valid_end_year, self.end_month)
            self.add_date_input_fields_2()
        
        elif kind_value_int == 3:
            self.handle_specific_data(SrchRainData_3, kind_value_int, self.valid_start_year, self.valid_end_year)
            self.add_date_input_fields_3()
        
        elif kind_value_int == 4:
            self.handle_specific_data(SrchRainData_4, kind_value_int, self.valid_start_year, self.valid_end_year)
            self.add_date_input_fields_4()

    # start_yearやend_yearなどのDataClassにより異なるロジックを処理
    # handle_rain_dataから移動

    def handle_specific_data(self, DataClass, kind_value_int, start_year=None, end_year=None, start_month=None, end_month=None):
        # SrchRainData_3の場合のみ、start_year, end_yearを処理
        # 別のデータにおいては別のデータ処理プロセスを追加

        if DataClass == SrchRainData_1:
            data_handler = DataClass(self.js_detail, kind_value_int, start_year, start_month, end_year, end_month)
        
        elif DataClass == SrchRainData_2:
            data_handler = DataClass(self.js_detail, kind_value_int, start_year, start_month, end_year, end_month)
        
        elif DataClass == SrchRainData_3:
            data_handler = DataClass(self.js_detail, kind_value_int, start_year, end_year)

        elif DataClass == SrchRainData_4:
            data_handler = DataClass(self.js_detail, kind_value_int, start_year, end_year)
        
        else:
            data_handler = DataClass(self.js_detail, kind_value_int)

        header_value = data_handler.fetch_header_value()
        self.display_header_value(header_value)

        table_data = data_handler.fetch_table_data()
        self.display_table_data(table_data)

        station_data = data_handler.fetch_station_data()
        self.display_station_data(station_data)

    def display_station_data(self, station_data):
        if not station_data:
            self.display_message("Station data not available")
            return

        self.station_layout = QVBoxLayout()

        for key, value in station_data.items():
            label = self.create_label(f"{key}: {value}", 10, QFont.Normal)
            self.station_layout.addWidget(label)

        self.main_layout.insertLayout(1, self.station_layout)

    # tableデータを表示
    def display_table_data(self, table_data):
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(10)
        self.table_widget.setHorizontalHeaderLabels([str(i) for i in range(10)])
        self.table_widget.verticalHeader().setVisible(True)

        table_dict = self.prepare_table_dict(table_data)
        self.table_widget.setRowCount(len(table_dict))

        # tableデータの動的処理やレイアウトサイズ決定
        total_height = self.table_widget.horizontalHeader().height()
        for i, (decade, statuses) in enumerate(table_dict.items()):
            for j, status in enumerate(statuses):
                item = QTableWidgetItem()
                if status == 'ari':
                    item.setBackground(QColor(255, 255, 0))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table_widget.setItem(i, j, item)

            header_item = QTableWidgetItem(decade)
            header_item.setFlags(header_item.flags() & ~Qt.ItemIsEditable)
            self.table_widget.setVerticalHeaderItem(i, header_item)
            total_height += self.table_widget.rowHeight(i)

        layout_height = total_height + 5
        self.table_widget.setFixedHeight(layout_height)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.additional_container.addWidget(self.table_widget)
        self.additional_container.addStretch(1)

    # date tableのための事前処理
    def prepare_table_dict(self, table_data):
        table_dict = {}
        for data in table_data:
            year, status = data.split(' - ')
            decade = year[:-1]
            if decade not in table_dict:
                table_dict[decade] = ['nashi'] * 10
            table_dict[decade][int(year[-1])] = status
        return table_dict

    # header表示
    def display_message(self, message):
        message_label = self.create_label(message, 12, QFont.Bold)
        self.header_layout.addWidget(message_label)

    def display_header_value(self, header_value):
        header_value_label = self.create_label(header_value, 12, QFont.Bold)
        header_value_label.setStyleSheet("""
            QLabel {
                color: black;
                font-family: Arial;
                font-size: 20pt;
            }
        """)
        self.header_layout.addWidget(header_value_label)

    # lable生成
    def create_label(self, text, font_size, font_weight):
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", font_size, font_weight))
        return label

    # data_type_codeからdata typeの確認
    def get_data_type(self, data_type_code):
        data_type_mapping = {
            0: 'SrchRainData',
            1: 'SrchWaterData',
            2: 'SrchWquaData',
            3: 'SrchUWaterData',
            4: 'SrchDamData',
            5: 'SrchKaisyoData',
            6: 'SrchSnowData'
        }
        return data_type_mapping.get(data_type_code, 'UnknownData')

############################################ SrchRainData_1に関するロジック ############################################

    @date_input_decorator(input_type='date')
    def add_date_input_fields_1(self):
        self.confirm_button.clicked.disconnect()
        self.confirm_button.clicked.connect(self.on_confirm_clicked_1)

    def on_confirm_clicked_1(self):
        start_date_str = self.start_input.text()
        end_date_str = self.end_input.text()

        if not all(char.isdigit() or char == '/' for char in start_date_str + end_date_str):
            QMessageBox.warning(self, "警告", "Invalid input")
            return

        try:
            start_year, start_month = map(int, start_date_str.split('/'))
            end_year, end_month = map(int, end_date_str.split('/'))

            if not (1 <= start_month <= 12) or not (1 <= end_month <= 12):
                QMessageBox.warning(self, "警告", "Invalid Month")
                return

            if start_year > end_year or (start_year == end_year and start_month > end_month):
                QMessageBox.warning(self, "警告", "Invalid range")
                return

            self.valid_start_year = start_year
            self.start_month = start_month
            self.valid_end_year = end_year
            self.end_month = end_month

            temp_data_handler = SrchRainData_1(self.js_detail, 1, start_year, start_month, end_year, end_month)
            filtered_years = temp_data_handler.filter_years()

            all_years_in_range = [str(year) for year in range(start_year, end_year + 1)]

            if not all(year in filtered_years for year in all_years_in_range):
                QMessageBox.warning(self, "警告", "Invalid range")
                return

            data_handler = SrchRainData_1(self.js_detail, 1, self.valid_start_year, self.start_month, self.valid_end_year, self.end_month)
            data_handler.scrape_data_for_months()

            QMessageBox.information(self, "Download Complete", "Data download completed successfully.")

        except ValueError:
            QMessageBox.warning(self, "警告", "Invalid Date Format")
            return

#######################################################################################################################

############################################ SrchRainData_2に関するロジック ############################################

    # 日付入力・現在はSrchRainData_2にだけ有効、YYYY/MMで入力してもらい、on_confirm_clicked_2で日付の分離を実行

    @date_input_decorator(input_type='date')
    def add_date_input_fields_2(self):
        self.confirm_button.clicked.disconnect()
        self.confirm_button.clicked.connect(self.on_confirm_clicked_2)

    def on_confirm_clicked_2(self):
        start_date_str = self.start_input.text()
        end_date_str = self.end_input.text()

        if not all(char.isdigit() or char == '/' for char in start_date_str + end_date_str):
            QMessageBox.warning(self, "警告", "Invalid input")
            return

        try:
            start_year, start_month = map(int, start_date_str.split('/'))
            end_year, end_month = map(int, end_date_str.split('/'))

            if not (1 <= start_month <= 12) or not (1 <= end_month <= 12):
                QMessageBox.warning(self, "警告", "Invalid Month")
                return

            if start_year > end_year or (start_year == end_year and start_month > end_month):
                QMessageBox.warning(self, "警告", "Invalid range")
                return

            self.valid_start_year = start_year
            self.start_month = start_month
            self.valid_end_year = end_year
            self.end_month = end_month

            temp_data_handler = SrchRainData_2(self.js_detail, 2, start_year, start_month, end_year, end_month)
            filtered_years = temp_data_handler.filter_years()

            all_years_in_range = [str(year) for year in range(start_year, end_year + 1)]

            if not all(year in filtered_years for year in all_years_in_range):
                QMessageBox.warning(self, "警告", "Invalid range")
                return

            data_handler = SrchRainData_2(self.js_detail, 2, self.valid_start_year, self.start_month, self.valid_end_year, self.end_month)
            data_handler.scrape_data_for_months()

            QMessageBox.information(self, "Download Complete", "Data download completed successfully.")

        except ValueError:
            QMessageBox.warning(self, "警告", "Invalid Date Format")
            return

#######################################################################################################################

############################################ SrchRainData_3に関するロジック ############################################

    @date_input_decorator(input_type='year')
    def add_date_input_fields_3(self):
        self.confirm_button.clicked.disconnect()
        self.confirm_button.clicked.connect(self.on_confirm_clicked_3)
    
    def on_confirm_clicked_3(self):
        start_year_str = self.start_input.text()
        end_year_str = self.end_input.text()

        if not start_year_str.isdigit() or not end_year_str.isdigit():
            QMessageBox.warning(self, "警告", "Invalid input")
            return

        start_year = int(start_year_str)
        end_year = int(end_year_str)

        if start_year > end_year:
            QMessageBox.warning(self, "警告", "Invalid range")
            return

        self.valid_start_year = start_year
        self.valid_end_year = end_year

        temp_data_handler = SrchRainData_3(self.js_detail, 3, start_year, end_year)
        filtered_years = temp_data_handler.filter_years()

        all_years_in_range = [str(year) for year in range(start_year, end_year + 1)]

        if not all(year in filtered_years for year in all_years_in_range):
            QMessageBox.warning(self, "警告", "Invalid range")
            return

        data_handler = SrchRainData_3(self.js_detail, 3, start_year, end_year)
        data_handler.scrape_data_for_years()

        QMessageBox.information(self, "Download Complete", "Data download completed successfully.")

#######################################################################################################################

############################################ SrchRainData_4に関するロジック ############################################

    @date_input_decorator(input_type='year')
    def add_date_input_fields_4(self):
        self.confirm_button.clicked.disconnect()
        self.confirm_button.clicked.connect(self.on_confirm_clicked_4)

    def on_confirm_clicked_4(self):
        start_year_str = self.start_input.text()
        end_year_str = self.end_input.text()

        if not start_year_str.isdigit() or not end_year_str.isdigit():
            QMessageBox.warning(self, "警告", "Invalid range")
            return

        start_year = int(start_year_str)
        end_year = int(end_year_str)

        temp_data_handler = SrchRainData_4(self.js_detail, 4, start_year, end_year)
        filtered_years = temp_data_handler.filter_years()

        all_years_in_range = [str(year) for year in range(start_year, end_year + 1)]

        if not all(year in filtered_years for year in all_years_in_range):
            QMessageBox.warning(self, "警告", "Invalid range")
            return

        data_handler = SrchRainData_4(self.js_detail, 4, start_year, end_year)
        data_handler.scrape_data_for_period()

        QMessageBox.information(self, "Download Complete", "Data download completed successfully.")

#######################################################################################################################

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    ex = DetailInfoWindow(name="Example", js_detail="Example")
    ex.show()
    
    sys.exit(app.exec_())
