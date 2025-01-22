import sys
import os
# Caminho absoluto para o diretório onde o módulo src está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.app.utils.hierarquia_estrutura import BOMViewer as HierarquiaEstruturaWindow
from src.dialog.loading_dialog import loading_dialog


def abrir_hierarquia_estrutura(self, codigo_pai=None):
    if codigo_pai is None:
        selected_row_table = self.linha_selecionada()
        if selected_row_table:
            codigo_index = self.tree.horizontalHeaderItem(0).text().index("Código")
            codigo_pai = selected_row_table[codigo_index]  # Usa o índice encontrado
    dialog = loading_dialog(self, "Eureka® Engenharia", "🤖 Consultando dados...\n\nPor favor, aguarde!")
    hierarquia_estrutura_window = HierarquiaEstruturaWindow(codigo_pai)
    hierarquia_estrutura_window.showMaximized()
    dialog.close()
    hierarquia_estrutura_window.raise_()
    hierarquia_estrutura_window.activateWindow()
