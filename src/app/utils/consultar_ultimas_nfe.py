import locale
from datetime import datetime

import pyodbc
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QTableWidgetItem, QTableWidget, QHeaderView, QHBoxLayout, QVBoxLayout, QWidget, \
    QMessageBox, QPushButton, QSizePolicy, QSpacerItem

from src.app.utils.db_mssql import setup_mssql
from src.app.utils.utils import copiar_linha, exportar_excel
from src.app.utils.visualizar_nfe import visualizar_nfe


def consultar_ultimas_nfe(self, table):
    item_selecionado = table.currentItem()
    codigo, descricao = None, None

    if item_selecionado:
        header = table.horizontalHeader()
        codigo_col = None
        descricao_col = None

        for col in range(header.count()):
            header_text = table.horizontalHeaderItem(col).text().lower()
            if header_text == 'código':
                codigo_col = col
            elif header_text == 'descrição':
                descricao_col = col

        if codigo_col is not None and descricao_col is not None:
            codigo = table.item(item_selecionado.row(), codigo_col).text()
            descricao = table.item(item_selecionado.row(), descricao_col).text()

        if codigo not in self.guias_abertas_ultimas_nfe and codigo is not None:
            query = f"""
                    SELECT
                        D1_EMISSAO AS "Data da emissão",
                        D1_DTDIGIT AS "Data Entrada",
                        D1_DOC AS "Documento",
                        D1_SERIE AS "Série",
                        D1_PEDIDO AS "Pedido",
                        D1_FORNECE AS "Cód. Fornecedor",
                        FORN.A2_NOME AS "Fornecedor/Cliente",
                        D1_LOJA AS "Loja",
                        livroFiscal.F3_ESPECIE AS "Espécie",
                        D1_QUANT AS "Qtde NF",
                        D1_VUNIT AS "Valor Unitário",
                        D1_TOTAL AS "Valor Total",
                        livroFiscal.F3_CHVNFE AS "CHAVE DE ACESSO"
                    FROM 
                        {database}.dbo.SD1010 NFE
                    LEFT JOIN
                        {database}.dbo.SA2010 FORN
                    ON
                        FORN.A2_COD = NFE.D1_FORNECE
                    LEFT JOIN
                        {database}.dbo.SF3010 livroFiscal
                    ON
                        F3_NFISCAL = D1_DOC AND F3_CLIEFOR = D1_FORNECE
                    WHERE 
                        D1_COD LIKE '{codigo}%'
                        AND NFE.D_E_L_E_T_ <> '*'
                    ORDER BY 
                        NFE.R_E_C_N_O_ DESC;
                """
            self.guias_abertas_ultimas_nfe.append(codigo)
            conn = pyodbc.connect(
                f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
            try:
                cursor = conn.cursor()
                cursor.execute(query)

                if cursor.rowcount == 0:
                    QMessageBox.information(None, "Atenção", "Nenhuma Nota Fiscal foi encontrada.\n\nEureka®")
                    return

                nova_guia = QWidget()
                layout_nova_guia = QVBoxLayout()
                layout_cabecalho = QHBoxLayout()

                tabela = QTableWidget(nova_guia)
                tabela.setSelectionBehavior(QTableWidget.SelectRows)
                tabela.setSelectionMode(QTableWidget.SingleSelection)

                tabela.setContextMenuPolicy(Qt.CustomContextMenu)
                tabela.customContextMenuRequested.connect(
                    lambda pos: self.show_context_menu(pos, tabela))

                tabela.setColumnCount(len(cursor.description))
                tabela.setHorizontalHeaderLabels(
                    [desc[0] for desc in cursor.description])

                tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

                # Tornar a tabela somente leitura
                tabela.setEditTriggers(QTableWidget.NoEditTriggers)

                # Configurar a fonte da tabela1
                fonte_tabela = QFont("Segoe UI", 10)  # Substitua por sua fonte desejada e tamanho
                tabela.setFont(fonte_tabela)

                # Ajustar a altura das linhas
                altura_linha = 20  # Substitua pelo valor desejado
                tabela.verticalHeader().setDefaultSectionSize(altura_linha)

                column_names = [desc[0] for desc in cursor.description]

                for i, row in enumerate(cursor.fetchall()):
                    tabela.insertRow(i)
                    for column_index, column_name in enumerate(column_names):
                        value = row[column_index]
                        if column_name in ('Data Entrada', 'Data da emissão') and not value.isspace():
                            date_obj = datetime.strptime(value, "%Y%m%d")
                            value = date_obj.strftime('%d/%m/%Y')
                        elif column_name in ('Qtde NF', 'Valor Unitário', 'Valor Total'):
                            value = locale.format_string('%.2f', value, grouping=True)
                        elif column_name == 'Documento':
                            value = value.lstrip('0')

                        valor_formatado = str(value).strip()
                        item = QTableWidgetItem(valor_formatado)
                        if column_name == 'Fornecedor/Cliente':
                            item.setTextAlignment(Qt.AlignLeft)
                        elif column_name in ('Valor Unitário', 'Valor Total'):
                            item.setTextAlignment(Qt.AlignRight)
                        else:
                            item.setTextAlignment(Qt.AlignCenter)
                        tabela.setItem(i, column_index, item)

                tabela.setSortingEnabled(True)

                btn_exportar_excel_estrutura = QPushButton("Exportar Excel", self)
                btn_exportar_excel_estrutura.clicked.connect(lambda: exportar_excel(self, tabela))
                btn_exportar_excel_estrutura.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

                btn_visualizar_nfe = QPushButton("Visualizar Nota Fiscal", self)
                btn_visualizar_nfe.clicked.connect(lambda: visualizar_nfe(self, tabela))
                btn_visualizar_nfe.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

                select_product_label = QLabel(f'ÚLTIMAS NOTAS FISCAIS\n\n{codigo}\t{descricao}')
                select_product_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
                layout_cabecalho.addWidget(select_product_label, alignment=Qt.AlignLeft)
                layout_cabecalho.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
                layout_cabecalho.addWidget(btn_visualizar_nfe)
                layout_cabecalho.addWidget(btn_exportar_excel_estrutura)

                layout_nova_guia.addLayout(layout_cabecalho)
                layout_nova_guia.addWidget(tabela)
                nova_guia.setLayout(layout_nova_guia)

                nova_guia.setStyleSheet("""                                           
                        * {
                            background-color: #262626;
                        }

                        QLabel {
                            color: #EEEEEE;
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
                        
                        QTableWidget::item {
                            color: #EEEEEE;
                        }    

                        QTableWidget::item:selected {
                            background-color: #000000;
                            color: #fff;
                            font-weight: bold;
                        }        
                    """)

                if not self.existe_guias_abertas():
                    # Se não houver guias abertas, adicione a guia ao layout principal
                    self.layout().addWidget(self.tabWidget)
                    self.tabWidget.setVisible(True)

                self.tabWidget.addTab(nova_guia, f"Histórico de NFe - {codigo}")
                tabela.itemDoubleClicked.connect(copiar_linha)
                self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(nova_guia))

            except pyodbc.Error as ex:
                print(f"Falha na consulta de estrutura. Erro: {str(ex)}")

            finally:
                conn.close()


driver = '{SQL Server}'
username, password, database, server = setup_mssql()
