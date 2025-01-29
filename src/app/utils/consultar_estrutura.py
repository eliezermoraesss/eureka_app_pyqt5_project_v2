import ctypes
import locale
import os
from datetime import datetime

import pandas as pd
import pyodbc
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QAbstractItemView, QItemDelegate, \
    QTableWidgetItem, QPushButton, QSizePolicy, QLabel, QSpacerItem, QMessageBox, QComboBox
from sqlalchemy import create_engine

from src.app.utils.utils import ajustar_largura_coluna_descricao, exportar_excel, exibir_mensagem
from .abrir_hierarquia_estrutura import abrir_hierarquia_estrutura
from .db_mssql import setup_mssql


class ConsultaEstrutura:
    def __init__(self):
        super().__init__()
        self.last_revision = None
        self.query = None
        self.engine = None
        self.descricao = None
        self.df = None
        self.COLOR_FILE_EXISTS = QColor(51, 211, 145)  # green
        self.COLOR_FILE_MISSING = QColor(201, 92, 118)  # light red
        self.tabela = None
        self.layout_cabecalho = None
        self.layout_nova_guia_estrutura = None
        self.nova_guia_estrutura = None
        self.codigo_pai = None
        self.combobox_revisao = None
        self.module_object = None
        self.driver = '{SQL Server}'
        self.username, self.password, self.database, self.server = setup_mssql()

    def configurar_tabela(self):
        self.nova_guia_estrutura = QWidget()
        self.layout_nova_guia_estrutura = QVBoxLayout()
        self.layout_cabecalho = QHBoxLayout()

        self.tabela = QTableWidget(self.nova_guia_estrutura)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)

        self.tabela.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabela.customContextMenuRequested.connect(
            lambda pos: self.module_object.show_context_menu(pos, self.tabela))

        self.tabela.setColumnCount(len(self.df.columns))
        self.tabela.setHorizontalHeaderLabels(self.df.columns)

        # Tornar a tabela somente leitura
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)

        self.tabela.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.tabela.setItemDelegateForColumn(self.df.columns.get_loc('Quantidade'), QItemDelegate(self.tabela))

        # Configurar a fonte da tabela
        fonte_tabela = QFont("Segoe UI", 8)
        self.tabela.setFont(fonte_tabela)

        # Ajustar a altura das linhas
        self.tabela.verticalHeader().setDefaultSectionSize(22)

        self.tabela.itemChanged.connect(
            lambda item_value: self.handle_item_change(item_value, self.tabela,
                                                       self.codigo_pai) if self.tabela.currentItem() else None)

    def configurar_layout(self):
        layout_combobox = QHBoxLayout()

        label_revisao = QLabel("Revisão:")
        label_revisao.setObjectName("label_revisao")
        self.combobox_revisao = QComboBox()
        self.combobox_revisao.setEditable(False)
        self.combobox_revisao.setObjectName("combobox_revisao")

        revisao = self.get_last_revision(self.codigo_pai)
        revisao_int = int(revisao) if revisao else 0
        self.last_revision = revisao

        items = []
        for i in range(1, revisao_int + 1):
            items.append(str(i).zfill(3))

        items.sort(reverse=True)
        self.combobox_revisao.clear()

        for item in items:
            self.combobox_revisao.addItem(item)

        self.combobox_revisao.setCurrentIndex(0)
        layout_combobox.addWidget(label_revisao)
        layout_combobox.addWidget(self.combobox_revisao)

        self.combobox_revisao.currentIndexChanged.connect(self.when_combobox_revisao_changed)

        btn_estrutura_explodida = QPushButton("Consultar estrutura explodida", self.module_object)
        btn_estrutura_explodida.clicked.connect(lambda: abrir_hierarquia_estrutura(self, self.codigo_pai))
        btn_estrutura_explodida.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        btn_exportar_excel = QPushButton("Exportar Excel", self.module_object)
        btn_exportar_excel.clicked.connect(lambda: exportar_excel(self, self.tabela))
        btn_exportar_excel.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        select_product_label = QLabel(f"Consulta de Estrutura \n\n{self.codigo_pai}\t{self.descricao}")
        select_product_label.setTextInteractionFlags(Qt.TextSelectableByMouse |
                                                     Qt.TextSelectableByKeyboard)

        self.layout_cabecalho.addWidget(select_product_label, alignment=Qt.AlignLeft)
        self.layout_cabecalho.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.layout_cabecalho.addLayout(layout_combobox)
        self.layout_cabecalho.addWidget(btn_estrutura_explodida)
        self.layout_cabecalho.addWidget(btn_exportar_excel)

        self.layout_nova_guia_estrutura.addLayout(self.layout_cabecalho)
        self.layout_nova_guia_estrutura.addWidget(self.tabela)
        self.nova_guia_estrutura.setLayout(self.layout_nova_guia_estrutura)

        self.nova_guia_estrutura.setStyleSheet("""                                           
                                * {
                                    background-color: #262626;
                                }
        
                                QLabel {
                                    color: #EEEEEE;
                                    font-size: 18px;
                                    font-weight: bold;
                                }
                                
                                QLabel#label_revisao {
                                    font-size: 12px;
                                }
                                
                                QComboBox {
                                    background-color: #EEEEEE;
                                    border: 1px solid #393E46;
                                    margin-bottom: 10px;
                                    padding: 5px 10px;
                                    border-radius: 10px;
                                    height: 20px;
                                    font-size: 16px;
                                }                 
                                
                                QComboBox QAbstractItemView {
                                    background-color: #EEEEEE;
                                    color: #000000; /* Cor do texto para garantir legibilidade */
                                    selection-background-color: #3f37c9; /* Cor de seleção quando passa o mouse */
                                    selection-color: #FFFFFF; /* Cor do texto quando selecionado */
                                    border: 1px solid #393E46;
                                }
                                
                                QPushButton {
                                    background-color: #0a79f8;
                                    color: #fff;
                                    padding: 5px 15px;
                                    border: 2px;
                                    border-radius: 8px;
                                    font-size: 11px;
                                    height: 20px;
                                    font-weight: bold;
                                    margin: 10px 5px;
                                }
                                
                                QPushButton:hover {
                                    background-color: #fff;
                                    color: #0a79f8
                                }
        
                                QPushButton:pressed {
                                    background-color: #6703c5;
                                    color: #fff;
                                }
        
                                QTableWidget {
                                    border: 1px solid #000000;
                                }
        
                                QTableWidget QHeaderView::section {
                                    background-color: #575a5f;
                                    color: #fff;
                                    padding: 5px;
                                    height: 18px;
                                }
        
                                QTableWidget QHeaderView::section:horizontal {
                                    border-top: 1px solid #333;
                                }
                                
                                QTableWidget::item {
                                    color: #EEEEEE;
                                }
        
                                QTableWidget::item:selected {
                                    background-color: #000000;
                                    color: #fff;
                                    font-weight: bold;
                                }        
                            """)

    def executar_consulta_estrutura(self, module_object, table):
        item_selecionado = table.currentItem()
        codigo, descricao = None, None

        if item_selecionado:
            header = table.horizontalHeader()
            codigo_col, descricao_col = None, None

            for col in range(header.count()):
                header_text = table.horizontalHeaderItem(col).text().lower()
                if header_text == 'código':
                    codigo_col = col
                elif header_text == 'descrição':
                    descricao_col = col

                if codigo_col is not None and descricao_col is not None:
                    codigo = table.item(item_selecionado.row(), codigo_col).text()
                    self.codigo_pai = codigo
                    descricao = table.item(item_selecionado.row(), descricao_col).text()
                    self.descricao = descricao
                    self.module_object = module_object

                if codigo not in module_object.guias_abertas and codigo is not None:
                    module_object.guias_abertas.append(codigo)
                    if not module_object.existe_guias_abertas():
                        # Se não houver guias abertas, adicione a guia ao layout principal
                        module_object.layout().addWidget(module_object.tabWidget)
                        module_object.tabWidget.setVisible(True)

                    try:
                        if not self.criar_dataframe():
                            return
                        self.configurar_tabela()
                        self.populate_table()
                        self.configurar_layout()

                        module_object.tabWidget.addTab(self.nova_guia_estrutura, f"ESTRUTURA - {self.codigo_pai}")
                        module_object.tabWidget.setCurrentIndex(module_object.tabWidget.indexOf(
                            self.nova_guia_estrutura))

                    except pyodbc.Error as ex:
                        print(f"Falha na consulta de estrutura. Erro: {str(ex)}")

                    finally:
                        if 'engine' in locals():
                            self.engine.dispose()

    def criar_dataframe(self, revision=None):
        conn_str = (f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};'
                    f'UID={self.username};PWD={self.password}')
        self.engine = create_engine(f'mssql+pyodbc:///?odbc_connect={conn_str}')
        self.query = self.query_estrutura(revision)
        self.df = pd.read_sql(self.query, self.engine)
        self.df.insert(5, 'Desenho PDF', '')

        if self.df.empty:
            QMessageBox.information(None, "Atenção", f"{self.codigo_pai}\n\n"
                                                     f"Estrutura não encontrada.\n\nEureka®")
            if revision is not None:
                self.combobox_revisao.setCurrentText(self.last_revision)

        return False if self.df.empty else True

    def populate_table(self):
        for i, row in self.df.iterrows():
            self.tabela.insertRow(i)
            for column_name, value in row.items():
                if column_name == 'Quantidade':
                    valor_formatado = locale.format_string("%.2f", value, grouping=True)
                elif column_name == 'Inserido em:':
                    data_obj = datetime.strptime(value, "%Y%m%d")
                    valor_formatado = data_obj.strftime("%d/%m/%Y")
                elif column_name == 'Bloqueado?':  # Verifica se o valor é da coluna B1_MSBLQL
                    # Converte o valor 1 para 'Sim' e 2 para 'Não'
                    valor_formatado = 'Sim' if value == '1' else 'Não'
                else:
                    valor_formatado = str(value).strip()

                item = QTableWidgetItem(valor_formatado)
                item.setForeground(QColor("#EEEEEE"))  # Definir cor do texto da coluna quantidade

                if column_name not in ('Código', 'Descrição'):
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

                if column_name == 'Desenho PDF':
                    codigo_desenho = row['Código'].strip()
                    pdf_path = os.path.join(r"\\192.175.175.4\dados\EMPRESA\PROJETOS\PDF-OFICIAL",
                                            f"{codigo_desenho}.PDF")

                    if os.path.exists(pdf_path):
                        item.setBackground(self.COLOR_FILE_EXISTS)
                        item.setText('Sim')
                        item.setToolTip("Desenho encontrado")
                    else:
                        item.setBackground(self.COLOR_FILE_MISSING)
                        item.setText('Não')
                        item.setToolTip("Desenho não encontrado")

                self.tabela.setItem(i, self.df.columns.get_loc(column_name), item)

        self.tabela.setSortingEnabled(True)

        # Ajustar automaticamente a largura da coluna "Descrição"
        ajustar_largura_coluna_descricao(self.tabela)

    def alterar_quantidade_estrutura(self, codigo_pai, codigo_filho, quantidade):
        query_alterar_quantidade_estrutura = f"""
                UPDATE {self.database}.dbo.SG1010 
                SET G1_QUANT = {quantidade} 
                WHERE G1_COD = '{codigo_pai}' 
                AND G1_COMP = '{codigo_filho}'
                AND G1_REVFIM <> 'ZZZ' AND D_E_L_E_T_ <> '*'
                AND G1_REVFIM = (SELECT MAX(G1_REVFIM) FROM {self.database}.dbo.SG1010 
                WHERE G1_COD = '{codigo_pai}' 
                AND G1_REVFIM <> 'ZZZ' 
                AND D_E_L_E_T_ <> '*');
            """
        try:
            with pyodbc.connect(
                    f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};'
                    f'UID={self.username};PWD={self.password}') as conn:
                cursor = conn.cursor()
                cursor.execute(query_alterar_quantidade_estrutura)
                conn.commit()

        except Exception as ex:
            ctypes.windll.user32.MessageBoxW(0, f"Falha na conexão com o TOTVS ou consulta. Erro: {str(ex)}",
                                             "Erro de execução", 16 | 0)

    def handle_item_change(self, item, tabela, codigo_pai):
        if item.column() == 2:
            linha_selecionada = tabela.currentItem()

            codigo_filho = tabela.item(linha_selecionada.row(), 0).text()
            nova_quantidade = item.text()
            nova_quantidade = nova_quantidade.replace(',', '.')

            if nova_quantidade.replace('.', '', 1).isdigit():
                self.alterar_quantidade_estrutura(codigo_pai, codigo_filho, float(nova_quantidade))
            else:
                ctypes.windll.user32.MessageBoxW(
                    0,
                    "QUANTIDADE INVÁLIDA\n\nOs valores devem ser números, não nulos, sem espaços em branco e maiores "
                    "que zero.\nPor favor, corrija tente novamente!",
                    "SMARTPLIC®", 48 | 0)

    def get_last_revision(self, codigo):
        query = f"""
            SELECT 
                B1_REVATU 
            FROM 
                {self.database}.dbo.SB1010 
            WHERE 
                B1_COD = ?
            AND 
                D_E_L_E_T_ <> '*'"""
        try:
            with pyodbc.connect(
                    f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};'
                    f'PWD={self.password}') as conn:
                cursor = conn.cursor()
                result = cursor.execute(query, (codigo,)).fetchone()
                return result[0] if result else None
        except Exception as ex:
            exibir_mensagem("EUREKA® Engenharia", f'Falha ao consultar banco de dados - {ex}\n\n'
                                                  f'get_last_revision(self)', "error")

    def when_combobox_revisao_changed(self, index):
        selected_revision = self.combobox_revisao.itemText(index)
        self.update_table_with_revision(selected_revision)

    def update_table_with_revision(self, revision):
        if not self.criar_dataframe(revision=revision):
            return
        self.tabela.setRowCount(0)  # Limpar a tabela
        self.populate_table()

    def query_estrutura(self, revision=None):
        query = f"""
            SELECT 
                struct.G1_COMP AS "Código", 
                prod.B1_DESC AS "Descrição", 
                struct.G1_QUANT AS "Quantidade", 
                prod.B1_UM AS "Unid.",
                struct.G1_REVFIM AS "Revisão Final", 
                struct.G1_INI AS "Inserido em:",
                prod.B1_MSBLQL AS "Bloqueado?",
                prod.B1_ZZLOCAL AS "Endereço"
            FROM 
                {self.database}.dbo.SG1010 struct
            INNER JOIN 
                {self.database}.dbo.SB1010 prod
            ON 
                struct.G1_COMP = prod.B1_COD AND prod.D_E_L_E_T_ <> '*'
            WHERE 
                G1_COD = '{self.codigo_pai}'
                AND G1_REVFIM <> 'ZZZ' 
                AND struct.D_E_L_E_T_ <> '*' 
                ???
            ORDER BY 
                B1_DESC ASC;
        """
        if revision is None:
            revisao = f"""
                AND G1_REVFIM = (SELECT MAX(G1_REVFIM)
                FROM {self.database}.dbo.SG1010 WHERE G1_COD = '{self.codigo_pai}'
                AND G1_REVFIM <> 'ZZZ' AND D_E_L_E_T_ <> '*')"""
            return query.replace("???", revisao)
        else:
            return (query.replace("???", f"AND '{revision}' BETWEEN struct.G1_REVINI AND struct.G1_REVFIM ")
                    .replace("AND struct.D_E_L_E_T_ <> '*'", ""))
