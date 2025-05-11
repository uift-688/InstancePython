import sys
import time
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QFileDialog, QVBoxLayout, QHBoxLayout, QComboBox,
    QCheckBox, QProgressBar, QMessageBox, QDialog
)
from PySide6.QtCore import Qt, QThread, Signal
from requests import get
from zipfile import ZipFile
from io import BytesIO
from hashlib import sha512
from subprocess import STDOUT, PIPE, run
import tempfile
from pathlib import Path
from shutil import copytree, rmtree
from os import getcwd
import sys

class Install(QThread):
    path: str
    is_dump: bool
    is_uninstall: bool
    signal = Signal(float)
    complete_signal = Signal(str)
    lang: dict
    def run(self):
        if self.is_uninstall:
            self.signal.emit(0)
            if self.is_dump:
                python = Path(self.path) / "python" / "python.exe"
                dumper = run(["python", "-m", "pip", "freeze"], executable=python, stdout=PIPE, stderr=STDOUT)
                with open(Path(getcwd()) / "requirements.txt", "wb") as f:
                    f.write(dumper.stdout)
                    rmtree(Path(self.path) / "python")
                self.signal.emit(50)
            rmtree(Path(self.path) / "python")
            self.signal.emit(100)
            self.complete_signal.emit("done")
        else:
            progress1 = 0
            progress2 = 0
            progress3 = 0
            self.signal.emit(0)
            path = "https://www.python.org/ftp/python/3.13.3/python-3.13.3-embed-win32.zip"
            steam = get(path, stream=True)
            file = BytesIO()
            file_size = int(steam.headers.get('Content-Length', 0))
            for i, chunk in enumerate(steam.iter_content(1024)):
                file.write(chunk)
                progress1 = round(len(file.getvalue()) / file_size * 100)
                self.signal.emit((progress1 + progress2 + progress3) / 3)
            file_hash = "20662b8680aa781bcb00898c7de98e64bbb49e73e502bbfe08482d792faa43e8fdbdd8d6c5c23b10ad543739e7d9bf84fb77425e1007b9a06af12a309b53c3c1"
            if sha512(file.getvalue()).hexdigest() == file_hash:
                progress2 = 100
                self.signal.emit((progress1 + progress2 + progress3) / 3)
            else:
                self.complete_signal.emit("error")
            site_loader = """python313.zip
.

# Uncomment to run site.main() automatically
import site"""
            with tempfile.TemporaryDirectory() as tempassets, tempfile.TemporaryDirectory() as tdir:
                with ZipFile(BytesIO(file.getvalue()), "r") as zipf:
                    zipf.extractall(tdir)
                with open(Path(tdir) / "python313._pth", "wb") as f:
                    f.write(site_loader.encode())
                steam = get("https://bootstrap.pypa.io/get-pip.py", stream=True)
                file = BytesIO()
                file_size = int(steam.headers.get('Content-Length', 0))
                for i, chunk in enumerate(steam.iter_content(1024)):
                    file.write(chunk)
                    progress3 = round(len(file.getvalue()) / file_size * 100)
                    self.signal.emit((progress1 + progress2 + progress3) / 3)
                copytree(tdir, Path(self.path) / "python")
                self.signal.emit((progress1 + progress2 + progress3) / 3)
                self.complete_signal.emit("done")

class ProgressDialog(QDialog):
    def __init__(self, lang_texts, operation, parent=None, path = None, dump = None):
        super().__init__(parent)
        self.setWindowTitle(lang_texts["progress_title"])
        self.setFixedSize(350, 120)

        self.label = QLabel(f"{operation}...")
        self.progress = QProgressBar()
        self.path = path
        self.progress.setValue(0)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        self.lang = lang_texts
        self.setLayout(layout)
        self.install = Install(self)
        self.install.is_dump = dump
        self.install.is_uninstall = True if operation == "Uninstall" else False
        self.install.signal.connect(self.update_progress)
        self.install.complete_signal.connect(self.dialog)
        self.install.path = path
        self.install.lang = lang_texts
        self.install.start()
    def update_progress(self, data):
        self.progress.setValue(round(data))
    def dialog(self, data):
        if data == "done":
            QMessageBox.information(self, self.lang["done_title"], self.lang["done_content"], QMessageBox.Ok)
            self.accept()
        elif data == "error":
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)  # エラーアイコン
            msg_box.setWindowTitle(self.lang["error_title"])
            msg_box.setText(self.lang["error_content"])
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
            self.reject()
            app.exit(1)

class InstallerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(420, 210)

        self.languages = {
            "English": {
                "title": "Installer",
                "label": "Install Directory:",
                "placeholder": "e.g., C:/Program Files/MyApp",
                "browse": "Browse...",
                "install": "Install",
                "uninstall": "Uninstall",
                "select_dir": "Select Install Directory",
                "dump": "Dump after operation",
                "progress_title": "Progress",
                "error_title": "Error",
                "error_content": "Hash verification failed.",
                "done_title": "Done",
                "done_content": "Installation is complete."
            },
            "日本語": {
                "title": "インストーラー",
                "label": "インストール先ディレクトリ:",
                "placeholder": "例: C:/Program Files/MyApp",
                "browse": "参照...",
                "install": "インストール",
                "uninstall": "アンインストール",
                "select_dir": "インストール先を選択",
                "dump": "処理後にダンプする",
                "progress_title": "進行状況",
                "error_title": "エラー",
                "error_content": "ハッシュの検証に失敗しました。",
                "done_title": "完了",
                "done_content": "インストールが完了しました。"
            }
        }

        self.current_lang = "English"
        self.setup_ui()

    def setup_ui(self):
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(self.languages.keys())
        self.lang_combo.currentTextChanged.connect(self.change_language)

        self.label = QLabel()
        self.dir_input = QLineEdit()
        self.browse_button = QPushButton()
        self.browse_button.clicked.connect(self.browse_directory)

        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(self.browse_button)

        self.dump_checkbox = QCheckBox()

        self.install_button = QPushButton()
        self.uninstall_button = QPushButton()
        self.install_button.clicked.connect(lambda: self.run_operation("Install"))
        self.uninstall_button.clicked.connect(lambda: self.run_operation("Uninstall"))

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.install_button)
        button_layout.addWidget(self.uninstall_button)

        layout = QVBoxLayout()
        layout.addWidget(self.lang_combo)
        layout.addWidget(self.label)
        layout.addLayout(dir_layout)
        layout.addWidget(self.dump_checkbox)
        layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.update_texts()

    def update_texts(self):
        texts = self.languages[self.current_lang]
        self.setWindowTitle(texts["title"])
        self.label.setText(texts["label"])
        self.dir_input.setPlaceholderText(texts["placeholder"])
        self.browse_button.setText(texts["browse"])
        self.install_button.setText(texts["install"])
        self.uninstall_button.setText(texts["uninstall"])
        self.dump_checkbox.setText(texts["dump"])

    def change_language(self, lang):
        self.current_lang = lang
        self.update_texts()

    def browse_directory(self):
        texts = self.languages[self.current_lang]
        dir_path = QFileDialog.getExistingDirectory(self, texts["select_dir"])
        if dir_path:
            self.dir_input.setText(dir_path)

    def run_operation(self, operation_name):
        path = self.dir_input.text()
        texts = self.languages[self.current_lang]

        progress = ProgressDialog(texts, operation_name, self, path, self.dump_checkbox.isChecked())
        progress.exec()  # モーダル表示
        self.hide()
        app.exit(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = InstallerGUI()
    gui.show()
    sys.exit(app.exec())
