import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication

from src.qt.ui.ui_search_window import Ui_SearchWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(640, 600)

        self.ui = Ui_SearchWindow()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
