import os

import bcrypt
import random
import sqlite3
from datetime import datetime, timedelta


class AuthController:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        # Define o caminho para salvar o banco de dados na pasta database
        database_path = os.path.abspath(os.path.join(self.base_dir, '..', 'config', 'database', 'app.db'))

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

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    def verify_password(self, hashed_password, password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

    def create_user(self, full_name, username, email, password, role):
        if self.get_user_by_username(username):
            return False, "O nome de usuário já está em uso."
        if self.get_user_by_email(email):
            return False, "O e-mail já está em uso."

        hashed_password = self.hash_password(password)
        created_at = datetime.now()  # Captura a data e hora atuais
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO users (full_name, username, email, hashed_password, role, created_at)
                          VALUES (?, ?, ?, ?, ?, ?)''', (full_name, username, email, hashed_password, role, created_at))
        self.conn.commit()
        return True, "Usuário registrado com sucesso!"

    def get_user_by_username(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()

    def get_user_by_email(self, email):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        return cursor.fetchone()

    def generate_reset_code(self, email):
        user = self.get_user_by_email(email)
        if user:
            reset_code = str(random.randint(100000, 999999))
            expiration_time = datetime.now() + timedelta(seconds=10)
            cursor = self.conn.cursor()
            cursor.execute('''INSERT INTO password_reset (user_id, reset_code, expiration_time)
                              VALUES (?, ?, ?)''', (user[0], reset_code, expiration_time))
            self.conn.commit()
            self.send_reset_email(email, reset_code)
            return True
        return False

    def send_reset_email(self, email, reset_code):
        print(f'Send reset code {reset_code} to {email}')

    def verify_reset_code(self, email, code):
        user = self.get_user_by_email(email)
        if not user:
            return False, "Email inválido."

        cursor = self.conn.cursor()
        cursor.execute('''SELECT reset_code, expiration_time FROM password_reset
                          WHERE user_id = ? ORDER BY id DESC LIMIT 1''', (user[0],))
        result = cursor.fetchone()

        if not result:
            return False, "Nenhum código de recuperação encontrado."

        if result[0] != code:
            return False, "Código inválido."

        if datetime.now() > datetime.fromisoformat(result[1]):
            return False, "O código expirou."

        return True, "Código verificado."

    def reset_password(self, email, new_password):
        user = self.get_user_by_email(email)
        if user:
            hashed_password = self.hash_password(new_password)
            cursor = self.conn.cursor()
            cursor.execute('''UPDATE users SET hashed_password = ?
                              WHERE email = ?''', (hashed_password, email))
            self.conn.commit()
            return True
        return False

    def check_authorization(self, username, required_role):
        user = self.get_user_by_username(username)
        if user:
            user_role = user[5]
            if user_role == 'Admin' or user_role == required_role:
                return True
        return False