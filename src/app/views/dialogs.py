from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel


class EngenhariaDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Engenharia")
        self.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Conteúdo da Engenharia"))
        self.setLayout(layout)


class ComercialDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Comercial")
        self.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Conteúdo do Comercial"))
        self.setLayout(layout)


class PcpDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PCP")
        self.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Conteúdo do PCP"))
        self.setLayout(layout)
