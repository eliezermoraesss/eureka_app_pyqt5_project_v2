from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLineEdit, QLabel, QPushButton, QVBoxLayout, QMessageBox

from src.app.views.reset_password_window import ResetPasswordWindow


class CodeVerificationWindow(QtWidgets.QWidget):
    def __init__(self, auth_controller, email):
        super().__init__()
        self.auth_controller = auth_controller
        self.email = email
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Verificação de Código')
        self.setGeometry(100, 100, 300, 250)

        self.code_input = QLineEdit(self)
        self.code_input.setPlaceholderText('Código de verificação')

        self.verify_button = QPushButton('Verificar', self)
        self.verify_button.clicked.connect(self.verify_code)

        self.new_code_button = QPushButton('Gerar Novo Código', self)
        self.new_code_button.clicked.connect(self.generate_new_code)
        self.new_code_button.hide()

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Digite o código enviado para o seu e-mail:'))
        layout.addWidget(self.code_input)
        layout.addWidget(self.verify_button)
        layout.addWidget(self.new_code_button)
        self.setLayout(layout)

    def verify_code(self):
        code = self.code_input.text()
        success, message = self.auth_controller.verify_reset_code(self.email, code)
        if success:
            self.reset_password_window = ResetPasswordWindow(self.auth_controller, self.email)
            self.reset_password_window.show()
            self.close()
        else:
            QMessageBox.warning(self, 'Erro', message)
            if message == "O código expirou.":
                self.new_code_button.show()

    def generate_new_code(self):
        if self.auth_controller.generate_reset_code(self.email):
            QMessageBox.information(self, 'Sucesso', 'Novo código enviado para o seu e-mail.')
            self.new_code_button.hide()
        else:
            QMessageBox.warning(self, 'Erro', 'Erro ao gerar novo código.')