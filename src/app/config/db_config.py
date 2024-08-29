import os
import sqlite3


class DbConnection:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        database_path = os.path.abspath(os.path.join(base_dir, 'database', 'app.db'))

        os.makedirs(os.path.dirname(database_path), exist_ok=True)
        self.conn = sqlite3.connect(database_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              full_name TEXT NOT NULL,
                              username TEXT NOT NULL UNIQUE,
                              email TEXT NOT NULL UNIQUE,
                              hashed_password TEXT NOT NULL,
                              role TEXT NOT NULL,
                              created_at DATETIME NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS password_reset (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              user_id INTEGER,
                              reset_code TEXT NOT NULL,
                              expiration_time DATETIME NOT NULL)''')
        self.conn.commit()
