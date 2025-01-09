from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtWidgets import QCompleter


class AutoCompleteManager:
    def __init__(self, history_manager):
        """
        Inicializa o gerenciador de autocompletes.

        :param history_manager: Um objeto responsável por gerenciar os históricos dos campos.
        """
        self.history_manager = history_manager
        self.fields = {}

    def setup_autocomplete(self, field_name_list, object_fields):
        for field_name in field_name_list:
            completer = QCompleter()
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setModel(QStringListModel())

            popup = completer.popup()
            popup.setStyleSheet("""
                   QListView {
                       background-color: #EEEEEE;
                       color: #000000;
                       font-size: 14px;
                       padding: 5px;
                       border: 1px solid #262626;
                       min-height: 100px;
                   }
                   QListView::item {
                       padding: 5px;
                       min-height: 25px;
                   }
                   QListView::item:selected {
                       background-color: #0a79f8;
                       color: #FFFFFF;
                   }""")

            object_fields[field_name].setCompleter(completer)

            # Atualizar completer com dados históricos
            self.update_completer(field_name, completer)

            # Guarda referências
            self.fields[field_name] = {
                'line_edit': object_fields[field_name],
                'completer': completer
            }

            # Conecta o sinal
            object_fields[field_name].returnPressed.connect(
                lambda fn=field_name: self.save_search_history(fn)
            )

    def update_completer(self, field_name, completer):
        """Atualiza a lista de sugestões do completer"""
        history = self.history_manager.get_history(field_name)
        completer.model().setStringList(history)
        completer.setMaxVisibleItems(20)

    def save_search_history(self, field_name):
        value = self.fields[field_name]['line_edit'].text()

        if value.strip():  # Verifica se não está vazio
            self.history_manager.save_history(field_name, value)

            # Atualiza completer do campo
            completer = self.fields[field_name]['completer']
            self.update_completer(field_name, completer)
