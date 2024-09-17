import logging
import os
import sys
from functools import wraps

# Caminho absoluto para o diretório onde o módulo src está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt5 import QtWidgets

from app.utils.load_session import load_session


def authorize(allowed_roles, self):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                user_data = load_session()  # Load session data to get user role
                logging.debug(f"User data loaded: {user_data}")

                user_role = user_data.get('role')  # Assumes 'role' is in the session data
                logging.debug(f"User role: {user_role}")

                if user_role in allowed_roles:
                    logging.debug(f"Access granted for role: {user_role}")
                    return func(*args, **kwargs)  # User has the required role, proceed
                else:
                    logging.warning(f"Access denied for role: {user_role}")
                    QtWidgets.QMessageBox.warning(self, "Eureka® - Acesso negado",
                                                  "Desculpe, você não tem permissão para acessar este recurso.")
                    return None  # Access denied, do nothing
            except Exception as e:
                logging.error(f"Error during authorization: {e}")
                QtWidgets.QMessageBox.critical(None, "Error", f"An error occurred: {e}")
                return None

        return wrapper

    return decorator
