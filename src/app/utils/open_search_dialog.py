from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from src.app.views.search_window import SearchWindow


def open_search_dialog(entity_name, field, entity):
    dialog = SearchWindow(entity_name, entity)
    dialog.setWindowModality(Qt.ApplicationModal)
    if dialog.exec() == QDialog.Accepted:
        get_value = dialog.get_selected_value()
        if get_value:
            field.setText(get_value)
