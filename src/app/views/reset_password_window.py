from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from src.qt.ui.ui_password_change_window import Ui_PasswordChangeWindow


class ResetPasswordWindow(QtWidgets.QDialog):
    def __init__(self, auth_controller, email):
        super(ResetPasswordWindow, self).__init__()
        self.auth_controller = auth_controller
        self.email = email
        self.ui = Ui_PasswordChangeWindow()
        self.ui.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(480, 400)
        self.ui.btn_change_password.clicked.connect(self.reset_password)
        self.ui.btn_close.clicked.connect(self.close)

    def reset_password(self):
        new_password = self.ui.password_field.text()
        confirm_password = self.ui.password_confirm_field.text()

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