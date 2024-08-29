from PyQt5 import QtWidgets
import sys
import os

from src.app.controllers.auth_controller import AuthController
from src.app.views.login_window import LoginWindow


def load_stylesheet(application, path):
    with open(path, 'r') as file:
        application.setStyleSheet(file.read())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    stylesheet_path = os.path.abspath(os.path.join(base_dir, '..', 'resources', 'styles', 'style.qss'))
    load_stylesheet(app, stylesheet_path)

    auth_controller = AuthController()
    login_window = LoginWindow(auth_controller)
    login_window.show()
    sys.exit(app.exec_())
