from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox

from src.app.views.reset_password_window import ResetPasswordWindow
from src.qt.ui.ui_token_verification_window import Ui_TokenVerificationWindow


class CodeVerificationWindow(QtWidgets.QDialog):
    def __init__(self, auth_controller, email):
        super(CodeVerificationWindow, self).__init__()
        self.auth_controller = auth_controller
        self.email = email
        self.ui = Ui_TokenVerificationWindow()
        self.ui.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(480, 400)
        self.ui.btn_verify_token.clicked.connect(self.verify_code)
        self.ui.btn_new_token.clicked.connect(self.generate_new_code)
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_new_token.hide()

    def verify_code(self):
        code = self.ui.token_field.text()
        success, message = self.auth_controller.verify_reset_code(self.email, code)
        if success:
            self.reset_password_window = ResetPasswordWindow(self.auth_controller, self.email)
            self.reset_password_window.exec_()
            self.close()
        else:
            QMessageBox.warning(self, 'Erro', message)
            if message == "O código expirou.":
                self.ui.btn_new_token.show()

    def generate_new_code(self):
        if self.auth_controller.generate_reset_code(self.email):
            QMessageBox.information(self, 'Sucesso', 'Novo código enviado para o seu e-mail.')
            self.ui.btn_new_token.hide()
        else:
            QMessageBox.warning(self, 'Erro', 'Erro ao gerar novo código.')

    def fade_in(self):
        self.effect = QtWidgets.QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.effect)
        self.anim = QtCore.QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()
