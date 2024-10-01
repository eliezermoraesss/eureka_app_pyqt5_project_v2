from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from src.app.views.search_window import SearchWindow


def open_search_dialog(entity_name, field, entity, nome_coluna=None, parent=None):
    dialog = SearchWindow(entity_name, entity, nome_coluna)
    dialog.setWindowModality(Qt.ApplicationModal)
    if dialog.exec() == QDialog.Accepted:
        get_value = dialog.get_selected_value()
        if get_value:
            field.setText(get_value)
    if parent is not None:
        parent.dialog_open = False
