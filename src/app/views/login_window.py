import os
import sys

# Caminho absoluto para o diretório onde o módulo src está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QProcess

from app.controllers.auth_controller import AuthController
from app.views.main_window import MainWindow
from app.views.email_recovery_window import EmailRecoveryWindow
from app.views.register_window import RegisterWindow
from qt.ui.ui_login_screen import Ui_LoginWindow


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

        self.ui.user_field.returnPressed.connect(self.login)
        self.ui.password_field.returnPressed.connect(self.login)

    def login(self):
        username = self.ui.user_field.text()
        password = self.ui.password_field.text()

        if not username or not password:
            QtWidgets.QMessageBox.warning(self, 'Atenção', 'Todos os campos são obrigatórios')
            return

        user = self.auth_controller.get_user_by_username(username)

        if user and self.auth_controller.verify_password(user[4], password):
            user_data = {
                "full_name": user[1],
                "username": user[2],
                "email": user[3],
                "role": user[5]
            }
            self.auth_controller.save_session(user_data)  # Salva a sessão com o QSettings
            self.start_home_window()
            self.close()
        else:
            QtWidgets.QMessageBox.warning(self, 'Atenção', 'Credenciais inválidas')

    def forgot_password(self):
        self.email_recovery_window = EmailRecoveryWindow(self.auth_controller, self)
        self.email_recovery_window.exec_()

    def open_register_window(self):
        self.register_window = RegisterWindow(self.auth_controller)
        self.register_window.show()

    def start_home_window(self):
        self.home_window = MainWindow()
        self.home_window.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    auth_controller = AuthController()
    login_window = LoginWindow(auth_controller)
    login_window.show()
    sys.exit(app.exec_())
