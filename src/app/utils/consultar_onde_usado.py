import locale

import pyodbc
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QMessageBox, \
    QPushButton, QSizePolicy, QSpacerItem

from src.app.utils.db_mssql import setup_mssql
from src.app.utils.utils import ajustar_largura_coluna_descricao, copiar_linha, exportar_excel


def executar_consulta_onde_usado(self, table):
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

        if codigo not in self.guias_abertas_onde_usado:
            query_onde_usado = f"""
                    SELECT 
                        STRUT.G1_COD AS "Código", 
                        PROD.B1_DESC "Descrição",
                        STRUT.G1_QUANT AS "Quant. Usada",
                        STRUT.G1_XUM AS "Unid."
                    FROM 
                        {database}.dbo.SG1010 STRUT 
                    INNER JOIN 
                        {database}.dbo.SB1010 PROD 
                    ON 
                        STRUT.G1_COD = PROD.B1_COD 
                    WHERE G1_COMP = '{codigo}'
                        AND STRUT.G1_REVFIM = (
                            SELECT MAX(G1_REVFIM) 
                            FROM PROTHEUS12_R27.dbo.SG1010 
                            WHERE G1_COD = STRUT.G1_COD 
                            AND G1_REVFIM <> 'ZZZ' 
                            AND D_E_L_E_T_ <> '*')
                        AND STRUT.G1_REVFIM <> 'ZZZ' 
                        AND STRUT.D_E_L_E_T_ <> '*'
                        AND PROD.D_E_L_E_T_ <> '*'
                    ORDER BY B1_DESC ASC;
                """
            self.guias_abertas_onde_usado.append(codigo)
            conn = pyodbc.connect(
                f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
            try:
                cursor = conn.cursor()
                resultado = cursor.execute(query_onde_usado)

                if resultado.rowcount == 0:
                    QMessageBox.information(None, "Atenção", f"{codigo}\n\nNenhum item pai encontrado.\nEste item não "
                                                             "compõe nenhuma estrutura de produto.\n\nEureka®")
                    return

                nova_guia_estrutura = QWidget()
                layout_nova_guia_estrutura = QVBoxLayout()
                layout_cabecalho = QHBoxLayout()

                tabela = QTableWidget(nova_guia_estrutura)
                tabela.setSelectionBehavior(QTableWidget.SelectRows)
                tabela.setSelectionMode(QTableWidget.SingleSelection)

                tabela.setContextMenuPolicy(Qt.CustomContextMenu)
                tabela.customContextMenuRequested.connect(
                    lambda pos: self.show_context_menu(pos, tabela))

                tabela.setColumnCount(len(cursor.description))
                tabela.setHorizontalHeaderLabels([desc[0] for desc in cursor.description])

                # Tornar a tabela somente leitura
                tabela.setEditTriggers(QTableWidget.NoEditTriggers)

                # Configurar a fonte da tabela
                fonte_tabela = QFont("Segoe UI", 8)  # Substitua por sua fonte desejada e tamanho
                tabela.setFont(fonte_tabela)

                # Ajustar a altura das linhas
                altura_linha = 22  # Substitua pelo valor desejado
                tabela.verticalHeader().setDefaultSectionSize(altura_linha)

                for i, row in enumerate(cursor.fetchall()):
                    tabela.insertRow(i)
                    for j, value in enumerate(row):
                        valor_formatado = str(value).strip()
                        if j == 2:
                            valor_formatado = locale.format_string("%.2f", value, grouping=True)
                        item = QTableWidgetItem(valor_formatado)
                        if j != 0 and j != 1:
                            item.setTextAlignment(Qt.AlignCenter)

                        tabela.setItem(i, j, item)

                tabela.setSortingEnabled(True)

                # Ajustar automaticamente a largura da coluna "Descrição"
                ajustar_largura_coluna_descricao(tabela)

                btn_exportar_excel_estrutura = QPushButton("Exportar Excel", self)
                btn_exportar_excel_estrutura.clicked.connect(lambda: exportar_excel(self, tabela))
                btn_exportar_excel_estrutura.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

                select_product_label = QLabel(f'ONDE É USADO?\n\n{codigo}\t{descricao}')
                select_product_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

                layout_cabecalho.addWidget(select_product_label, alignment=Qt.AlignLeft)
                layout_cabecalho.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
                layout_cabecalho.addWidget(btn_exportar_excel_estrutura)

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

                self.tabWidget.addTab(nova_guia_estrutura, f"ONDE É USADO? - {codigo}")
                tabela.itemDoubleClicked.connect(copiar_linha)
                self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(nova_guia_estrutura))

            except pyodbc.Error as ex:
                print(f"Falha na consulta de estrutura. Erro: {str(ex)}")

            finally:
                conn.close()


driver = '{SQL Server}'
username, password, database, server = setup_mssql()
