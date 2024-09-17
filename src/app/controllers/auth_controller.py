import base64
from pathlib import Path

import bcrypt
import random
from datetime import datetime, timedelta
from PyQt5.QtCore import QSettings
from app.config.db_config import DbConnection
from app.utils.email_service import send_email


class AuthController:
    def __init__(self):
        self.db_connection = DbConnection()

    def save_session(self, user_data):
        settings = QSettings("Enaplic", "EurekaApp")
        settings.setValue("username", user_data["username"])
        settings.setValue("email", user_data["email"])
        settings.setValue("role", user_data["role"])
        settings.setValue("full_name", user_data["full_name"])

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        # Armazenar o hash como string usando decode('utf-8')
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, hashed_password, password):
        # Converter a string de volta para bytes usando encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def create_user(self, full_name, username, email, password, role):
        if self.get_user_by_username(username):
            return False, "O nome de usuário já está em uso."
        if self.get_user_by_email(email):
            return False, "O e-mail já está em uso."

        hashed_password = self.hash_password(password)
        created_at = datetime.now()  # Captura a data e hora atuais
        cursor = self.db_connection.conn.cursor()
        cursor.execute('''INSERT INTO enaplic_management.dbo.eureka_users 
                          (full_name, username, email, hashed_password, role, created_at)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (full_name, username, email, hashed_password, role, created_at))
        self.db_connection.conn.commit()
        return True, "Usuário registrado com sucesso!"

    def get_user_by_username(self, username):
        cursor = self.db_connection.conn.cursor()
        cursor.execute("SELECT * FROM enaplic_management.dbo.eureka_users WHERE username = ?", (username,))
        return cursor.fetchone()

    def get_user_by_email(self, email):
        cursor = self.db_connection.conn.cursor()
        cursor.execute("SELECT * FROM enaplic_management.dbo.eureka_users WHERE email = ?", (email,))
        return cursor.fetchone()

    def generate_reset_code(self, email):
        user = self.get_user_by_email(email)
        if user:
            reset_code = str(random.randint(100000, 999999))
            minutes = 5
            expiration_time = datetime.now() + timedelta(minutes=minutes)
            cursor = self.db_connection.conn.cursor()
            cursor.execute('''INSERT INTO enaplic_management.dbo.eureka_password_reset 
                              (user_id, reset_code, expiration_time)
                              VALUES (?, ?, ?)''',
                           (user[0], reset_code, expiration_time))
            self.db_connection.conn.commit()
            subject = "🦾🤖 Eureka® BOT - Recuperação de senha solicitada 🔒"

            image_path = Path(__file__).resolve().parent.parent.parent / "resources" / "images" / "logo_enaplic.jpg"
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

            body = f"""
                <html>
                <body>
                    <h2 style="color: #4CAF50;">Recuperação de Senha 🔒</h2>
                    <p> 🤖 Prezado(a) {user[1].split(' ')[0]},</p>
                    <p>Recebemos uma solicitação para redefinir a senha associada ao seu acesso. Utilize o código abaixo para concluir o processo de recuperação de senha:</p>
                    <h2 style="color: #333333; background-color: #f2f2f2; padding: 10px; display: inline-block; border-radius: 5px;">{reset_code}</h2>
                    <p>Este código é válido por {minutes} minuto. Caso o tempo expire, será necessário solicitar um novo código.</p>
                    <p>Atenciosamente,</p>
                    <p><strong>🦾🤖 Eureka® BOT</strong></p>
                    <p>👨‍💻<i> Este e-mail foi gerado automaticamente e não há necessidade de respondê-lo.</i></p>
                    <br>
                    <img src="data:image/jpeg;base64,{encoded_image}" alt="Enaplic logo" width="200px">
                </body>
                </html>
                """

            send_email(subject, body, email)
            print(f'Send reset code {reset_code} to {email}')
            return True
        return False

    def verify_reset_code(self, email, code):
        user = self.get_user_by_email(email)
        if not user:
            return False, "Email inválido."

        cursor = self.db_connection.conn.cursor()
        cursor.execute('''SELECT TOP 1 reset_code, expiration_time AS value 
                          FROM enaplic_management.dbo.eureka_password_reset
                          WHERE user_id = ? ORDER BY id DESC''',
                       (user[0],))
        result = cursor.fetchone()

        if not result:
            return False, "Nenhum código de recuperação encontrado."

        if result[0] != code:
            return False, "Código inválido."

        if datetime.now() > datetime.fromisoformat(str(result[1])):
            return False, "O código expirou."

        return True, "Código verificado."

    def reset_password(self, email, new_password):
        user = self.get_user_by_email(email)
        if user:
            hashed_password = self.hash_password(new_password)
            cursor = self.db_connection.conn.cursor()
            cursor.execute('''UPDATE enaplic_management.dbo.eureka_users 
                              SET hashed_password = ? WHERE email = ?''',
                           (hashed_password, email))
            self.db_connection.conn.commit()
            return True
        return False

    def check_authorization(self, username, required_role):
        user = self.get_user_by_username(username)
        if user:
            user_role = user[5]
            if user_role == 'admin' or user_role == required_role:
                return True
        return False
