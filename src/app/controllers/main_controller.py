import os
from PyQt5.QtCore import QProcess
from ..views.main_window import MainWindow


class MainController:
    def __init__(self):
        self.main_window = MainWindow()
        self.setup_connections()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

    def setup_connections(self):
        def execute_engenharia_model():
            process = QProcess()
            script_path = os.path.abspath(os.path.join(self.base_dir, '..', '..', 'models', 'engenharia_model.pyw'))
            process.startDetached("python", [script_path])  # Usa startDetached para execução independente

        def execute_comercial_model():
            process = QProcess()
            script_path = os.path.abspath(os.path.join(self.base_dir, '..', '..', 'models', 'comercial_model.pyw'))
            process.startDetached("python", [script_path])

        def execute_pcp_model():
            process = QProcess()
            script_path = os.path.abspath(os.path.join(self.base_dir, '..', '..', 'models', 'pcp_model.pyw'))
            process.startDetached("python", [script_path])

        self.main_window.engenharia_button.clicked.connect(execute_engenharia_model)
        self.main_window.pcp_button.clicked.connect(execute_pcp_model)
        self.main_window.comercial_button.clicked.connect(execute_comercial_model)

    def show_main_window(self):
        self.main_window.showMaximized()
