from PyQt5 import QtWidgets
import sys

from src.app.controllers.auth_controller import AuthController
from src.app.views.login_window import LoginWindow

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    auth_controller = AuthController()
    login_window = LoginWindow(auth_controller)
    login_window.show()
    sys.exit(app.exec_())
