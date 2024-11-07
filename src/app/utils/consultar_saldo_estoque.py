import locale
from datetime import datetime

import pyodbc
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QTableWidgetItem, QTableWidget, QHeaderView, QHBoxLayout, QWidget, QVBoxLayout, \
    QMessageBox

from src.app.utils.db_mssql import setup_mssql
from src.app.utils.utils import copiar_linha


def executar_saldo_em_estoque(self, table):
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

        if codigo not in self.guias_abertas_saldo and codigo is not None:
            query_saldo = f"""
                    SELECT 
                        B2_QATU AS "Saldo Atual",
                        EST.B2_QATU - EST.B2_QEMP AS "Qtd. Disponível",
                        B2_QEMP AS "Qtd. Empenhada",
                        B2_SALPEDI AS "Qtd. Prev. Entrada",
                        PROD.B1_UM AS "Unid. Med.",
                        B2_VATU1 AS "Valor Saldo Atual (R$)", 
                        B2_CM1 AS "Custo Unit. (R$)",
                        B2_DMOV AS "Dt. Últ. Mov.", 
                        B2_HMOV AS "Hora Últ. Mov.",
                        B2_DINVENT AS "Dt. Últ. Inventário"
                    FROM 
                        {database}.dbo.SB2010 EST
                    INNER JOIN
                        {database}.dbo.SB1010 PROD
                    ON
                        PROD.B1_COD = EST.B2_COD 
                    WHERE 
                        B2_COD = '{codigo}';
                """
            self.guias_abertas_saldo.append(codigo)
            try:
                conn_saldo = pyodbc.connect(
                    f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')

                cursor_saldo_estoque = conn_saldo.cursor()
                cursor_saldo_estoque.execute(query_saldo)

                if cursor_saldo_estoque.rowcount == 0:
                    QMessageBox.information(None, "Eureka®", "Saldo estoque.")
                    return

                nova_guia_saldo = QWidget()
                layout_nova_guia_saldo = QVBoxLayout()
                layout_cabecalho = QHBoxLayout()

                tabela_saldo_estoque = QTableWidget(nova_guia_saldo)

                tabela_saldo_estoque.setColumnCount(len(cursor_saldo_estoque.description))
                tabela_saldo_estoque.setHorizontalHeaderLabels(
                    [desc[0] for desc in cursor_saldo_estoque.description])

                tabela_saldo_estoque.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

                # Tornar a tabela somente leitura
                tabela_saldo_estoque.setEditTriggers(QTableWidget.NoEditTriggers)

                # Configurar a fonte da tabela1
                fonte_tabela = QFont("Segoe UI", 10)  # Substitua por sua fonte desejada e tamanho
                tabela_saldo_estoque.setFont(fonte_tabela)

                # Ajustar a altura das linhas
                altura_linha = 20  # Substitua pelo valor desejado
                tabela_saldo_estoque.verticalHeader().setDefaultSectionSize(altura_linha)

                for i, row in enumerate(cursor_saldo_estoque.fetchall()):
                    tabela_saldo_estoque.insertRow(i)
                    for j, value in enumerate(row):

                        if j in (0, 1, 2, 3, 5, 6):
                            value = locale.format_string("%.2f", value, grouping=True)

                        elif j in (7, 9) and not value.isspace():
                            data_obj = datetime.strptime(value, "%Y%m%d")
                            value = data_obj.strftime("%d/%m/%Y")

                        valor_formatado = str(value).strip()
                        item = QTableWidgetItem(valor_formatado)
                        item.setTextAlignment(Qt.AlignCenter)
                        tabela_saldo_estoque.setItem(i, j, item)

                tabela_saldo_estoque.setSortingEnabled(True)

                select_product_label = QLabel(f'Saldos em Estoque\n\n{codigo}\t{descricao}')
                select_product_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
                layout_cabecalho.addWidget(select_product_label,
                                           alignment=Qt.AlignCenter)
                layout_nova_guia_saldo.addLayout(layout_cabecalho)
                layout_nova_guia_saldo.addWidget(tabela_saldo_estoque)
                nova_guia_saldo.setLayout(layout_nova_guia_saldo)

                nova_guia_saldo.setStyleSheet("""                                           
                        * {
                            background-color: #262626;
                        }

                        QLabel {
                            color: #EEEEEE;
                            font-size: 18px;
                            font-weight: bold;
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
                            background-color: #0066ff;
                            color: #fff;
                            font-weight: bold;
                        }        
                    """)

                if not self.existe_guias_abertas():
                    # Se não houver guias abertas, adicione a guia ao layout principal
                    self.layout().addWidget(self.tabWidget)
                    self.tabWidget.setVisible(True)

                self.tabWidget.addTab(nova_guia_saldo, f"Saldos em Estoque - {codigo}")
                tabela_saldo_estoque.itemDoubleClicked.connect(copiar_linha)

            except pyodbc.Error as ex:
                print(f"Falha na consulta de estrutura. Erro: {str(ex)}")

            finally:
                self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(nova_guia_saldo))
                conn_saldo.close()


driver = '{SQL Server}'
username, password, database, server = setup_mssql()
