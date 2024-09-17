import pyodbc
from app.utils.db_mssql import setup_mssql


class DbConnection:
    def __init__(self):
        username, password, database, server = setup_mssql()
        # String de conexão para MSSQL
        self.conn = pyodbc.connect(
            'DRIVER={SQL Server};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
            'Trusted_Connection=no;'
        )
