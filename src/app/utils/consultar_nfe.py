import locale

import pyodbc
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QTableWidgetItem, QTableWidget, QHeaderView, QHBoxLayout, QVBoxLayout, QWidget, \
    QMessageBox, QPushButton, QSizePolicy, QSpacerItem

from src.app.utils.db_mssql import setup_mssql
from src.app.utils.utils import copiar_linha, exportar_excel


def visualizar_nfe(self, table):
    item_selecionado = table.currentItem()
    documento, nome_fornec, cod_fornecedor, pedido = None, None, None, None

    if item_selecionado:
        header = table.horizontalHeader()
        documento_col = None
        nome_fornec_col = None
        cod_fornecedor_col = None
        pedido_col = None

        for col in range(header.count()):
            header_text = table.horizontalHeaderItem(col).text().lower()
            if header_text in ('documento', 'doc. nf entrada'):
                documento_col = col
            elif header_text in ('fornecedor/cliente', 'razão social fornecedor'):
                nome_fornec_col = col
            elif header_text == 'cód. fornecedor':
                cod_fornecedor_col = col
            elif header_text == 'pedido':
                pedido_col = col

        if documento_col is not None and nome_fornec_col is not None and cod_fornecedor_col is not None:
            documento = table.item(item_selecionado.row(), documento_col).text().zfill(9)
            nome_fornec = table.item(item_selecionado.row(), nome_fornec_col).text()
            cod_fornecedor = table.item(item_selecionado.row(), cod_fornecedor_col).text()
            pedido = table.item(item_selecionado.row(), pedido_col).text()

        if documento not in self.guias_abertas_visualizar_nfe and documento is not None:
            query = f"""
                    SELECT
                        D1_COD AS "Código",
                        D1_XDESCRI AS "Descrição do produto/serviço",
                        D1_ITEM AS "Item NF",
                        D1_XPOSIPI AS "NCM/SH",
                        D1_UM AS "Unid.",
                        D1_QUANT AS "Qtde",
                        D1_VUNIT AS "Valor Unitário",
                        D1_TOTAL AS "Valor Total",
                        D1_BASEICM AS "BC ICMS",
                        D1_VALICM AS "V. ICMS",
                        D1_VALIPI AS "V. IPI",
                        D1_PICM AS "ALIQ. ICMS",
                        D1_IPI AS "ALIQ. IPI",
                        D1_PEDIDO AS "Pedido"
                    FROM
                        {database}.dbo.SD1010 NFE
                    WHERE 
                        D1_DOC = '{documento}'
                        AND D1_FORNECE = '{cod_fornecedor}'
                        AND D1_PEDIDO = '{pedido}'
                        AND NFE.D_E_L_E_T_ <> '*'
                    ORDER BY 
                        D1_ITEM ASC;
                """
            self.guias_abertas_visualizar_nfe.append(documento)
            conn = pyodbc.connect(
                f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
            try:
                cursor = conn.cursor()
                cursor.execute(query)

                if cursor.rowcount == 0:
                    QMessageBox.information(None, "Atenção", f"{documento}\n\nNota fiscal não encontrada.\n\nEureka®")
                    return

                nova_guia = QWidget()
                layout_nova_guia = QVBoxLayout()
                layout_cabecalho = QHBoxLayout()

                tabela = QTableWidget(nova_guia)
                tabela.setSelectionBehavior(QTableWidget.SelectRows)
                tabela.setSelectionMode(QTableWidget.SingleSelection)

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
                altura_linha = 25  # Substitua pelo valor desejado
                tabela.verticalHeader().setDefaultSectionSize(altura_linha)

                column_names = [desc[0] for desc in cursor.description]

                for i, row in enumerate(cursor.fetchall()):
                    tabela.insertRow(i)
                    for column_index, column_name in enumerate(column_names):
                        value = row[column_index]
                        if (column_name in ('Qtde', 'Valor Unitário', 'Valor Total',
                                            'BC ICMS', 'V. ICMS', 'V. IPI', 'ALIQ. ICMS', 'ALIQ. IPI')):
                            value = locale.format_string('%.2f', value, grouping=True)
                        elif column_name == 'NCM/SH':
                            value = f'{value[:4]}.{value[4:6]}.{value[6:]}'  # NCM FORMAT 1234.56.78

                        valor_formatado = str(value).strip()
                        item = QTableWidgetItem(valor_formatado)
                        if column_name == 'Descrição do produto/serviço':
                            item.setTextAlignment(Qt.AlignLeft)
                        elif column_name in ('Valor Unitário', 'Valor Total',
                                             'BC ICMS', 'V. ICMS', 'V. IPI', 'ALIQ. ICMS', 'ALIQ. IPI'):
                            item.setTextAlignment(Qt.AlignRight)
                        else:
                            item.setTextAlignment(Qt.AlignCenter)
                        tabela.setItem(i, column_index, item)

                tabela.setSortingEnabled(True)

                btn_exportar_excel_estrutura = QPushButton("Exportar Excel", self)
                btn_exportar_excel_estrutura.clicked.connect(lambda: exportar_excel(self, tabela))
                btn_exportar_excel_estrutura.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

                select_product_label = QLabel(f'VISUALIZAÇÃO DA NOTA FISCAL\n\n'
                                              f'Fornecedor:\t{cod_fornecedor}\t{nome_fornec}\t\tDocumento:\t{documento.lstrip('0')}')
                select_product_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
                layout_cabecalho.addWidget(select_product_label, alignment=Qt.AlignLeft)
                layout_cabecalho.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
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

                self.tabWidget.addTab(nova_guia, f"NOTA FISCAL - {documento}")
                tabela.itemDoubleClicked.connect(copiar_linha)
                self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(nova_guia))

            except pyodbc.Error as ex:
                print(f"Falha na consulta de estrutura. Erro: {str(ex)}")

            finally:
                conn.close()


driver = '{SQL Server}'
username, password, database, server = setup_mssql()
