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
        self.driver = '{SQL Server}'
        self.username, self.password, self.database, self.server = setup_mssql()

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
                    descricao = table.item(item_selecionado.row(), descricao_col).text()

                if codigo not in module_object.guias_abertas and codigo is not None:
                    select_query_estrutura = f"""
                            SELECT 
                                struct.G1_COMP AS "Código", 
                                prod.B1_DESC AS "Descrição", 
                                struct.G1_QUANT AS "Quantidade", 
                                prod.B1_UM AS "Unid.",
                                struct.G1_REVFIM AS "Revisão", 
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
                                G1_COD = '{codigo}' 
                                AND G1_REVFIM <> 'ZZZ' 
                                AND struct.D_E_L_E_T_ <> '*' 
                                AND G1_REVFIM = (SELECT MAX(G1_REVFIM) 
                                    FROM {self.database}.dbo.SG1010 WHERE G1_COD = '{codigo}' 
                                AND G1_REVFIM <> 'ZZZ' AND D_E_L_E_T_ <> '*')
                            ORDER BY 
                                B1_DESC ASC;
                        """
                    module_object.guias_abertas.append(codigo)
                    try:
                        conn_str = (f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};'
                                    f'UID={self.username};PWD={self.password}')
                        engine = create_engine(f'mssql+pyodbc:///?odbc_connect={conn_str}')
                        df = pd.read_sql(select_query_estrutura, engine)
                        df.insert(5, 'Desenho PDF', '')

                        if df.empty:
                            QMessageBox.information(None, "Atenção", f"{codigo}\n\nEstrutura não encontrada.\n\nEureka®")
                            return

                        nova_guia_estrutura = QWidget()
                        layout_nova_guia_estrutura = QVBoxLayout()
                        layout_cabecalho = QHBoxLayout()

                        tabela = QTableWidget(nova_guia_estrutura)
                        tabela.setSelectionBehavior(QTableWidget.SelectRows)
                        tabela.setSelectionMode(QTableWidget.SingleSelection)

                        tabela.setContextMenuPolicy(Qt.CustomContextMenu)
                        tabela.customContextMenuRequested.connect(
                            lambda pos: module_object.show_context_menu(pos, tabela))

                        tabela.setColumnCount(len(df.columns))
                        tabela.setHorizontalHeaderLabels(df.columns)

                        # Tornar a tabela somente leitura
                        tabela.setEditTriggers(QTableWidget.NoEditTriggers)

                        # Permitir edição apenas na coluna "Quantidade" (assumindo que "Quantidade" é a terceira coluna,
                        # índice 2)
                        tabela.setEditTriggers(QAbstractItemView.DoubleClicked)
                        tabela.setItemDelegateForColumn(df.columns.get_loc('Quantidade'), QItemDelegate(tabela))

                        # Configurar a fonte da tabela
                        fonte_tabela = QFont("Segoe UI", 8)  # Substitua por sua fonte desejada e tamanho
                        tabela.setFont(fonte_tabela)

                        # Ajustar a altura das linhas
                        tabela.verticalHeader().setDefaultSectionSize(22)

                        COLOR_FILE_EXISTS = QColor(51, 211, 145)  # green
                        COLOR_FILE_MISSING = QColor(201, 92, 118)  # light red

                        for i, row in df.iterrows():
                            tabela.insertRow(i)
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
                                        item.setBackground(COLOR_FILE_EXISTS)
                                        item.setText('Sim')
                                        item.setToolTip("Desenho encontrado")
                                    else:
                                        item.setBackground(COLOR_FILE_MISSING)
                                        item.setText('Não')
                                        item.setToolTip("Desenho não encontrado")

                                tabela.setItem(i, df.columns.get_loc(column_name), item)

                        tabela.setSortingEnabled(True)

                        # Ajustar automaticamente a largura da coluna "Descrição"
                        ajustar_largura_coluna_descricao(tabela)

                        layout_combobox = QHBoxLayout()

                        label_revisao = QLabel("Revisão:")
                        label_revisao.setObjectName("label_revisao")
                        combobox_revisao = QComboBox()
                        combobox_revisao.setEditable(False)
                        combobox_revisao.setObjectName("combobox_revisao")

                        revisao = self.get_last_revision(codigo)
                        revisao_int = int(revisao) if revisao else 0

                        items = []
                        for i in range(1, revisao_int + 1):
                            items.append(str(i).zfill(3))

                        items.sort(reverse=True)
                        combobox_revisao.clear()

                        for item in items:
                            combobox_revisao.addItem(item)

                        combobox_revisao.setCurrentIndex(0)
                        layout_combobox.addWidget(label_revisao)
                        layout_combobox.addWidget(combobox_revisao)

                        codigo_pai = codigo
                        btn_estrutura_explodida = QPushButton("Consultar estrutura explodida", module_object)
                        btn_estrutura_explodida.clicked.connect(lambda: abrir_hierarquia_estrutura(self, codigo_pai))
                        btn_estrutura_explodida.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

                        btn_exportar_excel = QPushButton("Exportar Excel", module_object)
                        btn_exportar_excel.clicked.connect(lambda: exportar_excel(self, tabela))
                        btn_exportar_excel.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

                        select_product_label = QLabel(f"Consulta de Estrutura \n\n{codigo}\t{descricao}")
                        select_product_label.setTextInteractionFlags(Qt.TextSelectableByMouse |
                                                                     Qt.TextSelectableByKeyboard)

                        layout_cabecalho.addWidget(select_product_label, alignment=Qt.AlignLeft)
                        layout_cabecalho.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
                        layout_cabecalho.addLayout(layout_combobox)
                        layout_cabecalho.addWidget(btn_estrutura_explodida)
                        layout_cabecalho.addWidget(btn_exportar_excel)

                        layout_nova_guia_estrutura.addLayout(layout_cabecalho)
                        layout_nova_guia_estrutura.addWidget(tabela)
                        nova_guia_estrutura.setLayout(layout_nova_guia_estrutura)

                        nova_guia_estrutura.setStyleSheet("""                                           
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

                        if not module_object.existe_guias_abertas():
                            # Se não houver guias abertas, adicione a guia ao layout principal
                            module_object.layout().addWidget(module_object.tabWidget)
                            module_object.tabWidget.setVisible(True)

                        module_object.tabWidget.addTab(nova_guia_estrutura, f"ESTRUTURA - {codigo}")
                        module_object.tabWidget.setCurrentIndex(module_object.tabWidget.indexOf(nova_guia_estrutura))
                        tabela.itemChanged.connect(
                            lambda item: self.handle_item_change(item, tabela, codigo))

                    except pyodbc.Error as ex:
                        print(f"Falha na consulta de estrutura. Erro: {str(ex)}")

                    finally:
                        if 'engine' in locals():
                            engine.dispose()

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
