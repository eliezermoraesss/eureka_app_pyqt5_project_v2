import os
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QProcess, Qt

from src.app.utils.load_session import load_session
from ...qt.ui.ui_home_window import Ui_HomeWindow


class MainController(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainController, self).__init__()
        self.home_window = Ui_HomeWindow()
        self.home_window.setupUi(self)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.init_ui()

    def init_ui(self):
        user_data = load_session()
        primeiro_nome = user_data["full_name"].split(' ')[0]
        id_title = self.home_window.user_label.text()
        self.home_window.user_label.setText(id_title.replace("{user}", f"{primeiro_nome},"))
        self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setFixedSize(1200, 800)
        self.setup_connections()

    def setup_connections(self):
        def execute_dashboard_model():
            process = QProcess()
            script_path = os.path.abspath(os.path.join(self.base_dir, '..', '..', 'models', 'dashboard_model.pyw'))
            process.startDetached("python", [script_path])  # Usa startDetached para execução independente

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

        def execute_compras_model():
            process = QProcess()
            script_path = os.path.abspath(os.path.join(self.base_dir, '..', '..', 'models', 'compras_model.pyw'))
            process.startDetached("python", [script_path])

        def execute_qps_model():
            process = QProcess()
            script_path = os.path.abspath(os.path.join(self.base_dir, '..', '..', 'models', 'qps_model.pyw'))
            process.startDetached("python", [script_path])

        self.home_window.btn_dashboard.clicked.connect(execute_dashboard_model)
        self.home_window.btn_engenharia.clicked.connect(execute_engenharia_model)
        self.home_window.btn_pcp.clicked.connect(execute_pcp_model)
        self.home_window.btn_compras.clicked.connect(execute_compras_model)
        self.home_window.btn_comercial.clicked.connect(execute_comercial_model)
        self.home_window.btn_qps.clicked.connect(execute_qps_model)
        self.home_window.btn_close.clicked.connect(self.close)


# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#     main_window = MainController()
#     main_window.show()
#     sys.exit(app.exec_())
