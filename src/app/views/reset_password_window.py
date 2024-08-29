from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLineEdit, QLabel, QPushButton, QVBoxLayout, QMessageBox


class ResetPasswordWindow(QtWidgets.QWidget):
    def __init__(self, auth_controller, email):
        super().__init__()
        self.auth_controller = auth_controller
        self.email = email
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Redefinir Senha')
        self.setGeometry(100, 100, 300, 250)

        self.new_password_input = QLineEdit(self)
        self.new_password_input.setPlaceholderText('Nova senha')
        self.new_password_input.setEchoMode(QLineEdit.Password)

        self.confirm_password_input = QLineEdit(self)
        self.confirm_password_input.setPlaceholderText('Confirme a nova senha')
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        self.confirm_button = QPushButton('Redefinir Senha', self)
        self.confirm_button.clicked.connect(self.reset_password)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Digite a nova senha:'))
        layout.addWidget(self.new_password_input)
        layout.addWidget(QLabel('Confirme a nova senha:'))
        layout.addWidget(self.confirm_password_input)
        layout.addWidget(self.confirm_button)
        self.setLayout(layout)

    def reset_password(self):
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not new_password or not confirm_password:
            QMessageBox.warning(self, 'Erro', 'Todos os campos são obrigatórios')
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, 'Erro', 'As senhas não coincidem')
            return

        if self.auth_controller.reset_password(self.email, new_password):
            QMessageBox.information(self, 'Sucesso', 'Senha redefinida com sucesso!')
            self.close()
        else:
            QMessageBox.warning(self, 'Erro', 'Erro ao redefinir a senha.')