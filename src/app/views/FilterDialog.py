from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QLabel, QLineEdit, QTextEdit


class FilterDialog(QDialog):
    def __init__(self, parent, nome_coluna, dataframe):
        super().__init__(parent)

        self.nome_coluna = nome_coluna
        self.dataframe = dataframe
        self.selecionados = []
        self.ordenacao_crescente = True  # Controle de ordenação
        self.vazio_label = "Vazio"

        self.setWindowTitle(f"{self.nome_coluna}")
        self.setGeometry(300, 300, 200, 500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # Remove botão de ajuda

        layout = QVBoxLayout()

        # Título
        titulo = QLabel(f"Filtrar por: {self.nome_coluna}")

        # Botão para ordenar os itens
        self.btn_ordenar = QPushButton("Ordenar itens (crescente)")
        self.btn_ordenar.clicked.connect(self.ordenar_itens)

        # Campo de pesquisa
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Pesquisar...")
        self.search_box.textChanged.connect(self.filtrar_itens)  # Filtrar enquanto o usuário digita

        # Criação do QListWidget com seleção múltipla
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)

        # Pegar valores únicos da coluna
        if self.nome_coluna == ' ':
            self.itens_originais = ['SEM PEDIDO COMPRA', 'AGUARDANDO ENTREGA', 'ENTREGA PARCIAL', 'PEDIDO ENCERRADO']
            self.list_widget.addItems(self.itens_originais)
        else:
            self.itens_originais = list(map(str, self.dataframe[self.nome_coluna].dropna().unique()))
            if self.dataframe[self.nome_coluna].isnull().any():
                self.itens_originais.append(self.vazio_label)
            self.list_widget.addItems(self.itens_originais)

        # Botão de aplicar filtro
        btn_aplicar = QPushButton("Aplicar Filtro")
        btn_aplicar.clicked.connect(self.aplicar_filtro)

        layout.addWidget(titulo)
        layout.addWidget(self.search_box)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.btn_ordenar)
        layout.addWidget(btn_aplicar)

        self.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
            }
            QListWidget {
                color: #EEEEEE;
                font-size: 14px;
            }
            QPushButton {
                font-size: 12px;
                height: 15px;
                font-weight: semibold;
            }
            """)
        self.setLayout(layout)

    def filtrar_itens(self):
        # Filtrar os itens com base no texto de pesquisa
        termo_pesquisa = self.search_box.text().lower()
        self.list_widget.clear()

        # Filtrar itens da lista original
        itens_filtrados = [item for item in self.itens_originais if termo_pesquisa in item.lower()]
        self.list_widget.addItems(itens_filtrados)

    def aplicar_filtro(self):
        # Coletar seleção
        itens_selecionados = self.list_widget.selectedItems()
        self.selecionados = []

        for item in itens_selecionados:
            if item.text() == self.vazio_label:
                self.selecionados.append(None)
            else:
                self.selecionados.append(item.text())

        self.accept()

    def ordenar_itens(self):
        # Ordenar os itens da lista
        if self.ordenacao_crescente:
            self.list_widget.sortItems()  # Ordena de forma crescente (padrão)
        else:
            # Obtem os itens, inverte a ordem e limpa a lista
            itens = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
            self.list_widget.clear()

            # Adiciona os itens em ordem decrescente
            self.list_widget.addItems(reversed(itens))

        # Alterna o estado da ordenação
        self.ordenacao_crescente = not self.ordenacao_crescente

        # Atualiza o texto do botão de ordenação
        if self.ordenacao_crescente:
            self.btn_ordenar.setText("Ordenar itens (crescente)")
        else:
            self.btn_ordenar.setText("Ordenar itens (decrescente)")

    def get_filtros_selecionados(self):
        return self.selecionados
