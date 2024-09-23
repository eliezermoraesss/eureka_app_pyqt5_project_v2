import ctypes
from datetime import datetime

import pyodbc
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QAbstractItemView, QItemDelegate, \
    QTableWidgetItem, QPushButton, QSizePolicy, QLabel, QSpacerItem

from src.app.utils.db_mssql import setup_mssql
from src.app.utils.utils import ajustar_largura_coluna_descricao, exportar_excel


def executar_consulta_estrutura(self, table):
    item_selecionado = table.currentItem()
    header = table.horizontalHeader()
    codigo_col, descricao_col = None, None
    codigo = None
    descricao = None

    for col in range(header.count()):
        header_text = table.horizontalHeaderItem(col).text()
        if header_text == 'Código':
            codigo_col = col
        elif header_text == 'Descrição':
            descricao_col = col

        if codigo_col is not None and descricao_col is not None:
            codigo = table.item(item_selecionado.row(), codigo_col).text()
            descricao = table.item(item_selecionado.row(), descricao_col).text()

        if codigo not in self.guias_abertas and codigo is not None:
            select_query_estrutura = f"""
                    SELECT 
                        struct.G1_COMP AS "Código", 
                        prod.B1_DESC AS "Descrição", 
                        struct.G1_QUANT AS "Qtd..", 
                        struct.G1_XUM AS "Unid.", 
                        struct.G1_REVFIM AS "Revisão", 
                        struct.G1_INI AS "Inserido em:",
                        prod.B1_MSBLQL AS "Bloqueado?"
                    FROM 
                        {database}.dbo.SG1010 struct
                    INNER JOIN 
                        {database}.dbo.SB1010 prod
                    ON 
                        struct.G1_COMP = prod.B1_COD AND prod.D_E_L_E_T_ <> '*'
                    WHERE 
                        G1_COD = '{codigo}' 
                        AND G1_REVFIM <> 'ZZZ' 
                        AND struct.D_E_L_E_T_ <> '*' 
                        AND G1_REVFIM = (SELECT MAX(G1_REVFIM) FROM {database}.dbo.SG1010 WHERE G1_COD = '{codigo}' 
                        AND G1_REVFIM <> 'ZZZ' AND D_E_L_E_T_ <> '*')
                    ORDER BY 
                        B1_DESC ASC;
                """

            try:
                conn_estrutura = pyodbc.connect(
                    f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')

                cursor_estrutura = conn_estrutura.cursor()
                resultado = cursor_estrutura.execute(select_query_estrutura)

                nova_guia_estrutura = QWidget()
                layout_nova_guia_estrutura = QVBoxLayout()
                layout_cabecalho = QHBoxLayout()

                tree_estrutura = QTableWidget(nova_guia_estrutura)

                tree_estrutura.setContextMenuPolicy(Qt.CustomContextMenu)
                tree_estrutura.customContextMenuRequested.connect(
                    lambda pos: self.show_context_menu(pos, tree_estrutura))

                tree_estrutura.setColumnCount(len(cursor_estrutura.description))
                tree_estrutura.setHorizontalHeaderLabels([desc[0] for desc in cursor_estrutura.description])

                # Tornar a tabela somente leitura
                tree_estrutura.setEditTriggers(QTableWidget.NoEditTriggers)

                # Permitir edição apenas na coluna "Quantidade" (assumindo que "Quantidade" é a terceira coluna,
                # índice 2)
                tree_estrutura.setEditTriggers(QAbstractItemView.DoubleClicked)
                tree_estrutura.setItemDelegateForColumn(2, QItemDelegate(tree_estrutura))

                # Configurar a fonte da tabela
                fonte_tabela = QFont("Segoe UI", 8)  # Substitua por sua fonte desejada e tamanho
                tree_estrutura.setFont(fonte_tabela)

                # Ajustar a altura das linhas
                altura_linha = 22  # Substitua pelo valor desejado
                tree_estrutura.verticalHeader().setDefaultSectionSize(altura_linha)

                for i, row in enumerate(resultado.fetchall()):
                    tree_estrutura.insertRow(i)
                    for j, value in enumerate(row):
                        if j == 2:
                            valor_formatado = "{:.2f}".format(float(value))
                        elif j == 5:
                            data_obj = datetime.strptime(value, "%Y%m%d")
                            valor_formatado = data_obj.strftime("%d/%m/%Y")
                        elif j == 6:  # Verifica se o valor é da coluna B1_MSBLQL
                            # Converte o valor 1 para 'Sim' e 2 para 'Não'
                            if value == '1':
                                valor_formatado = 'Sim'
                            else:
                                valor_formatado = 'Não'
                        else:
                            valor_formatado = str(value).strip()

                        item = QTableWidgetItem(valor_formatado)
                        item.setForeground(QColor("#EEEEEE"))  # Definir cor do texto da coluna quantidade

                        if j != 0 and j != 1:
                            item.setTextAlignment(Qt.AlignCenter)

                        tree_estrutura.setItem(i, j, item)

                tree_estrutura.setSortingEnabled(True)

                # Ajustar automaticamente a largura da coluna "Descrição"
                ajustar_largura_coluna_descricao(tree_estrutura)

                btn_exportar_excel_estrutura = QPushButton("Exportar Excel", self)
                btn_exportar_excel_estrutura.clicked.connect(lambda: exportar_excel(self, tree_estrutura))
                btn_exportar_excel_estrutura.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

                layout_cabecalho.addWidget(QLabel(f"CONSULTA DE ESTRUTURA \n\n{codigo} - {descricao}"),
                                           alignment=Qt.AlignLeft)
                layout_cabecalho.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
                layout_cabecalho.addWidget(btn_exportar_excel_estrutura)

                layout_nova_guia_estrutura.addLayout(layout_cabecalho)
                # layout_nova_guia_estrutura.addLayout(layout_buttons)
                layout_nova_guia_estrutura.addWidget(tree_estrutura)
                nova_guia_estrutura.setLayout(layout_nova_guia_estrutura)

                nova_guia_estrutura.setStyleSheet("""                                           
                        * {
                            background-color: #262626;
                        }

                        QLabel {
                            color: #A7A6A6;
                            font-size: 18px;
                            font-weight: bold;
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

                        QTableWidget::item:selected {
                            background-color: #0066ff;
                            color: #fff;
                            font-weight: bold;
                        }        
                    """)

                if not self.existe_guias_abertas():
                    # Se não houver guias abertas, adicione a guia ao layout principal
                    self.layout().addWidget(self.tabWidget)
                    self.tabWidget.setVisible(True)

                self.tabWidget.addTab(nova_guia_estrutura, f"{codigo}")

            except pyodbc.Error as ex:
                print(f"Falha na consulta de estrutura. Erro: {str(ex)}")

            finally:
                self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(nova_guia_estrutura))
                tree_estrutura.itemChanged.connect(
                    lambda item: handle_item_change(item, tree_estrutura, codigo))
                self.guias_abertas.append(codigo)
                conn_estrutura.close()


def alterar_quantidade_estrutura(codigo_pai, codigo_filho, quantidade):
    query_alterar_quantidade_estrutura = f"""
            UPDATE {database}.dbo.SG1010 
            SET G1_QUANT = {quantidade} 
            WHERE G1_COD = '{codigo_pai}' 
            AND G1_COMP = '{codigo_filho}'
            AND G1_REVFIM <> 'ZZZ' AND D_E_L_E_T_ <> '*'
            AND G1_REVFIM = (SELECT MAX(G1_REVFIM) FROM {database}.dbo.SG1010 
            WHERE G1_COD = '{codigo_pai}' 
            AND G1_REVFIM <> 'ZZZ' 
            AND D_E_L_E_T_ <> '*');
        """
    try:
        with pyodbc.connect(
                f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}') as conn:
            cursor = conn.cursor()
            cursor.execute(query_alterar_quantidade_estrutura)
            conn.commit()

    except Exception as ex:
        ctypes.windll.user32.MessageBoxW(0, f"Falha na conexão com o TOTVS ou consulta. Erro: {str(ex)}",
                                         "Erro de execução", 16 | 0)


def handle_item_change(item, tree_estrutura, codigo_pai):
    if item.column() == 2:
        linha_selecionada = tree_estrutura.currentItem()

        codigo_filho = tree_estrutura.item(linha_selecionada.row(), 0).text()
        nova_quantidade = item.text()
        nova_quantidade = nova_quantidade.replace(',', '.')

        if nova_quantidade.replace('.', '', 1).isdigit():
            alterar_quantidade_estrutura(codigo_pai, codigo_filho, float(nova_quantidade))
        else:
            ctypes.windll.user32.MessageBoxW(
                0,
                "QUANTIDADE INVÁLIDA\n\nOs valores devem ser números, não nulos, sem espaços em branco e maiores "
                "que zero.\nPor favor, corrija tente novamente!",
                "SMARTPLIC®", 48 | 0)


driver = '{SQL Server}'
username, password, database, server = setup_mssql()
