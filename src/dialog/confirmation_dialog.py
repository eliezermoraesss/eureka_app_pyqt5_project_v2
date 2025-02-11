from PyQt5.QtWidgets import QMessageBox

def show_confirmation_dialog(self, title, message):
    msg_box = QMessageBox(self)
    msg_box.setIcon(QMessageBox.Question)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg_box.setDefaultButton(QMessageBox.No)
    yes_button = msg_box.button(QMessageBox.Yes)
    yes_button.setText("Sim")
    no_button = msg_box.button(QMessageBox.No)
    no_button.setText("Não")
    return msg_box.exec_()
