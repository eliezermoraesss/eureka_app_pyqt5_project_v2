import sys
import os
# Caminho absoluto para o diretório onde o módulo src está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt5.QtWidgets import QApplication
from src.app.controllers.main_controller import MainController


def main():
    app = QApplication(sys.argv)
    main_controller = MainController()
    main_controller.show_main_window()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
