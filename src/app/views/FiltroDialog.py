from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QLabel, QLineEdit, QTextEdit


class FiltroDialog(QDialog):
    def __init__(self, parent, nome_coluna, dataframe):
        super().__init__(parent)

        self.nome_coluna = nome_coluna
        self.dataframe = dataframe
        self.selecionados = []
        self.ordenacao_crescente = True  # Controle de ordenação

        self.setWindowTitle(f"Filtrar: {self.nome_coluna}")
        self.setGeometry(100, 100, 250, 500)

        layout = QVBoxLayout()

        # Título
        titulo = QLabel(f"Filtrar valores na coluna: {self.nome_coluna}")
        layout.addWidget(titulo)

        # Botão para ordenar os itens
        self.btn_ordenar = QPushButton("Ordenar Itens (Crescente)")
        self.btn_ordenar.clicked.connect(self.ordenar_itens)
        layout.addWidget(self.btn_ordenar)

        # Campo de pesquisa
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Pesquisar...")
        self.search_box.textChanged.connect(self.filtrar_itens)  # Filtrar enquanto o usuário digita
        layout.addWidget(self.search_box)

        # Criação do QListWidget com seleção múltipla
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)

        # Pegar valores únicos da coluna
        self.itens_originais = list(map(str, self.dataframe[self.nome_coluna].dropna().unique()))
        self.list_widget.addItems(self.itens_originais)

        layout.addWidget(self.list_widget)

        # Campo de texto para exibir as seleções
        self.resultado_texto = QTextEdit()
        self.resultado_texto.setReadOnly(True)
        layout.addWidget(self.resultado_texto)

        # Botão de aplicar filtro
        btn_aplicar = QPushButton("Aplicar Filtro")
        btn_aplicar.clicked.connect(self.aplicar_filtro)
        layout.addWidget(btn_aplicar)

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
        self.selecionados = [item.text() for item in itens_selecionados]
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
            self.btn_ordenar.setText("Ordenar Itens (Crescente)")
        else:
            self.btn_ordenar.setText("Ordenar Itens (Decrescente)")

    def get_filtros_selecionados(self):
        return self.selecionados
