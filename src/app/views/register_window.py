from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLineEdit, QLabel, QPushButton, QVBoxLayout, QMessageBox, QComboBox


class RegisterWindow(QtWidgets.QWidget):
    def __init__(self, auth_controller):
        super().__init__()
        self.auth_controller = auth_controller
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Registrar')
        self.setGeometry(100, 100, 300, 400)

        self.full_name_input = QLineEdit(self)
        self.full_name_input.setPlaceholderText('Nome Completo')

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText('Nome de Usuário')

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText('Email')

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('Senha')
        self.password_input.setEchoMode(QLineEdit.Password)

        self.confirm_password_input = QLineEdit(self)
        self.confirm_password_input.setPlaceholderText('Confirme a Senha')
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        self.role_combobox = QComboBox(self)
        self.role_combobox.addItems(["Engenharia", "PCP", "Faturamento", "Comercial", "Compras", "RH", "Almoxarifado", "Expedição"])

        self.register_button = QPushButton('Registrar', self)
        self.register_button.clicked.connect(self.register)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Nome Completo:'))
        layout.addWidget(self.full_name_input)
        layout.addWidget(QLabel('Nome de Usuário:'))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel('Email:'))
        layout.addWidget(self.email_input)
        layout.addWidget(QLabel('Senha:'))
        layout.addWidget(self.password_input)
        layout.addWidget(QLabel('Confirme a Senha:'))
        layout.addWidget(self.confirm_password_input)
        layout.addWidget(QLabel('Setor:'))
        layout.addWidget(self.role_combobox)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def register(self):
        full_name = self.full_name_input.text()
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        role = self.role_combobox.currentText()

        if not full_name or not username or not email or not password or not confirm_password:
            QMessageBox.warning(self, 'Erro', 'Todos os campos são obrigatórios')
            return

        if password != confirm_password:
            QMessageBox.warning(self, 'Erro', 'As senhas não coincidem')
            return

        success, message = self.auth_controller.create_user(full_name, username, email, password, role)
        if success:
            QMessageBox.information(self, 'Sucesso', message)
            self.close()
        else:
            QMessageBox.warning(self, 'Erro', message)