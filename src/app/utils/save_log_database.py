import pyodbc
from PyQt5.QtWidgets import QMessageBox

from src.app.utils.db_mssql import setup_mssql


def format_log_description(selected_row_before_changed, selected_row_after_changed):
    before_change = {}
    after_change = {}
    column_names = {
        1: 'Descrição: ',
        2: 'Desc. Compl.: ',
        3: 'Tipo: ',
        4: 'Unid. Med.: ',
        5: 'Armazém: ',
        6: 'Grupo: ',
        7: 'Desc. Grupo: ',
        8: 'Centro Custo: ',
        9: 'Bloqueio: ',
        13: 'Endereço: '
    }
    for value in selected_row_after_changed:
        if value not in selected_row_before_changed:
            index = selected_row_after_changed.index(value)
            after_change[index] = value
    for value in selected_row_before_changed:
        if value not in selected_row_after_changed:
            index = selected_row_before_changed.index(value)
            before_change[index] = value
    result = 'Before:\n'
    for key, value in before_change.items():
        result += column_names[key] + value + '\n'
    result += '\nAfter:\n'
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

    except Exception as ex:
        conn.rollback()
        QMessageBox.warning(None, f"Eureka® - Erro",
                            f"Erro ao salvar log {user_data}\n{log_description}.\n\n{str(ex)}\n\nContate o administrador do sistema.")
