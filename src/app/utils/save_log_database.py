import logging
import os
from datetime import datetime

import pyodbc
from PyQt5.QtWidgets import QMessageBox

from src.app.utils.db_mssql import setup_mssql

logging.basicConfig(
    filename='edit_product_error_log.log',  # Local log file for errors
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Network path for log storage
network_log_path = r'\\192.175.175.4\desenvolvimento\REPOSITORIOS\resources\logs'


def format_log_description(selected_row_before_changed, selected_row_after_changed):
    before_change = {}
    after_change = {}
    column_names = {
        1: 'Descricao: ',
        2: 'Desc. Compl.: ',
        3: 'Tipo: ',
        4: 'Unid. Med.: ',
        5: 'Armazem: ',
        6: 'Grupo: ',
        7: 'Desc. Grupo: ',
        8: 'Centro Custo: ',
        9: 'Bloqueio: ',
        13: 'Endereco: '
    }
    for value in selected_row_after_changed:
        if value not in selected_row_before_changed:
            index = selected_row_after_changed.index(value)
            after_change[index] = value
    for value in selected_row_before_changed:
        if value not in selected_row_after_changed:
            index = selected_row_before_changed.index(value)
            before_change[index] = value
    result = 'Antes:\n'
    for key, value in before_change.items():
        result += column_names[key] + value + '\n'
    result += '\nDepois:\n'
    for key, value in after_change.items():
        result += column_names[key] + value + '\n'
    return result


def save_log_database(user_data, selected_row_before_changed, selected_row_after_changed):
    full_name = user_data["full_name"]
    email = user_data["email"]
    user_role = user_data["role"]

    log_description = format_log_description(selected_row_before_changed, selected_row_after_changed)

    query = f"""
    INSERT INTO 
        enaplic_management.dbo.tb_user_logs 
        (full_name, email, user_role, part_number, log_description, created_at) 
    VALUES
        ('{full_name}', '{email}', '{user_role}', '{selected_row_after_changed[0]}', '{log_description}', switchoffset(sysdatetimeoffset(),'-03:00'));
    """

    driver = '{SQL Server}'
    username, password, database, server = setup_mssql()
    database = "enaplic_management"
    try:
        with pyodbc.connect(
                f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}') as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

        # Save log data to network location after successful database persistence
        save_to_network_log(user_data, log_description)

    except Exception as ex:
        conn.rollback()
        # Log the error locally
        logging.error(f"Error while inserting log entry: {log_description}. Exception: {str(ex)}")
        QMessageBox.warning(None, f"Eureka® - Erro",
                            f"Erro ao salvar log {user_data}\n{log_description}.\n\n{str(ex)}\n\nContate o administrador do sistema.")


def save_to_network_log(user_data, log_description):
    try:
        # Ensure the network path exists
        if not os.path.exists(network_log_path):
            os.makedirs(network_log_path)

        # Construct the log file path with the current date
        log_file = os.path.join(network_log_path, f"eureka_eng_edit_product_log_{datetime.now().strftime('%Y-%m-%d')}.txt")

        # Format the log entry
        log_entry = (f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                     f"Full Name: {user_data['full_name']}\n"
                     f"Email: {user_data['email']}\n"
                     f"Role: {user_data['role']}\n"
                     f"Log description:\n{log_description}\n\n")

        # Append log entry to the file
        with open(log_file, 'a', encoding='utf-8') as file:
            file.write(log_entry)

    except Exception as ex:
        # Log if there is any failure while writing to network location
        logging.error(f"Failed to write log to network location: {str(ex)}")

