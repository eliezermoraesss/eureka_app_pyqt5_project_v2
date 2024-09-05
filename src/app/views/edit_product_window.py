from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton


class EditarItemWindow(QDialog):
    def __init__(self, linha_completa, parent=None):
        super().__init__(parent)
        self.linha_completa = linha_completa
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Editar Item")
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
                background-color: #DFE0E2;
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
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #fff;
                color: #0a79f8;
            }
            QPushButton:pressed {
                background-color: #6703c5;
                color: #fff;
            }
        """)

        layout = QVBoxLayout(self)

        # Labels e campos de edição
        self.label_desc = QLabel("Descrição")
        self.line_edit_desc = QLineEdit(self.linha_completa[1])  # Coluna "Descrição"

        self.label_desc_compl = QLabel("Desc. Compl.")
        self.line_edit_desc_compl = QLineEdit(self.linha_completa[2])  # Coluna "Desc. Compl."

        self.label_tipo = QLabel("Tipo")
        self.line_edit_tipo = QLineEdit(self.linha_completa[3])  # Coluna "Tipo"

        self.label_unid_med = QLabel("Unid. Med")
        self.line_edit_unid_med = QLineEdit(self.linha_completa[4])  # Coluna "Unid. Med"

        self.label_armazem = QLabel("Armazém")
        self.line_edit_armazem = QLineEdit(self.linha_completa[5])  # Coluna "Armazém"

        self.label_grupo = QLabel("Grupo")
        self.line_edit_grupo = QLineEdit(self.linha_completa[6])  # Coluna "Grupo"

        self.label_centro_custo = QLabel("Centro Custo")
        self.line_edit_centro_custo = QLineEdit(self.linha_completa[8])  # Coluna "Centro Custo"

        self.label_bloqueado = QLabel("Bloqueado?")
        self.line_edit_bloqueado = QLineEdit(self.linha_completa[9])  # Coluna "Bloqueado?"

        self.label_endereco = QLabel("Endereço")
        self.line_edit_endereco = QLineEdit(self.linha_completa[13])  # Coluna "Endereço"

        # Botão para salvar
        self.btn_salvar = QPushButton("Salvar")

        # Adiciona os widgets ao layout
        layout.addWidget(self.label_desc)
        layout.addWidget(self.line_edit_desc)

        layout.addWidget(self.label_desc_compl)
        layout.addWidget(self.line_edit_desc_compl)

        layout.addWidget(self.label_tipo)
        layout.addWidget(self.line_edit_tipo)

        layout.addWidget(self.label_unid_med)
        layout.addWidget(self.line_edit_unid_med)

        layout.addWidget(self.label_armazem)
        layout.addWidget(self.line_edit_armazem)

        layout.addWidget(self.label_grupo)
        layout.addWidget(self.line_edit_grupo)

        layout.addWidget(self.label_centro_custo)
        layout.addWidget(self.line_edit_centro_custo)

        layout.addWidget(self.label_bloqueado)
        layout.addWidget(self.line_edit_bloqueado)

        layout.addWidget(self.label_endereco)
        layout.addWidget(self.line_edit_endereco)

        layout.addWidget(self.btn_salvar)

        self.btn_salvar.clicked.connect(self.salvar_edicao)

    def salvar_edicao(self):
        # Recupera os valores editados
        self.linha_completa[1] = self.line_edit_desc.text()
        self.linha_completa[2] = self.line_edit_desc_compl.text()
        self.linha_completa[3] = self.line_edit_tipo.text()
        self.linha_completa[4] = self.line_edit_unid_med.text()
        self.linha_completa[5] = self.line_edit_armazem.text()
        self.linha_completa[6] = self.line_edit_grupo.text()
        self.linha_completa[8] = self.line_edit_centro_custo.text()
        self.linha_completa[9] = self.line_edit_bloqueado.text()
        self.linha_completa[13] = self.line_edit_endereco.text()

        # Fechar a janela após salvar
        self.accept()
