import pandas as pd
import pyodbc
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QMessageBox
from sqlalchemy import create_engine

from src.app.utils.config_search_table import config_search_table
from src.app.utils.db_mssql import setup_mssql
from src.app.utils.search_queries import select_query
from src.qt.ui.ui_search_window import Ui_SearchWindow


class SearchWindow(QDialog):
    def __init__(self, entity_name, entity, nome_coluna=None, parent=None):
        super(SearchWindow, self).__init__(parent)
        self.entity_name = entity_name
        self.engine = None
        self.entity = entity
        self.selected_value = None
        self.nome_coluna = nome_coluna
        self.altura_linha = 30
        self.tamanho_fonte_tabela = 10
        self.fonte_tabela = 'Segoe UI'
        self.setFixedSize(640, 600)
        self.ui = Ui_SearchWindow()
        self.ui.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.ui.type_label.setText(self.entity_name)
        self.fill_search_table(self.entity)
        self.ui.search_table.itemDoubleClicked.connect(self.accept_selection)
        self.ui.btn_search.clicked.connect(self.get_parameters_values)
        self.ui.btn_ok.clicked.connect(self.accept_selection)
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.search_field.returnPressed.connect(self.get_parameters_values)
        self.ui.search_field.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Bloqueia o fechamento da janela e chama a função de busca
            event.accept()  # Impede o comportamento padrão (fechar a janela)
        else:
            super(SearchWindow, self).keyPressEvent(event)  # Executa o comportamento padrão para outras teclas

    def get_parameters_values(self):
        search_field = self.ui.search_field.text().upper().strip()
        criteria = self.ui.type_search_combobox.currentText().strip()
        self.fill_search_table(self.entity, search_field=search_field, criteria=criteria)

    def fill_search_table(self, entity, search_field=None, criteria=None):
        query = select_query(entity)
        if search_field is not None and criteria is not None:
            if criteria == 'Código':
                query = query[1]
            elif criteria == 'Descrição':
                query = query[2]
            query = query.replace(":search_field", f"{search_field}")
        else:
            query = query[0]

        driver = '{SQL Server}'
        username, password, database, server = setup_mssql()

        try:
            conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
            self.engine = create_engine(f'mssql+pyodbc:///?odbc_connect={conn_str}')
            dataframe = pd.read_sql(query, self.engine)

            if not dataframe.empty:
                config_search_table(self, self.ui.search_table, dataframe)
                self.ui.search_table.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
                self.ui.search_table.setRowCount(0)
            else:
                QMessageBox.information(self, "Eureka®", "Nenhum resultado encontrado!")
                return

            for i, row in dataframe.iterrows():
                self.ui.search_table.setSortingEnabled(False)
                self.ui.search_table.insertRow(i)
                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(value).strip())
                    if j == 0:
                        item.setTextAlignment(Qt.AlignCenter)
                    self.ui.search_table.setItem(i, j, item)
            self.ui.search_table.setSortingEnabled(True)

        except pyodbc.Error as ex:
            print(f"Falha na consulta. Erro: {str(ex)}")

        finally:
            if hasattr(self, 'engine'):
                self.engine.dispose()
                self.engine = None

    def accept_selection(self):
        selected_items = self.ui.search_table.selectedItems()
        if self.nome_coluna is None and selected_items:
            codigo = selected_items[0].text()  # Pega o código da primeira coluna
            self.selected_value = codigo
            self.accept()
        else:
            header_items = [self.ui.search_table.horizontalHeaderItem(i).text() for i in
                            range(self.ui.search_table.columnCount())]
            try:
                indice_coluna = header_items.index(self.nome_coluna)
                valor_campo = selected_items[indice_coluna].text()
                self.selected_value = valor_campo
                self.accept()
            except ValueError:
                QMessageBox.warning(None, 'Eureka® Search Window', f"Coluna '{self.nome_coluna}' não encontrada.")

    def get_selected_value(self):
        return getattr(self, 'selected_value', None)
