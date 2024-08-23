from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QSizePolicy, QSpacerItem
from PyQt5.QtGui import QIcon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("EUREKA SMARTPLIC® HOME - v0.1")

        # Configurar o ícone da janela
        icon_path = "src/resources/images/010.png"
        self.setWindowIcon(QIcon(icon_path))

        # Aplicar folha de estilo ao aplicativo
        self.setStyleSheet("""
            * {
                background-color: #363636;
            }

            QLabel, QCheckBox {
                color: #EEEEEE;
                font-size: 11px;
                font-weight: bold;
            }

            QLineEdit {
                background-color: #A7A6A6;
                border: 1px solid #262626;
                padding: 5px;
                border-radius: 8px;
            }

            QPushButton {
                background-color: #0a79f8;
                color: #fff;
                padding: 5px 15px;
                border: 2px;
                border-radius: 8px;
                font-size: 11px;
                height: 60px;
                font-weight: bold;
                margin-top: 6px;
                margin-bottom: 6px;
            }

            QPushButton:hover {
                background-color: #fff;
                color: #0a79f8
            }

            QPushButton:pressed {
                background-color: #6703c5;
                color: #fff;
            }
        """)

        # Botões
        self.engenharia_button = QPushButton("Engenharia", self)
        self.engenharia_button .setMinimumWidth(150)

        self.comercial_button = QPushButton("Comercial", self)
        self.comercial_button .setMinimumWidth(150)

        self.pcp_button = QPushButton("PCP", self)
        self.pcp_button.setMinimumWidth(150)

        layout = QVBoxLayout()
        layout_linha_01 = QHBoxLayout()

        layout_linha_01.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout_linha_01.addWidget(self.engenharia_button)
        layout_linha_01.addWidget(self.comercial_button )
        layout_linha_01.addWidget(self.pcp_button)
        layout_linha_01.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        layout.addLayout(layout_linha_01)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
