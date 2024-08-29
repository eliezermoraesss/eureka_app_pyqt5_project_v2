from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLineEdit, QLabel, QPushButton, QVBoxLayout, QMessageBox

from src.app.views.code_verification_window import CodeVerificationWindow
from src.app.views.open_home_window import OpenHomeWindow
from src.app.views.register_window import RegisterWindow


class LoginWindow(QtWidgets.QWidget):
    def __init__(self, auth_controller):
        super().__init__()
        self.auth_controller = auth_controller
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Login')
        self.setGeometry(100, 100, 300, 200)

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText('Nome de Usuário')

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('Senha')
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton('Login', self)
        self.login_button.clicked.connect(self.login)

        self.forgot_password_button = QPushButton('Esqueceu a senha?', self)
        self.forgot_password_button.clicked.connect(self.forgot_password)

        self.register_button = QPushButton('Registrar', self)
        self.register_button.clicked.connect(self.open_register_window)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Nome de Usuário:'))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel('Senha:'))
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.forgot_password_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, 'Erro', 'Todos os campos são obrigatórios')
            return

        user = self.auth_controller.get_user_by_username(username)

        if user and self.auth_controller.verify_password(user[4], password):
            self.main_window = OpenHomeWindow(self.auth_controller, username)  # Abre a janela principal se o login for bem-sucedido
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, 'Erro', 'Credenciais inválidas')

    def forgot_password(self):
        email, ok = QtWidgets.QInputDialog.getText(self, 'Recuperar Senha', 'Digite seu e-mail:')
        if ok and email:
            if self.auth_controller.generate_reset_code(email):
                self.code_verification_window = CodeVerificationWindow(self.auth_controller, email)
                self.code_verification_window.show()
            else:
                QMessageBox.warning(self, 'Erro', 'Email não encontrado')

    def open_register_window(self):
        self.register_window = RegisterWindow(self.auth_controller)
        self.register_window.show()
