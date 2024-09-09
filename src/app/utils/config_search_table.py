from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QHeaderView, QTableWidget


def config_search_table(self, table, dataframe):
    table.setColumnCount(len(dataframe.columns))
    table.setHorizontalHeaderLabels(dataframe.columns)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setSelectionMode(QTableWidget.SingleSelection)
    table.setFont(QFont(self.fonte_tabela, self.tamanho_fonte_tabela))
    table.verticalHeader().setDefaultSectionSize(self.altura_linha)
    table.horizontalHeader().sectionClicked.connect(order_column_table)


def order_column_table(self, logical_index):
    # Obter o índice real da coluna (considerando a ordem de classificação)
    index = self.ui.search_table.horizontalHeader().sortIndicatorOrder()
    # Definir a ordem de classificação
    order = Qt.AscendingOrder if index == 0 else Qt.DescendingOrder
    # Ordenar a tabela pela coluna clicada
    self.ui.search_table.sortItems(logical_index, order)
