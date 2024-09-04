import os
import subprocess
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QProcess

from src.app.controllers.auth_controller import AuthController
from src.app.views.email_recovery_window import EmailRecoveryWindow
from src.app.views.register_window import RegisterWindow
from src.qt.ui.ui_login_screen import Ui_LoginWindow


class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self, auth_controller):
        super(LoginWindow, self).__init__()
        self.auth_controller = auth_controller
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Conectar os botões às funções
        self.ui.btn_login.clicked.connect(self.login)
        self.ui.btn_register.clicked.connect(self.open_register_window)
        self.ui.btn_forget_password.clicked.connect(self.forgot_password)
        self.ui.btn_close.clicked.connect(self.close)

    def login(self):
        username = self.ui.user_field.text()
        password = self.ui.password_field.text()

        if not username or not password:
            QtWidgets.QMessageBox.warning(self, 'Atenção', 'Todos os campos são obrigatórios')
            return

        user = self.auth_controller.get_user_by_username(username)

        if user and self.auth_controller.verify_password(user[4], password):
            self.close()
            subprocess.run(['setx', 'EUREKA_USER', user[2]], shell=True)
            self.start_home_window()
        else:
            QtWidgets.QMessageBox.warning(self, 'Atenção', 'Credenciais inválidas')

    def forgot_password(self):
        self.email_recovery_window = EmailRecoveryWindow(self.auth_controller, self)
        self.email_recovery_window.exec_()

    def open_register_window(self):
        self.register_window = RegisterWindow(self.auth_controller)
        self.register_window.show()

    def start_home_window(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        process = QProcess()
        script_path = os.path.abspath(os.path.join(base_dir, 'home_window.py'))
        process.startDetached("python", [script_path])


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    auth_controller = AuthController()
    login_window = LoginWindow(auth_controller)
    login_window.show()
    sys.exit(app.exec_())
