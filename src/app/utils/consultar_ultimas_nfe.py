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
                        D1_DTDIGIT AS "Data Entrada",
                        D1_DOC AS "Documento",
                        D1_SERIE AS "Série",
                        D1_PEDIDO AS "Pedido",
                        D1_FORNECE AS "Cód. Fornecedor",
                        FORN.A2_NOME AS "Fornecedor/Cliente",
                        D1_LOJA AS "Loja",
                        livroFiscal.F3_ESPECIE AS "Espécie",
                        D1_TIPO AS "Tipo NF",
                        D1_ITEM AS "Item NF",
                        D1_QUANT AS "Quant. NF",
                        D1_VUNIT AS "Vlr. Unitário",
                        D1_TOTAL AS "Vlr. Total",
                        D1_ITEMPC AS "Item Pedido",
                        D1_QTDPEDI AS "Quant. Pedido",
                        D1_EMISSAO AS "Data da emissão",
                        livroFiscal.F3_CHVNFE AS "Chave de acesso"
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
                    QMessageBox.information(None, "Eureka® ", "Nenhuma Nota Fiscal foi encontrada.")
                    return

                nova_guia = QWidget()
                layout_nova_guia = QVBoxLayout()
                layout_cabecalho = QHBoxLayout()

                tabela = QTableWidget(nova_guia)

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

                for i, row in enumerate(cursor.fetchall()):
                    tabela.insertRow(i)
                    for j, value in enumerate(row):
                        valor_formatado = str(value).strip()
                        item = QTableWidgetItem(valor_formatado)
                        item.setTextAlignment(Qt.AlignCenter)
                        tabela.setItem(i, j, item)

                tabela.setSortingEnabled(True)

                btn_exportar_excel_estrutura = QPushButton("Exportar Excel", self)
                btn_exportar_excel_estrutura.clicked.connect(lambda: exportar_excel(self, tabela))
                btn_exportar_excel_estrutura.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

                btn_visualizar_nfe = QPushButton("Visualizar Nota Fiscal", self)
                btn_visualizar_nfe.clicked.connect(lambda: visualizar_nfe(self, tabela))
                btn_visualizar_nfe.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

                layout_cabecalho.addWidget(QLabel(f'Histórico de compras - Últimas Notas Fiscais\n\n{codigo} - {descricao}'),
                                           alignment=Qt.AlignLeft)
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
                            background-color: #0066ff;
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
