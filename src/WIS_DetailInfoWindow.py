from PyQt5.QtWidgets import (
                            QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QLineEdit, QPushButton, QLabel, 
                            QHeaderView, QMessageBox
                            )
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from SrchRainData import SrchRainData_1, SrchRainData_2, SrchRainData_3, SrchRainData_4
from SrchWaterData import SrchWaterData_1, SrchWaterData_2, SrchWaterData_3, SrchWaterData_4, SrchWaterData_5, SrchWaterData_6, SrchWaterData_7, SrchWaterData_8

from getObservationInfo import ObservationDataMatcher
from decorators import date_input, data_confirm, data_type_decorator

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

# ============================ 共通関数 ============================== #

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

    # dataの実際の配列での有効範囲検証
    def validate_years_range(self, data_handler_class, kind_value, start_year, end_year):
        data_handler = data_handler_class(self.js_detail, kind_value, start_year, end_year)
        filtered_years = data_handler.filter_years()

        all_years_in_range = [str(year) for year in range(start_year, end_year + 1)]
        if not all(year in filtered_years for year in all_years_in_range):
            QMessageBox.warning(self, "警告", "Invalid Data range")
            return False
        return True

    # data_typeの処理
    def process_data(self):
        matcher = ObservationDataMatcher(self.js_detail, self.name)
        is_name_present, kind_value = matcher.check_name_in_page()
        data_type_code = matcher.check_data_type()

        data_type = self.get_data_type(data_type_code)
        kind_value_int = int(kind_value)

        # SrchRainDataの処理　
        # handle_data_rainに移動
        if data_type == 'SrchRainData':
            self.handle_data_rain(kind_value_int) # SrchRainDataの時だけhandle_data_rainに移動

        elif data_type == 'SrchWaterData':
            self.handle_data_water(kind_value_int)

        else:
            self.display_message("Not Supported Yet")

# ========================= SrchWaterData Part ========================== #

    # this is not best way, which mean this code 'WIS_DetailInfoWindow.py hav to changed for DRY and SOLID Principle for program optimization
    # REFACTORING IS REQUIRED
    
    @data_type_decorator(data_type="water")
    def handle_data_water(self, kind_value_int, data_class_prefix):
        data_class = lambda x: globals()[f'{data_class_prefix}_{x}']
        
        if kind_value_int == 1:
            self.handle_specific_data_water(data_class(1), kind_value_int, self.valid_start_year, self.start_month, self.valid_end_year, self.end_month)
            self.add_date_input_fields_water_1()

        elif kind_value_int == 2:
            self.handle_specific_data_water(data_class(2), kind_value_int, self.valid_start_year, self.start_month, self.valid_end_year, self.end_month)
            self.add_date_input_fields_water_2()
        
        elif kind_value_int == 3:
            self.handle_specific_data_water(data_class(3), kind_value_int, self.valid_start_year, self.valid_end_year)
            self.add_date_input_fields_water_3()
        
        elif kind_value_int == 4:
            self.handle_specific_data_water(data_class(4), kind_value_int, self.valid_start_year, self.valid_end_year)
            self.add_date_input_fields_water_4()

        elif kind_value_int == 5:
            self.handle_specific_data_water(data_class(5), kind_value_int, self.valid_start_year, self.start_month, self.valid_end_year, self.end_month)
            self.add_date_input_fields_water_5()

        elif kind_value_int == 6:
            self.handle_specific_data_water(data_class(6), kind_value_int, self.valid_start_year, self.start_month, self.valid_end_year, self.end_month)
            self.add_date_input_fields_water_6()

        elif kind_value_int == 7:
            self.handle_specific_data_water(data_class(7), kind_value_int, self.valid_start_year, self.valid_end_year)
            self.add_date_input_fields_water_7()
        
        elif kind_value_int == 8:
            self.handle_specific_data_water(data_class(8), kind_value_int, self.valid_start_year, self.valid_end_year)
            self.add_date_input_fields_water_8()
        
        else:
            self.display_message("Not Supported Data Type")

    @data_type_decorator(data_type="water")
    def handle_specific_data_water(self, DataClass, kind_value_int, start_year=None, end_year=None, start_month=None, end_month=None, data_class_prefix=None):
        if DataClass == globals()[f'{data_class_prefix}_1']:
            data_handler = DataClass(self.js_detail, kind_value_int, start_year, start_month, end_year, end_month)

        elif DataClass == globals()[f'{data_class_prefix}_2']:
            data_handler = DataClass(self.js_detail, kind_value_int, start_year, start_month, end_year, end_month)
        
        elif DataClass == globals()[f'{data_class_prefix}_3']:
            data_handler = DataClass(self.js_detail, kind_value_int, start_year, end_year)
        
        elif DataClass == globals()[f'{data_class_prefix}_4']:
            data_handler = DataClass(self.js_detail, kind_value_int, start_year, end_year)

        elif DataClass == globals()[f'{data_class_prefix}_5']:
            data_handler = DataClass(self.js_detail, kind_value_int, start_year, start_month, end_year, end_month)

        elif DataClass == globals()[f'{data_class_prefix}_6']:
            data_handler = DataClass(self.js_detail, kind_value_int, start_year, start_month, end_year, end_month)

        elif DataClass == globals()[f'{data_class_prefix}_7']:
            data_handler = DataClass(self.js_detail, kind_value_int, start_year, end_year)

        elif DataClass == globals()[f'{data_class_prefix}_8']:
            data_handler = DataClass(self.js_detail, kind_value_int, start_year, end_year)
        
        else:
            self.display_message("Not Supported Data Type")
            return

        header_value = data_handler.fetch_header_value()
        self.display_header_value(header_value)

        table_data = data_handler.fetch_table_data()
        self.display_table_data(table_data)

        station_data = data_handler.fetch_station_data()
        self.display_station_data(station_data)

    # SrchwaterData_1
    @date_input(input_type='date')
    def add_date_input_fields_water_1(self):
        self.confirm_button.clicked.disconnect()
        self.confirm_button.clicked.connect(self.on_data_confirm_water_1)

    @data_confirm(data_type='date')
    def on_data_confirm_water_1(self, start_year, end_year, start_month, end_month):
        if not self.validate_years_range(SrchWaterData_1, 1, start_year, end_year):
            return
        
        data_handler = SrchWaterData_1(self.js_detail, 1, start_year, start_month, end_year, end_month)
        data_handler.scrape_data_for_months()

        QMessageBox.information(self, "Download Complete", "Data download completed successfully.")

    # SrchwaterData_2
    @date_input(input_type='date')
    def add_date_input_fields_water_2(self):
        self.confirm_button.clicked.disconnect()
        self.confirm_button.clicked.connect(self.on_data_confirm_water_2)

    @data_confirm(data_type='date')
    def on_data_confirm_water_2(self, start_year, end_year, start_month, end_month):
        if not self.validate_years_range(SrchWaterData_2, 2, start_year, end_year):
            return

        data_handler = SrchWaterData_2(self.js_detail, 2, start_year, start_month, end_year, end_month)
        data_handler.scrape_data_for_months()

        QMessageBox.information(self, "Download Complete", "Data download completed successfully.")

    # SrchwaterData_3
    @date_input(input_type='year')
    def add_date_input_fields_water_3(self):
        self.confirm_button.clicked.disconnect()
        self.confirm_button.clicked.connect(self.on_data_confirm_water_3)
    
    @data_confirm(data_type='year')
    def on_data_confirm_water_3(self, start_year, end_year, start_month=None, end_month=None):
        if not self.validate_years_range(SrchWaterData_3, 3, start_year, end_year):
            return

        data_handler = SrchWaterData_3(self.js_detail, 3, start_year, end_year)
        data_handler.scrape_data_for_years()

        QMessageBox.information(self, "Download Complete", "Data download completed successfully.")

    # SrchwaterData_4
    @date_input(input_type='year')
    def add_date_input_fields_water_4(self):
        self.confirm_button.clicked.disconnect()
        self.confirm_button.clicked.connect(self.on_data_confirm_water_4)

    @data_confirm(data_type='year')
    def on_data_confirm_water_4(self, start_year, end_year, start_month=None, end_month=None):
        if not self.validate_years_range(SrchWaterData_4, 4, start_year, end_year):
            return
        
        data_handler = SrchWaterData_4(self.js_detail, 4, start_year, end_year)
        data_handler.scrape_data_for_period()
        
        QMessageBox.information(self, "Download Complete", "Data download completed successfully.")

    # SrchwaterData_5
    @date_input(input_type='date')
    def add_date_input_fields_water_5(self):
        self.confirm_button.clicked.disconnect()
        self.confirm_button.clicked.connect(self.on_data_confirm_water_5)

    @data_confirm(data_type='date')
    def on_data_confirm_water_5(self, start_year, end_year, start_month, end_month):
        if not self.validate_years_range(SrchWaterData_5, 5, start_year, end_year):
            return
        
        data_handler = SrchWaterData_5(self.js_detail, 5, start_year, start_month, end_year, end_month)
        data_handler.scrape_data_for_months()

        QMessageBox.information(self, "Download Complete", "Data download completed successfully.")

    # SrchwaterData_6
    @date_input(input_type='date')
    def add_date_input_fields_water_6(self):
        self.confirm_button.clicked.disconnect()
        self.confirm_button.clicked.connect(self.on_data_confirm_water_6)

    @data_confirm(data_type='date')
    def on_data_confirm_water_6(self, start_year, end_year, start_month, end_month):
        if not self.validate_years_range(SrchWaterData_6, 6, start_year, end_year):
            return

        data_handler = SrchWaterData_6(self.js_detail, 6, start_year, start_month, end_year, end_month)
        data_handler.scrape_data_for_months()

        QMessageBox.information(self, "Download Complete", "Data download completed successfully.")

    # SrchwaterData_7
    @date_input(input_type='year')
    def add_date_input_fields_water_7(self):
        self.confirm_button.clicked.disconnect()
        self.confirm_button.clicked.connect(self.on_data_confirm_water_7)
    
    @data_confirm(data_type='year')
    def on_data_confirm_water_7(self, start_year, end_year, start_month=None, end_month=None):
        if not self.validate_years_range(SrchWaterData_7, 7, start_year, end_year):
            return

        data_handler = SrchWaterData_7(self.js_detail, 7, start_year, end_year)
        data_handler.scrape_data_for_years()

        QMessageBox.information(self, "Download Complete", "Data download completed successfully.")

    # SrchwaterData_8
    @date_input(input_type='year')
    def add_date_input_fields_water_8(self):
        self.confirm_button.clicked.disconnect()
        self.confirm_button.clicked.connect(self.on_data_confirm_water_8)

    @data_confirm(data_type='year')
    def on_data_confirm_water_8(self, start_year, end_year, start_month=None, end_month=None):
        if not self.validate_years_range(SrchWaterData_8, 8, start_year, end_year):
            return
        
        data_handler = SrchWaterData_8(self.js_detail, 8, start_year, end_year)
        data_handler.scrape_data_for_period()
        
        QMessageBox.information(self, "Download Complete", "Data download completed successfully.")

# ========================== SrchRainData Part ========================== #

    # SrchRainDataのデータ処理、
    # process_dataから移動、handle_specific_data_rainに移動
    @data_type_decorator(data_type="rain")
    def handle_data_rain(self, kind_value_int, data_class_prefix):
        data_class = lambda x: globals()[f'{data_class_prefix}_{x}']
        
        if kind_value_int == 1:
            self.handle_specific_data_rain(data_class(1), kind_value_int, self.valid_start_year, self.start_month, self.valid_end_year, self.end_month)
            self.add_date_input_fields_rain_1()

        elif kind_value_int == 2:
            self.handle_specific_data_rain(data_class(2), kind_value_int, self.valid_start_year, self.start_month, self.valid_end_year, self.end_month)
            self.add_date_input_fields_rain_2()
        
        elif kind_value_int == 3:
            self.handle_specific_data_rain(data_class(3), kind_value_int, self.valid_start_year, self.valid_end_year)
            self.add_date_input_fields_rain_3()
        
        elif kind_value_int == 4:
            self.handle_specific_data_rain(data_class(4), kind_value_int, self.valid_start_year, self.valid_end_year)
            self.add_date_input_fields_rain_4()

        else:
            self.display_message("Not Supported Data Type")
            return

    # start_yearやend_yearなどのDataClassにより異なるロジックを処理
    # handle_data_rainから移動

    @data_type_decorator(data_type="rain")
    def handle_specific_data_rain(self, DataClass, kind_value_int, start_year=None, end_year=None, start_month=None, end_month=None, data_class_prefix=None):
        if DataClass == globals()[f'{data_class_prefix}_1']:
            data_handler = DataClass(self.js_detail, kind_value_int, start_year, start_month, end_year, end_month)

        elif DataClass == globals()[f'{data_class_prefix}_2']:
            data_handler = DataClass(self.js_detail, kind_value_int, start_year, start_month, end_year, end_month)
        
        elif DataClass == globals()[f'{data_class_prefix}_3']:
            data_handler = DataClass(self.js_detail, kind_value_int, start_year, end_year)
        
        elif DataClass == globals()[f'{data_class_prefix}_4']:
            data_handler = DataClass(self.js_detail, kind_value_int, start_year, end_year)
        
        else:
            data_handler = DataClass(self.js_detail, kind_value_int)

        header_value = data_handler.fetch_header_value()
        self.display_header_value(header_value)

        table_data = data_handler.fetch_table_data()
        self.display_table_data(table_data)

        station_data = data_handler.fetch_station_data()
        self.display_station_data(station_data)

    # SrchRainData_1
    @date_input(input_type='date')
    def add_date_input_fields_rain_1(self):
        self.confirm_button.clicked.disconnect()
        self.confirm_button.clicked.connect(self.on_data_confirm_rain_1)

    @data_confirm(data_type='date')
    def on_data_confirm_rain_1(self, start_year, end_year, start_month, end_month):
        if not self.validate_years_range(SrchRainData_1, 1, start_year, end_year):
            return

        data_handler = SrchRainData_1(self.js_detail, 1, start_year, start_month, end_year, end_month)
        data_handler.scrape_data_for_months()

        QMessageBox.information(self, "Download Complete", "Data download completed successfully.")

    # SrchRainData_2
    @date_input(input_type='date')
    def add_date_input_fields_rain_2(self):
        self.confirm_button.clicked.disconnect()
        self.confirm_button.clicked.connect(self.on_data_confirm_rain_2)

    @data_confirm(data_type='date')
    def on_data_confirm_rain_2(self, start_year, end_year, start_month, end_month):
        if not self.validate_years_range(SrchRainData_2, 2, start_year, end_year):
            return
        
        data_handler = SrchRainData_2(self.js_detail, 2, start_year, start_month, end_year, end_month)
        data_handler.scrape_data_for_months()

        QMessageBox.information(self, "Download Complete", "Data download completed successfully.")

    # SrchRainData_3
    @date_input(input_type='year')
    def add_date_input_fields_rain_3(self):
        self.confirm_button.clicked.disconnect()
        self.confirm_button.clicked.connect(self.on_data_confirm_rain_3)
    
    @data_confirm(data_type='year')
    def on_data_confirm_rain_3(self, start_year, end_year, start_month=None, end_month=None):
        if not self.validate_years_range(SrchRainData_3, 3, start_year, end_year):
            return

        data_handler = SrchRainData_3(self.js_detail, 3, start_year, end_year)
        data_handler.scrape_data_for_years()

        QMessageBox.information(self, "Download Complete", "Data download completed successfully.")

    # SrchRainData_4
    @date_input(input_type='year')
    def add_date_input_fields_rain_4(self):
        self.confirm_button.clicked.disconnect()
        self.confirm_button.clicked.connect(self.on_data_confirm_rain_4)

    @data_confirm(data_type='year')
    def on_data_confirm_rain_4(self, start_year, end_year, start_month=None, end_month=None):
        if not self.validate_years_range(SrchRainData_4, 4, start_year, end_year):
            return
        
        data_handler = SrchRainData_4(self.js_detail, 4, start_year, end_year)
        data_handler.scrape_data_for_period()
        
        QMessageBox.information(self, "Download Complete", "Data download completed successfully.")

# ======================================================================= #

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    ex = DetailInfoWindow(name="Example", js_detail="Example")
    ex.show()
    
    sys.exit(app.exec_())
