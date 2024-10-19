import requests

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class UpdateChecker:
    def __init__(self, local_version_file: str, remote_version_url: str):
        self.local_version_file = local_version_file
        self.remote_version_url = remote_version_url

    def get_local_version(self) -> str:
        try:
            with open(self.local_version_file, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except FileNotFoundError:
            return "0.0.0"

    def get_remote_version(self) -> str:
        try:
            response = requests.get(self.remote_version_url, timeout=5)
            if response.status_code == 200:
                return response.text.strip()
            return ""
        except requests.RequestException:
            return ""

    def check_update(self) -> bool:
        local_version = self.get_local_version()
        remote_version = self.get_remote_version()
        return local_version and remote_version and local_version != remote_version

class DownloadProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ダウンロード")
        self.setFixedSize(400, 120)
        self.setWindowModality(Qt.WindowModal)

        layout = QVBoxLayout(self)

        self.label = QLabel("ダウンロード中...")
        self.label.setStyleSheet("font-size: 14px; color: black; font-weight: bold;")
        layout.addWidget(self.label)

        self.progressBar = QProgressBar(self)
        layout.addWidget(self.progressBar)

    def update_progress(self, percentage: int):
        self.progressBar.setValue(percentage)

class DownloadThread(QThread):
    update_progress = pyqtSignal(int)
    download_complete = pyqtSignal(str)
    download_failed = pyqtSignal(str)

    def __init__(self, url: str, file_name: str):
        super().__init__()
        self.url = url
        self.file_name = file_name

    def run(self):
        try:
            response = requests.get(self.url, stream=True, timeout=10)
            response.raise_for_status()
            total_length = response.headers.get('content-length')

            if total_length is None:
                with open(self.file_name, 'wb') as f:
                    f.write(response.content)
                self.update_progress.emit(100)
            else:
                total_length = int(total_length)
                downloaded = 0

                with open(self.file_name, 'wb') as f:
                    for data in response.iter_content(chunk_size=4096):
                        if data:
                            f.write(data)
                            downloaded += len(data)
                            done = int(100 * downloaded / total_length)
                            self.update_progress.emit(done)
            self.download_complete.emit(self.file_name)
        except requests.RequestException as e:
            self.download_failed.emit(str(e))
