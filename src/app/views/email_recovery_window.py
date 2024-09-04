from PyQt5 import QtWidgets

from src.app.views.code_verification_window import CodeVerificationWindow
from src.qt.ui.ui_email_recovery_window import Ui_EmailRecoveryWindow


class EmailRecoveryWindow(QtWidgets.QDialog):
    def __init__(self, auth_controller, parent=None):
        super(EmailRecoveryWindow, self).__init__(parent)
        self.ui = Ui_EmailRecoveryWindow()
        self.ui.setupUi(self)
        self.setFixedSize(480, 400)

        self.auth_controller = auth_controller

        # Connect buttons to methods
        self.ui.btn_send_email.clicked.connect(self.send_email)
        self.ui.btn_close.clicked.connect(self.close)

    def send_email(self):
        email = self.ui.email_field.text()
        if email:
            if self.auth_controller.generate_reset_code(email):
                # Assuming CodeVerificationWindow is defined elsewhere
                self.code_verification_window = CodeVerificationWindow(self.auth_controller, email)
                self.code_verification_window.show()
                self.close()
            else:
                QtWidgets.QMessageBox.warning(self, 'Erro', 'Email não encontrado')
        else:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'O campo de e-mail não pode estar vazio')
