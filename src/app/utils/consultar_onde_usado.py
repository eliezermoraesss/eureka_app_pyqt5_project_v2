import pyodbc
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel

from src.app.utils.db_mssql import setup_mssql
from src.app.utils.utils import ajustar_largura_coluna_descricao, copiar_linha


def executar_consulta_onde_usado(self, table):
    item_selecionado = table.currentItem()
    codigo, descricao = None, None

    if item_selecionado:
        header = table.horizontalHeader()
        codigo_col = None
        descricao_col = None

        for col in range(header.count()):
            header_text = table.horizontalHeaderItem(col).text()
            if header_text == 'Código':
                codigo_col = col
            elif header_text == 'Descrição':
                descricao_col = col

        if codigo_col is not None and descricao_col is not None:
            codigo = table.item(item_selecionado.row(), codigo_col).text()
            descricao = table.item(item_selecionado.row(), descricao_col).text()

        if codigo not in self.guias_abertas_onde_usado:
            query_onde_usado = f"""
                    SELECT 
                        STRUT.G1_COD AS "Código", 
                        PROD.B1_DESC "Descrição"
                    FROM 
                        {database}.dbo.SG1010 STRUT 
                    INNER JOIN 
                        {database}.dbo.SB1010 PROD 
                    ON 
                        G1_COD = B1_COD 
                    WHERE G1_COMP = '{codigo}' 
                        AND STRUT.G1_REVFIM <> 'ZZZ' 
                        AND STRUT.D_E_L_E_T_ <> '*'
                        AND PROD.D_E_L_E_T_ <> '*'
                    ORDER BY B1_DESC ASC;
                """
            self.guias_abertas_onde_usado.append(codigo)
            try:
                conn_estrutura = pyodbc.connect(
                    f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')

                cursor_estrutura = conn_estrutura.cursor()
                cursor_estrutura.execute(query_onde_usado)

                nova_guia_estrutura = QWidget()
                layout_nova_guia_estrutura = QVBoxLayout()
                layout_cabecalho = QHBoxLayout()

                tabela_onde_usado = QTableWidget(nova_guia_estrutura)

                tabela_onde_usado.setContextMenuPolicy(Qt.CustomContextMenu)
                tabela_onde_usado.customContextMenuRequested.connect(
                    lambda pos: self.show_context_menu(pos, tabela_onde_usado))

                tabela_onde_usado.setColumnCount(len(cursor_estrutura.description))
                tabela_onde_usado.setHorizontalHeaderLabels([desc[0] for desc in cursor_estrutura.description])

                # Tornar a tabela somente leitura
                tabela_onde_usado.setEditTriggers(QTableWidget.NoEditTriggers)

                # Configurar a fonte da tabela
                fonte_tabela = QFont("Segoe UI", 8)  # Substitua por sua fonte desejada e tamanho
                tabela_onde_usado.setFont(fonte_tabela)

                # Ajustar a altura das linhas
                altura_linha = 22  # Substitua pelo valor desejado
                tabela_onde_usado.verticalHeader().setDefaultSectionSize(altura_linha)

                for i, row in enumerate(cursor_estrutura.fetchall()):
                    tabela_onde_usado.insertRow(i)
                    for j, value in enumerate(row):
                        valor_formatado = str(value).strip()

                        item = QTableWidgetItem(valor_formatado)
                        tabela_onde_usado.setItem(i, j, item)

                tabela_onde_usado.setSortingEnabled(True)

                # Ajustar automaticamente a largura da coluna "Descrição"
                ajustar_largura_coluna_descricao(tabela_onde_usado)

                layout_cabecalho.addWidget(QLabel(f'Onde é usado?\n\n{codigo} - {descricao}'),
                                           alignment=Qt.AlignLeft)
                layout_nova_guia_estrutura.addLayout(layout_cabecalho)
                layout_nova_guia_estrutura.addWidget(tabela_onde_usado)
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

                self.tabWidget.addTab(nova_guia_estrutura, f"Onde é usado? - {codigo}")
                tabela_onde_usado.itemDoubleClicked.connect(copiar_linha)

            except pyodbc.Error as ex:
                print(f"Falha na consulta de estrutura. Erro: {str(ex)}")

            finally:
                self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(nova_guia_estrutura))
                conn_estrutura.close()


driver = '{SQL Server}'
username, password, database, server = setup_mssql()
