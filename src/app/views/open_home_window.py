from PyQt5 import QtWidgets
from PyQt5.QtCore import QProcess
import os


class OpenHomeWindow(QtWidgets.QWidget):
    def __init__(self, auth_controller, username):
        super().__init__()
        self.auth_controller = auth_controller
        self.username = username
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.init_ui()

    def init_ui(self):
        process = QProcess()
        script_path = os.path.abspath(os.path.join(self.base_dir, 'home_window.py'))
        process.startDetached("python", [script_path])
