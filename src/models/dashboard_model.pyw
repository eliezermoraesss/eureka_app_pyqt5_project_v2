import os
import sys

# Caminho absoluto para o diretório onde o módulo src está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QLocale

from src.app.utils.load_session import load_session


class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        user_data = load_session()
        username = user_data["username"]
        role = user_data["role"]
        self.setWindowTitle(f"Eureka® Enaplic Dashboard - Power BI Viewer . {username} ({role})")

        # Definir a localização para português do Brasil
        locale = QLocale(QLocale.Portuguese, QLocale.Brazil)
        QLocale.setDefault(locale)

        # Cria o widget QWebEngineView
        self.browser = QWebEngineView()

        # Converte a string da URL para um objeto QUrl
        power_bi_url = QUrl("https://app.powerbi.com/groups/me/reports/b0632c9a-3773-4099-85b4-ce57f55e74b7"
                            "/d752779fc700976478f5?experience=power-bi")

        # Carrega a URL do relatório do Power BI
        self.browser.setUrl(power_bi_url)

        # Layout para o QWebEngineView
        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        # Define o layout no widget central
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Configura a aplicação para usar a localidade 'pt_BR'
    locale = QLocale(QLocale.Portuguese, QLocale.Brazil)
    QLocale.setDefault(locale)

    window = DashboardWindow()
    window.showMaximized()
    sys.exit(app.exec_())
