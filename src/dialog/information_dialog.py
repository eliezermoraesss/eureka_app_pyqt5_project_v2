from PyQt5.QtWidgets import QMessageBox

def information_dialog(self, title, message):
    msg_box = QMessageBox(self)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setStandardButtons(QMessageBox.Ok)
    ok_button = msg_box.button(QMessageBox.Ok)
    ok_button.setFixedSize(100, 50)  # Aumenta o tamanho do botão
    msg_box.exec_()
