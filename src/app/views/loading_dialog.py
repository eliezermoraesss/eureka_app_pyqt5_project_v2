import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel


class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super(LoadingDialog, self).__init__(parent)
        self.setWindowTitle("Carregando...")
        self.setModal(True)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)  # Janela sem borda
        self.setFixedSize(200, 200)  # Tamanho fixo da janela

        layout = QVBoxLayout()
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)

        # Carregar o GIF de carregamento
        gif_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'images', 'loading.gif'))
        self.movie = QMovie(gif_path)
        self.label.setMovie(self.movie)

        layout.addWidget(self.label)
        self.setLayout(layout)

    def start_animation(self):
        self.movie.start()

    def stop_animation(self):
        self.movie.stop()
