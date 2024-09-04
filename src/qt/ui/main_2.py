import sys

from PyQt5.QtGui import QPainterPath, QPainter, QPalette
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton
from PyQt5.QtCore import pyqtSlot, QFile, QTextStream, Qt

from ui.ui_register_screen import Ui_RegisterWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)

        self.ui = Ui_RegisterWindow()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
