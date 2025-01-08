import os
import sqlite3


class SearchHistoryManager:
    def __init__(self, db_path='search_history.db'):
        app_data = os.getenv('LOCALAPPDATA') or os.path.expanduser('~\\AppData\\Roaming')

        # Determina o caminho do banco de dados
        self.db_path = os.path.join(app_data, 'Eureka', db_path)

        # Cria diretório se não existir
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # Conecta ao banco de dados
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # Cria tabela de histórico se não existir
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                field_name TEXT,
                value TEXT,
                timestamp DATE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(field_name, value)
            )
        ''')
        self.conn.commit()

    def save_history(self, field_name, value):
        """Salva item no histórico"""
        if not value:  # Ignora valores vazios
            return
        try:
            # Remove duplicatas e insere novo item
            self.cursor.execute('''
                INSERT OR REPLACE INTO search_history
                (field_name, value) VALUES (?, ?)
            ''', (field_name, value))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao salvar histórico: {e}")

    def get_history(self, field_name):
        """Recupera histórico de um campo"""
        self.cursor.execute('''
            SELECT value FROM search_history
            WHERE field_name = ?
            ORDER BY timestamp DESC
        ''', (field_name,))
        return [row[0] for row in self.cursor.fetchall()]

    def clear_history(self, field_name=None):
        """Limpa histórico"""
        if field_name:
            self.cursor.execute(
                'DELETE FROM search_history WHERE field_name = ?',
                (field_name,)
            )
        else:
            self.cursor.execute('DELETE FROM search_history')
        self.conn.commit()

    def __del__(self):
        """Fecha conexão com banco ao destruir objeto"""
        self.conn.close()


class AutoCompleteFeature(self):
    object_fields = {
        "codigo": self.campo_codigo,
        "descricao": self.campo_descricao,
        "contem_descricao": self.campo_contem_descricao,
        "tipo": self.campo_tipo,
        "unid_medida": self.campo_um,
        "armazem": self.campo_armazem,
        "grupo": self.campo_grupo,
        "centro_custo": self.campo_cc
    }

    for label, field_name in [
        ("Código", "codigo"),
        ("Descrição", "descricao"),
        ("Contém Descrição", "contem_descricao"),
        ("Tipo", "tipo"),
        ("Unidade de Medida", "unid_medida"),
        ("Armazém", "armazem"),
        ("Grupo", "grupo"),
        ("Centro de Custo", "centro_custo")
    ]:
        completer = QCompleter()
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setModel(QStringListModel())
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