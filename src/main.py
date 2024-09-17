import os

from PyQt5 import QtWidgets
import sys
# Caminho absoluto para o diretório onde o módulo src está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.controllers.auth_controller import AuthController
from app.views.login_window import LoginWindow

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    auth_controller = AuthController()
    login_window = LoginWindow(auth_controller)
    login_window.show()
    sys.exit(app.exec_())
