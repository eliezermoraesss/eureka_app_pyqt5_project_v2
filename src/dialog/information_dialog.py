from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

def information_dialog(self, title, message):
    msg_box = QMessageBox(self)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setStandardButtons(QMessageBox.Ok)
    ok_button = msg_box.button(QMessageBox.Ok)
    ok_button.setFixedSize(100, 50)  # Increase the button size
    msg_box.setWindowModality(Qt.ApplicationModal)  # Make the dialog modal
    msg_box.exec_()
