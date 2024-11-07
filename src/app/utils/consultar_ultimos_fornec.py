import locale
from datetime import datetime

import pyodbc
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QTableWidgetItem, QTableWidget, QHeaderView, QHBoxLayout, QVBoxLayout, QWidget, \
    QMessageBox

from src.app.utils.db_mssql import setup_mssql
from src.app.utils.utils import copiar_linha, format_cnpj


def executar_ultimos_fornecedores(self, table):
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

        if codigo not in self.guias_abertas_ultimos_fornecedores and codigo is not None:
            query = f"""
                    SELECT 
                        A5_FORNECE AS "Cód. Forn.", 
                        A5_NOMEFOR AS "Razão Social",
                        FORN.A2_NREDUZ AS "Nome Fantasia",
                        FORN.A2_CGC AS "CNPJ",
                        A5_QUANT01 AS "Qtd. 1ª compra",
                        A5_QUANT02 AS "Qtd. 2ª compra",
                        A5_QUANT03 AS "Qtd. 3ª compra",
                        A5_PRECO01 AS "Preço 1ª compra",
                        A5_PRECO02 AS "Preço 2ª compra",
                        A5_PRECO03 AS "Preço 3ª compra",
                        A5_DTCOM01 AS "Data 1ª compra",
                        A5_DTCOM02 AS "Data 2ª compra",
                        A5_DTCOM03 AS "Data 3ª compra",
                        A5_CODPRF AS "Cód. no fornecedor"
                    FROM 
                        {database}.dbo.SA5010 FP
                    INNER JOIN
                        {database}.dbo.SA2010 FORN
                    ON
                        FP.A5_FORNECE = FORN.A2_COD 
                    WHERE 
                        A5_PRODUTO LIKE '{codigo}%'
                    ORDER BY FORN.A2_NREDUZ ASC;
                """
            self.guias_abertas_ultimos_fornecedores.append(codigo)
            conn = pyodbc.connect(
                f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
            try:
                cursor = conn.cursor()
                cursor.execute(query)

                if cursor.rowcount == 0:
                    QMessageBox.information(None, "Eureka® ", "Nenhum fornecedor não encontrado.")
                    return

                nova_guia_ult_forn = QWidget()
                layout_nova_guia_ult_forn = QVBoxLayout()
                layout_cabecalho = QHBoxLayout()

                tabela_ult_fornecedores = QTableWidget(nova_guia_ult_forn)

                tabela_ult_fornecedores.setColumnCount(len(cursor.description))
                tabela_ult_fornecedores.setHorizontalHeaderLabels(
                    [desc[0] for desc in cursor.description])

                tabela_ult_fornecedores.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

                # Tornar a tabela somente leitura
                tabela_ult_fornecedores.setEditTriggers(QTableWidget.NoEditTriggers)

                # Configurar a fonte da tabela1
                fonte_tabela = QFont("Segoe UI", 10)  # Substitua por sua fonte desejada e tamanho
                tabela_ult_fornecedores.setFont(fonte_tabela)

                # Ajustar a altura das linhas
                altura_linha = 20  # Substitua pelo valor desejado
                tabela_ult_fornecedores.verticalHeader().setDefaultSectionSize(altura_linha)

                for i, row in enumerate(cursor.fetchall()):
                    tabela_ult_fornecedores.insertRow(i)
                    for j, value in enumerate(row):
                        if j == 3:
                            value = format_cnpj(value)
                        elif j in (4, 5, 6, 7, 8, 9):
                            value = locale.format_string("%.2f", value, grouping=True)
                        elif j in (10, 11, 12) and not value.isspace():
                            data_obj = datetime.strptime(value, "%Y%m%d")
                            value = data_obj.strftime("%d/%m/%Y")

                        valor_formatado = str(value).strip()
                        item = QTableWidgetItem(valor_formatado)
                        item.setTextAlignment(Qt.AlignCenter)
                        tabela_ult_fornecedores.setItem(i, j, item)

                tabela_ult_fornecedores.setSortingEnabled(True)

                select_product_label = QLabel(f'ÚLTIMOS FORNECEDORES\n\n{codigo}\t{descricao}')
                select_product_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
                layout_cabecalho.addWidget(select_product_label,
                                           alignment=Qt.AlignCenter)
                layout_nova_guia_ult_forn.addLayout(layout_cabecalho)

                layout_nova_guia_ult_forn.addWidget(tabela_ult_fornecedores)
                nova_guia_ult_forn.setLayout(layout_nova_guia_ult_forn)

                nova_guia_ult_forn.setStyleSheet("""                                           
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

                self.tabWidget.addTab(nova_guia_ult_forn, f"Últimos Fornecedores - {codigo}")
                tabela_ult_fornecedores.itemDoubleClicked.connect(copiar_linha)
                self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(nova_guia_ult_forn))

            except pyodbc.Error as ex:
                print(f"Falha na consulta de estrutura. Erro: {str(ex)}")

            finally:
                conn.close()


driver = '{SQL Server}'
username, password, database, server = setup_mssql()
