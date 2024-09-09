from PyQt5.QtWidgets import QDialog

from src.app.views.search_window import SearchWindow


def open_search_dialog(field, entity):
    dialog = SearchWindow(entity)
    if dialog.exec() == QDialog.Accepted:
        selected_code = dialog.get_selected_code()
        if selected_code:
            field.setText(selected_code)
