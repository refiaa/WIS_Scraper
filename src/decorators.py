from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

def date_input(input_type):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            self.date_input_layout = QHBoxLayout()

            self.start_input = QLineEdit()
            self.end_input = QLineEdit()
            if input_type == 'year':
                self.start_input.setPlaceholderText("Init Year")
                self.end_input.setPlaceholderText("End Year")
            else:  # input_type == 'date'
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

def data_confirm(data_type):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            start_str = self.start_input.text()
            end_str = self.end_input.text()

            if data_type == 'date':
                if not all(char.isdigit() or char == '/' for char in start_str + end_str):
                    QMessageBox.warning(self, "警告", "Invalid input")
                    return

                try:
                    start_year, start_month = map(int, start_str.split('/'))
                    end_year, end_month = map(int, end_str.split('/'))

                    if not (1 <= start_month <= 12) or not (1 <= end_month <= 12):
                        QMessageBox.warning(self, "警告", "Invalid Month")
                        return

                    if start_year > end_year or (start_year == end_year and start_month > end_month):
                        QMessageBox.warning(self, "警告", "Invalid range")
                        return

                except ValueError:
                    QMessageBox.warning(self, "警告", "Invalid Date Format")
                    return
                
                func(self, start_year, end_year, start_month, end_month)

            elif data_type == 'year':
                if not start_str.isdigit() or not end_str.isdigit():
                    QMessageBox.warning(self, "警告", "Invalid input")
                    return

                start_year = int(start_str)
                end_year = int(end_str)

                if start_year > end_year:
                    QMessageBox.warning(self, "警告", "Invalid range")
                    return

                func(self, start_year, end_year)

        return wrapper
    return decorator

def data_type_decorator(data_type):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if data_type == 'rain':
                return func(self, *args, **kwargs, data_class_prefix="SrchRainData")
            elif data_type == 'water':
                return func(self, *args, **kwargs, data_class_prefix="SrchWaterData")
            else:
                raise ValueError("Invalid data type")
        return wrapper
    return decorator