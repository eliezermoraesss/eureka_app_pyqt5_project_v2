import os
import sqlite3


class SearchHistoryManager:
    def __init__(self, modulo_eureka, db_path='search_history.db'):
        app_data = os.getenv('LOCALAPPDATA') or os.path.expanduser('~\\AppData\\Roaming')

        # Determina o caminho do banco de dados
        self.db_path = os.path.join(app_data, 'Eureka', db_path)

        # Cria diretório se não existir
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self.modulo_eureka = modulo_eureka

        # Conecta ao banco de dados
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # Cria tabela de histórico se não existir
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS autocomplete_{modulo_eureka} (
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
            self.cursor.execute(f'''
                INSERT OR REPLACE INTO autocomplete_{self.modulo_eureka}
                (field_name, value) VALUES (?, ?)
            ''', (field_name, value))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao salvar histórico: {e}")

    def get_history(self, field_name):
        """Recupera histórico de um campo"""
        self.cursor.execute(f'''
            SELECT value FROM autocomplete_{self.modulo_eureka}
            WHERE field_name = ?
            ORDER BY timestamp DESC
        ''', (field_name,))
        return [row[0] for row in self.cursor.fetchall()]

    def clear_history(self, field_name=None):
        """Limpa histórico"""
        if field_name:
            self.cursor.execute(
                f'DELETE FROM autocomplete_{self.modulo_eureka} WHERE field_name = ?',
                (field_name,)
            )
        else:
            self.cursor.execute(f'DELETE FROM autocomplete_{self.modulo_eureka}')
        self.conn.commit()

    def __del__(self):
        """Fecha conexão com banco ao destruir objeto"""
        self.conn.close()
