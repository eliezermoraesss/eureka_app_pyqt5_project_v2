import os
import sys

from PyQt5.QtCore import QProcess

# Caminho absoluto para o diretório onde o módulo src está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt5 import QtWidgets

from app.config.authorize_decorator import authorize
from models.engenharia_model import EngenhariaApp
from models.pcp_model import PcpApp
from models.compras_model import ComprasApp
from models.comercial_model import ComercialApp
from models.qps_model import QpClosedApp
from app.utils.load_session import load_session
from qt.ui.ui_home_window import Ui_HomeWindow


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.home_window = Ui_HomeWindow()
        self.home_window.setupUi(self)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.sub_windows = []
        self.processes = []
        self.init_ui()

    def init_ui(self):
        user_data = load_session()
        primeiro_nome = user_data["full_name"].split(' ')[0]
        id_title = self.home_window.user_label.text()
        self.setWindowTitle("Eureka® Home")
        self.home_window.user_label.setText(id_title.replace("{user}", f"{primeiro_nome},"))
        self.setFixedSize(1319, 797)
        self.setup_connections()

    def setup_connections(self):
        @authorize(['admin', 'manager', 'Diretoria', 'Comercial'], self)
        def execute_dashboard_model(checked=False):
            process = QProcess()
            script_path = os.path.abspath(os.path.join(self.base_dir, '..', '..', 'models', 'dashboard_model.pyw'))
            process.startDetached("python", [script_path])  # Usa startDetached para execução
            self.processes.append(process)

        def execute_engenharia_model():
            eng_window = EngenhariaApp(self)
            eng_window.showMaximized()
            self.sub_windows.append(eng_window)

        def execute_comercial_model():
            comercial_window = ComercialApp(self)
            comercial_window.showMaximized()
            self.sub_windows.append(comercial_window)

        def execute_pcp_model():
            pcp_window = PcpApp(self)
            pcp_window.showMaximized()
            self.sub_windows.append(pcp_window)
            
        def execute_compras_model():
            compras_window = ComprasApp(self)
            compras_window.showMaximized()
            self.sub_windows.append(compras_window)

        def execute_qps_model():
            qps_window = QpClosedApp(self)
            qps_window.showMaximized()
            self.sub_windows.append(qps_window)

        self.home_window.btn_dashboard.clicked.connect(execute_dashboard_model)
        self.home_window.btn_engenharia.clicked.connect(execute_engenharia_model)
        self.home_window.btn_pcp.clicked.connect(execute_pcp_model)
        self.home_window.btn_compras.clicked.connect(execute_compras_model)
        self.home_window.btn_comercial.clicked.connect(execute_comercial_model)
        self.home_window.btn_qps.clicked.connect(execute_qps_model)
        self.home_window.btn_logout.clicked.connect(self.close)

    def reopen(self):
        if not self.isVisible():
            self.show()
        self.raise_()

    def closeEvent(self, event):
        for window in self.sub_windows:
            window.close()

        for process in self.processes:
            process.kill()  # .terminate() ou .kill() se quiser garantir o encerramento imediato
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
