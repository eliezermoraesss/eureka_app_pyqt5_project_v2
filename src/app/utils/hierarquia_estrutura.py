import csv
import io
import locale
import os
from datetime import datetime

import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem, QTreeWidget,
                             QTreeWidgetItem, QSplitter, QLineEdit, QLabel, QHBoxLayout,
                             QAbstractItemView, QAction, QFileDialog, QMenu, QStyle)
from sqlalchemy import create_engine

from .db_mssql import setup_mssql
from .utils import abrir_desenho


class BOMViewer(QMainWindow):
    def __init__(self, codigo_pai):
        super().__init__()
        self.engine = None
        self.codigo_pai = codigo_pai
        self.descricao_pai = None
        self.current_theme = "white"  # Tema padrão
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        self.all_components = []
        self.setWindowTitle(f'Eureka® - Visualizador de hierarquia de estrutura - {codigo_pai}')

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Criar layout para filtro
        filter_layout = QHBoxLayout()

        # Filtro por Código
        filter_label_codigo = QLabel("Código:")
        self.filter_input_codigo = QLineEdit()
        self.filter_input_codigo.setMaxLength(13)
        self.filter_input_codigo.setFixedWidth(150)  # Ajusta a largura conforme o número máximo de caracteres
        self.filter_input_codigo.textChanged.connect(self.filter_tables)
        self.add_clear_button(self.filter_input_codigo)  # Adiciona o botão de limpar com ícone
        filter_layout.addWidget(filter_label_codigo)
        filter_layout.addWidget(self.filter_input_codigo)

        # Filtro por Descrição (início)
        filter_label_desc = QLabel("Descrição:")
        self.filter_input_desc = QLineEdit()
        self.filter_input_desc.setMaxLength(100)
        self.filter_input_desc.textChanged.connect(self.filter_tables)
        self.add_clear_button(self.filter_input_desc)  # Adiciona o botão de limpar com ícone
        filter_layout.addWidget(filter_label_desc)
        filter_layout.addWidget(self.filter_input_desc)

        # Filtro por Descrição (contém)
        filter_label_desc_contains = QLabel("Contém na Descrição:")
        self.filter_input_desc_contains = QLineEdit()
        self.filter_input_desc_contains.setMaxLength(60)
        self.filter_input_desc_contains.textChanged.connect(self.filter_tables)
        self.add_clear_button(self.filter_input_desc_contains)  # Adiciona o botão de limpar com ícone
        filter_layout.addWidget(filter_label_desc_contains)
        filter_layout.addWidget(self.filter_input_desc_contains)

        # Botão de alternar tema
        self.theme_button = QPushButton("🌓 Alternar Tema")
        self.theme_button.clicked.connect(self.toggle_theme)
        filter_layout.addWidget(self.theme_button)

        layout.addLayout(filter_layout)

        # Splitter para dividir tabela e árvore
        splitter = QSplitter(Qt.Horizontal)

        # Tabela
        self.table = QTableWidget()
        self.table.setSortingEnabled(False)
        self.table.setAlternatingRowColors(True)
        splitter.addWidget(self.table)

        # Container para árvore e botões
        tree_container = QWidget()
        tree_layout = QVBoxLayout(tree_container)

        # Árvore
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel('Árvore de hierarquia')

        # Mostrar linhas de conexão
        self.tree.setAlternatingRowColors(True)
        self.tree.setIndentation(20)  # Espaçamento da indentação
        self.tree.setRootIsDecorated(True)  # Mostra as linhas de conexão
        self.tree.setItemsExpandable(True)  # Permite expandir/recolher itens

        # Adicionar menu de contexto para a árvore
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_tree_context_menu)

        # Aumentar altura das linhas e melhorar espaçamento
        self.tree.setStyleSheet("""
            QTreeWidget::item {
                height: 30px;
                padding: 5px;
                margin: 2px;
            }
            QTreeWidget::item:selected {
                background-color: #cce5ff;
                color: #004085;
            }
        """)

        tree_layout.addWidget(self.tree)

        # Botões de expandir/recolher
        tree_buttons_layout = QHBoxLayout()
        expand_button = QPushButton("Expandir Tudo")
        collapse_button = QPushButton("Recolher Tudo")
        toggle_table_button = QPushButton("Ocultar/Exibir Tabela")
        export_button = QPushButton('Exportar para Excel')
        
        expand_button.clicked.connect(self.tree.expandAll)
        collapse_button.clicked.connect(self.tree.collapseAll)
        toggle_table_button.clicked.connect(self.toggle_table_visibility)
        export_button.clicked.connect(self.export_to_excel)
        
        tree_buttons_layout.addWidget(expand_button)
        tree_buttons_layout.addWidget(collapse_button)
        tree_buttons_layout.addWidget(toggle_table_button)
        tree_buttons_layout.addWidget(export_button)
        tree_layout.addLayout(tree_buttons_layout)

        splitter.addWidget(tree_container)

        layout.addWidget(splitter)

        # Setup banco de dados e carregar dados
        self.setup_database()
        self.load_data()
        
        self.apply_theme()

    def setup_database(self):
        username, password, database, server = setup_mssql()
        driver = '{SQL Server}'
        conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        self.engine = create_engine(f'mssql+pyodbc:///?odbc_connect={conn_str}')

    def get_components(self, parent_code: str, parent_qty: float = 1.0, level: int = 1):
        query = f"""
        SELECT 
            struct.G1_COD AS 'Código Pai',
            struct.G1_COMP AS 'Código',
            prod.B1_DESC AS 'Descrição',
            struct.G1_XUM AS 'Unidade',
            struct.G1_QUANT AS 'Quantidade'
        FROM 
            PROTHEUS12_R27.dbo.SG1010 struct
        INNER JOIN
            PROTHEUS12_R27.dbo.SB1010 prod
        ON 
            G1_COMP = B1_COD AND prod.D_E_L_E_T_ <> '*'
        WHERE 
            G1_COD = '{parent_code}' 
            AND G1_REVFIM <> 'ZZZ' 
            AND struct.D_E_L_E_T_ <> '*' 
            AND G1_REVFIM = (
                SELECT MAX(G1_REVFIM) 
                FROM PROTHEUS12_R27.dbo.SG1010 
                WHERE G1_COD = '{parent_code}'
                AND G1_REVFIM <> 'ZZZ' 
                AND struct.D_E_L_E_T_ <> '*'
            )
        """

        try:
            df = pd.read_sql(query, self.engine)

            if not df.empty:
                for _, row in df.iterrows():
                    total_qty = parent_qty * row['Quantidade']
    
                    component = {
                        'Nível': level,
                        'Código': row['Código'].strip(),
                        'Código Pai': row['Código Pai'].strip(),
                        'Descrição': row['Descrição'].strip(),
                        'Unidade': row['Unidade'].strip(),
                        'Quantidade': row['Quantidade'],
                        'Quantidade Total': total_qty
                    }
                    self.all_components.append(component)

                    self.get_components(row['Código'], total_qty, level + 1)

        except Exception as e:
            print(f"Erro ao processar código {parent_code}: {str(e)}")

    def load_data(self):
        codigo_pai = self.codigo_pai
        self.all_components = []

        # Adicionar item de nível mais alto
        # Primeiro precisamos buscar a descrição do item pai
        query = f"""
        SELECT B1_DESC as 'Descrição'
        FROM PROTHEUS12_R27.dbo.SB1010
        WHERE B1_COD = '{codigo_pai}'
        AND D_E_L_E_T_ <> '*'
        """
        try:
            df_pai = pd.read_sql(query, self.engine)
            descricao_pai = df_pai['Descrição'].iloc[0] if not df_pai.empty else ''
            self.descricao_pai = descricao_pai
        except:
            descricao_pai = ''

        self.all_components.append({
            'Nível': 0,
            'Código': codigo_pai.strip(),
            'Descrição': descricao_pai.strip(),
            'Código Pai': '-',
            'Unidade': 'UN',
            'Quantidade': 1.0,
            'Quantidade Total': 1.0
        })

        self.get_components(codigo_pai)
        self.df = pd.DataFrame(self.all_components)
        self.df.insert(5, 'Desenho PDF', '')
        # Reordenar as colunas
        self.df = self.df[['Nível', 'Código', 'Código Pai', 'Descrição', 'Desenho PDF', 'Unidade', 'Quantidade', 'Quantidade Total']]

        self.setup_table()
        self.build_tree()

    def setup_table(self):
        self.table.setColumnCount(len(self.df.columns))
        self.table.setHorizontalHeaderLabels(self.df.columns)
        self.populate_table(self.df)
        self.table.resizeColumnsToContents()

        # Tornar a tabela não editável
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Permitir seleção de múltiplas linhas
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Habilitar menu de contexto
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        # Conectar o sinal de duplo clique
        self.table.cellDoubleClicked.connect(self.copy_cell)

        # Ajustar o splitter após a tabela estar configurada
        self.adjust_splitter_sizes()

    def adjust_splitter_sizes(self):
        # Calcular a largura total necessária para a tabela
        total_width = 0
        for i in range(self.table.columnCount()):
            total_width += self.table.columnWidth(i)

        # Adicionar um pouco de margem
        total_width += 80

        # Obter a largura total da janela
        window_width = self.width()

        # Calcular a largura restante para a árvore
        tree_width = max(400, window_width - total_width)  # Mínimo de 400 pixels para a árvore

        # Definir as proporções do splitter
        splitter = self.findChild(QSplitter)
        if splitter:
            splitter.setSizes([total_width, tree_width])

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Reajustar o splitter quando a janela for redimensionada
        self.adjust_splitter_sizes()

    def show_context_menu(self, position):
        menu = QMenu()
        copy_action = QAction("Copiar", self)
        copy_action.triggered.connect(self.copy_selection)
        
        open_drawing_action = QAction("Abrir desenho...", self)
        open_drawing_action.triggered.connect(lambda: abrir_desenho(self, self.table))
        
        menu.addAction(copy_action)
        menu.addAction(open_drawing_action)
        menu.exec_(self.table.viewport().mapToGlobal(position))

    def copy_selection(self):
        selection = self.table.selectedIndexes()
        if selection:
            rows = sorted(index.row() for index in selection)
            columns = sorted(index.column() for index in selection)
            rowcount = rows[-1] - rows[0] + 1
            colcount = columns[-1] - columns[0] + 1
            table = [[''] * colcount for _ in range(rowcount)]
            for index in selection:
                row = index.row() - rows[0]
                col = index.column() - columns[0]
                table[row][col] = self.table.item(index.row(), index.column()).text()
            stream = io.StringIO()
            csv.writer(stream, delimiter='\t').writerows(table)
            QApplication.clipboard().setText(stream.getvalue())

    def format_quantity(self, value):
        """Formata a quantidade: inteiro sem casas decimais, decimal com duas casas"""
        if value.is_integer():
            return f"{int(value)}"
        return locale.format_string("%.2f", value, grouping=True)

    def populate_table(self, df):
        self.table.setRowCount(len(df))
        COLOR_FILE_EXISTS = QColor(51, 211, 145)  # green
        COLOR_FILE_MISSING = QColor(201, 92, 118)  # light red
        for i, row in df.iterrows():
            for j, (column_name, value) in enumerate(row.items()):
                item = QTableWidgetItem()
                
                # Formatar quantidades (colunas Quantidade e Quantidade Total)
                if column_name in ['Quantidade', 'Quantidade Total']:
                    formatted_value = self.format_quantity(value)
                    item.setText(formatted_value)
                # Special handling for Desenho PDF column
                elif column_name == 'Desenho PDF':
                    codigo_desenho = row['Código'].strip()
                    pdf_path = os.path.join(r"\\192.175.175.4\dados\EMPRESA\PROJETOS\PDF-OFICIAL",
                                            f"{codigo_desenho}.PDF")
                    if os.path.exists(pdf_path):
                        item.setBackground(COLOR_FILE_EXISTS)
                        item.setText('Sim')
                        item.setToolTip("Desenho encontrado")
                    else:
                        item.setBackground(COLOR_FILE_MISSING)
                        item.setText('Não')
                        item.setToolTip("Desenho não encontrado")
                else:
                    item.setText(str(value))
                
                # Alinhar ao centro exceto código e descrição
                if column_name not in ['Código', 'Descrição']:
                    item.setTextAlignment(Qt.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
                self.table.setItem(i, j, item)

    def build_tree_recursive(self, parent_item, parent_code, parent_qty):
        query = f"""
        SELECT 
            struct.G1_COD AS 'Código',
            struct.G1_COMP AS 'Código Pai',
            prod.B1_DESC AS 'Descrição',
            struct.G1_XUM AS 'Unidade',
            struct.G1_QUANT AS 'Quantidade'
        FROM 
            PROTHEUS12_R27.dbo.SG1010 struct
        INNER JOIN
            PROTHEUS12_R27.dbo.SB1010 prod
        ON 
            G1_COMP = B1_COD AND prod.D_E_L_E_T_ <> '*'
        WHERE 
            G1_COD = '{parent_code}' 
            AND G1_REVFIM <> 'ZZZ' 
            AND struct.D_E_L_E_T_ <> '*' 
            AND G1_REVFIM = (
                SELECT MAX(G1_REVFIM) 
                FROM PROTHEUS12_R27.dbo.SG1010 
                WHERE G1_COD = '{parent_code}'
                AND G1_REVFIM <> 'ZZZ' 
                AND struct.D_E_L_E_T_ <> '*'
            )
        """

        try:
            df = pd.read_sql(query, self.engine)

            for _, row in df.iterrows():
                total_qty = parent_qty * row['Quantidade']

                child_item = QTreeWidgetItem(parent_item)
                formatted_qty = self.format_quantity(total_qty)
                child_item.setText(0,
                                   f"{row['Código Pai'].strip()}  |  {row['Descrição'].strip()}  |  {formatted_qty} {row['Unidade'].strip()}")

                self.build_tree_recursive(child_item, row['Código Pai'], total_qty)
        except Exception as e:
            print(f"Erro ao processar código {parent_code}: {str(e)}")

    def build_tree(self):
        self.tree.clear()

        # Buscar descrição do item raiz
        query = f"""
        SELECT B1_DESC as 'Descrição', B1_UM as 'Unidade'
        FROM PROTHEUS12_R27.dbo.SB1010
        WHERE B1_COD = '{self.codigo_pai}'
        AND D_E_L_E_T_ <> '*'
        """
        try:
            df_root = pd.read_sql(query, self.engine)
            root_desc = df_root['Descrição'].iloc[0] if not df_root.empty else ''
            root_unidade = df_root['Unidade'].iloc[0] if not df_root.empty else ''
        except:
            root_desc = ''
            root_unidade = ''

        # Iniciar a construção da árvore com o nó raiz
        root_item = QTreeWidgetItem(self.tree)
        formatted_qty = self.format_quantity(1.0)
        root_item.setText(0, f"{self.codigo_pai}  |  {root_desc.strip()}  |  {formatted_qty} {root_unidade.strip()}")
        self.build_tree_recursive(root_item, self.codigo_pai, 1.0)

    def filter_tables(self):
        filter_codigo = self.filter_input_codigo.text().lower().strip()
        filter_desc = self.filter_input_desc.text().lower().strip()
        filter_desc_contains = self.filter_input_desc_contains.text().lower().strip()

        # PARTE 1: FILTRAGEM DA TABELA
        for row in range(self.table.rowCount()):
            row_visible = True
            codigo = self.table.item(row, 1).text().lower()
            descricao = self.table.item(row, 3).text().lower()

            if filter_codigo and filter_codigo not in codigo:
                row_visible = False
            if filter_desc and not descricao.startswith(filter_desc):
                row_visible = False
            if filter_desc_contains and filter_desc_contains not in descricao:
                row_visible = False

            self.table.setRowHidden(row, not row_visible)

        # PARTE 2: FILTRAGEM DA ÁRVORE
        first_match = None
        matched_items = []

        def process_item(item):
            nonlocal first_match
            text = item.text(0).lower()
            item_visible = True

            matches_filter = True
            if filter_codigo and filter_codigo not in text:
                matches_filter = False
            if filter_desc and not text.split('|')[1].strip().startswith(filter_desc):
                matches_filter = False
            if filter_desc_contains and filter_desc_contains not in text.split('|')[1].strip():
                matches_filter = False

            # Usar cores diferentes para highlight baseado no tema
            highlight_color = Qt.yellow if self.current_theme == "white" else QColor(255, 255, 0, 70)
            background_color = Qt.white if self.current_theme == "white" else QColor(45, 45, 45)

            if matches_filter and (filter_codigo or filter_desc or filter_desc_contains):
                item.setBackground(0, highlight_color)
                matched_items.append(item)
                if first_match is None:
                    first_match = item
            else:
                item.setBackground(0, background_color)

            for i in range(item.childCount()):
                child_visible = process_item(item.child(i))
                if child_visible:
                    item_visible = True

            item.setHidden(not item_visible)
            return item_visible or matches_filter

        for i in range(self.tree.topLevelItemCount()):
            process_item(self.tree.topLevelItem(i))

        if filter_codigo or filter_desc or filter_desc_contains:
            self.tree.expandAll()
            if first_match:
                self.tree.scrollToItem(first_match)
                self.tree.setCurrentItem(first_match)
        else:
            self.tree.collapseAll()

    def toggle_table_visibility(self):
        if self.table.isVisible():
            self.table.hide()
        else:
            self.table.show()

    def export_to_excel(self):
        # Gerar nome do arquivo com data e hora
        now = datetime.now()
        default_filename = f"estrutura_explodida_{self.codigo_pai}_{now.strftime('%Y%m%d_%H%M%S')}.xlsx"

        # Obter o caminho da área de trabalho
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        default_path = os.path.join(desktop, default_filename)

        # Abrir diálogo de salvamento
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar para Excel",
            default_path,
            "Excel Files (*.xlsx);;All Files (*)"
        )

        if filename:
            try:
                self.df.to_excel(filename, index=False)
                # Abrir o arquivo no Excel
                os.startfile(filename)
            except Exception as e:
                print(f"Erro ao exportar para Excel: {str(e)}")

    def add_clear_button(self, line_edit):
        clear_icon = self.style().standardIcon(QStyle.SP_LineEditClearButton)

        line_edit_height = line_edit.height()
        pixmap = clear_icon.pixmap(line_edit_height - 4, line_edit_height - 4)
        larger_clear_icon = QIcon(pixmap)

        clear_action = QAction(larger_clear_icon, "Limpar", line_edit)
        clear_action.triggered.connect(line_edit.clear)
        line_edit.addAction(clear_action, QLineEdit.TrailingPosition)

    def show_tree_context_menu(self, position):
        item = self.tree.itemAt(position)
        if item:
            menu = QMenu()
            copy_action = QAction("Copiar", self)
            copy_action.triggered.connect(lambda: self.copy_tree_item(item))
            
            # Extrair o código do item (primeira parte antes do |)
            codigo = item.text(0).split('|')[0].strip()
            
            open_drawing_action = QAction("Abrir desenho...", self)
            open_drawing_action.triggered.connect(lambda: self.abrir_desenho_arvore(codigo))
            
            menu.addAction(copy_action)
            menu.addAction(open_drawing_action)
            menu.exec_(self.tree.viewport().mapToGlobal(position))

    def copy_tree_item(self, item):
        if item:
            QApplication.clipboard().setText(item.text(0))

    def abrir_desenho_arvore(self, codigo):
        pdf_path = os.path.join(r"\\192.175.175.4\dados\EMPRESA\PROJETOS\PDF-OFICIAL",
                               f"{codigo}.PDF")
        
        if os.path.exists(pdf_path):
            os.startfile(pdf_path)

    def copy_cell(self, row, column):
        """Copia o conteúdo da célula selecionada para a área de transferência quando houver duplo clique"""
        item = self.table.item(row, column)
        if item:
            QApplication.clipboard().setText(item.text())

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "white" else "white"
        self.apply_theme()
        # Reaplica a filtragem para atualizar as cores dos itens na árvore
        self.filter_tables()

    def apply_theme(self):
        if self.current_theme == "white":
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
                QLabel {
                    font-weight: bold;
                    color: #000000;
                }
                QLineEdit {
                    border: 1px solid #ced4da;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 12px;
                    background-color: white;
                    color: #000000;
                }
                QTableWidget {
                    border: 1px solid #dee2e6;
                    background-color: white;
                    color: #000000;
                    alternate-background-color: #f8f9fa;
                }
                QHeaderView::section {
                    background-color: #f8f9fa;
                    padding: 4px;
                    border: 1px solid #dee2e6;
                    font-weight: bold;
                    color: #000000;
                }
                QTableWidget::item:selected {
                    background-color: #cce5ff;
                    color: #004085;
                }
                QTreeWidget {
                    border: 1px solid #dee2e6;
                    background-color: white;
                    color: #000000;
                    alternate-background-color: #f8f9fa;
                }
                QTreeWidget::item {
                    height: 30px;
                    padding: 5px;
                    margin: 2px;
                }
                QTreeWidget::item:selected {
                    background-color: #cce5ff;
                    color: #004085;
                }
            """)
        else:  # dark theme
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #0d6efd;
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #0b5ed7;
                }
                QLabel {
                    font-weight: bold;
                    color: #ffffff;
                }
                QLineEdit {
                    border: 1px solid #495057;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 12px;
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QTableWidget {
                    border: 1px solid #495057;
                    background-color: #2d2d2d;
                    color: #ffffff;
                    alternate-background-color: #363636;
                }
                QHeaderView::section {
                    background-color: #363636;
                    padding: 4px;
                    border: 1px solid #495057;
                    font-weight: bold;
                    color: #ffffff;
                }
                QTableWidget::item:selected {
                    background-color: #cce5ff;
                    color: #004085;
                }
                QTreeWidget {
                    border: 1px solid #495057;
                    background-color: #2d2d2d;
                    color: #ffffff;
                    alternate-background-color: #363636;
                }
                QTreeWidget::item {
                    height: 30px;
                    padding: 5px;
                    margin: 2px;
                }
                QTreeWidget::item:selected {
                    background-color: #cce5ff;
                    color: #004085;
                }
            """)
