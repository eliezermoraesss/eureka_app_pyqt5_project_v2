from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from ui.ui_register_screen import Ui_RegisterWindow


class RegisterWindow(QtWidgets.QMainWindow):
    def __init__(self, auth_controller):
        super(RegisterWindow, self).__init__()
        self.auth_controller = auth_controller
        self.ui = Ui_RegisterWindow()
        self.ui.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        # Conectar os botões às funções
        self.ui.btn_save.clicked.connect(self.register)
        self.ui.btn_close.clicked.connect(self.close)
        # Preencher o combobox com os valores desejados
        self.ui.area_combobox_field.addItems(["Engenharia", "PCP", "Faturamento", "Comercial", "Compras", "RH", "Almoxarifado", "Expedição"])

    def register(self):
        full_name = self.ui.name_field.text()
        username = self.ui.user_field.text()
        email = self.ui.email_field.text()
        password = self.ui.password_field.text()
        confirm_password = self.ui.password_field.text()
        role = self.ui.area_combobox_field.currentText()

        if not full_name or not username or not email or not password or not confirm_password:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Todos os campos são obrigatórios')
            return

        if password != confirm_password:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'As senhas não coincidem')
            return

        success, message = self.auth_controller.create_user(full_name, username, email, password, role)
        if success:
            QtWidgets.QMessageBox.information(self, 'Sucesso', message)
            self.close()
        else:
            QtWidgets.QMessageBox.warning(self, 'Erro', message)
