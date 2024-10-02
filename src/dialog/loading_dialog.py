from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QApplication


def loading_dialog(parent, titulo, mensagem):
    # Cria uma janela personalizada para carregamento
    dialog = QDialog(parent)
    dialog.setWindowTitle(titulo)
    dialog.setWindowModality(Qt.ApplicationModal)  # Bloqueia interações com a janela principal
    dialog.setFixedSize(400, 150)  # Define um tamanho maior
    dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # Remove botão de ajuda

    layout = QVBoxLayout()

    label_mensagem = QLabel(mensagem)
    label_mensagem.setAlignment(Qt.AlignCenter)

    # Adiciona barra de progresso preenchida
    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    progress_bar.setValue(100)  # Barra de progresso completamente cheia
    progress_bar.setTextVisible(False)  # Remove o texto da barra

    layout.addWidget(label_mensagem)
    layout.addWidget(progress_bar)

    dialog.setLayout(layout)

    # Centraliza a janela na tela
    qr = dialog.frameGeometry()
    cp = QApplication.desktop().screen().rect().center()
    qr.moveCenter(cp)
    dialog.move(qr.topLeft())

    dialog.show()

    # Força a atualização da "interface"
    QApplication.processEvents()

    return dialog
