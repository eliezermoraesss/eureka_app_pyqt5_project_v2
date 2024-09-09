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
    table.horizontalHeader().setStretchLastSection(True)
