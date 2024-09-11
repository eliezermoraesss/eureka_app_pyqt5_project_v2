import pyodbc
from PyQt5 import QtWidgets

from src.app.utils.db_mssql import setup_mssql
from src.app.utils.open_search_dialog import open_search_dialog
from src.app.utils.search_queries import select_query
from src.app.utils.utils import exibir_mensagem
from src.qt.ui.ui_edit_product_window import Ui_EditProductWindow


def execute_validate_query(entity, field):
    query = select_query(entity)
    query = query[1].replace(":search_field", f"{field}")  # Índice [1] filtra pelo código da entidade

    driver = '{SQL Server}'
    username, password, database, server = setup_mssql()
    try:
        with pyodbc.connect(
                f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}') as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            return result if result is not None else None

    except Exception as ex:
        exibir_mensagem(f"Eureka® - Falha ao conectar no banco de dados",
                        f"Erro ao consultar {field}.\n\n{str(ex)}\n\nContate o administrador do sistema.",
                        "error")


class EditarProdutoItemWindow(QtWidgets.QDialog):
    def __init__(self, selected_row_table):
        super(EditarProdutoItemWindow, self).__init__()

        self.required_field_is_blank = None
        self.selected_row_table = selected_row_table
        self.setFixedSize(640, 600)
        self.ui = Ui_EditProductWindow()
        self.ui.setupUi(self)
        self.required_fields = {
            "descricao": self.ui.descricao_field,
            "tipo": self.ui.tipo_field,
            "unidade_medida": self.ui.um_field,
            "armazem": self.ui.armazem_field,
            "centro_custo": self.ui.cc_field,
            "grupo": self.ui.grupo_field
        }
        self.init_ui()

    def init_ui(self):
        self.ui.type_label.setText(self.selected_row_table[0])
        self.ui.descricao_field.setText(self.selected_row_table[1])
        self.ui.desc_comp_field.setText(self.selected_row_table[2])
        self.ui.tipo_field.setText(self.selected_row_table[3])
        self.ui.um_field.setText(self.selected_row_table[4])
        self.ui.armazem_field.setText(self.selected_row_table[5])
        self.ui.cc_field.setText(self.selected_row_table[8])
        self.ui.grupo_field.setText(self.selected_row_table[6])
        self.ui.desc_grupo_field.setText(self.selected_row_table[7])
        self.ui.bloquear_combobox.setCurrentText(self.selected_row_table[9])
        self.ui.endereco_field.setText(self.selected_row_table[13])

        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self.update_product)
        self.ui.btn_search_tipo.clicked.connect(lambda: open_search_dialog("Tipo", self.ui.tipo_field, "tipo"))
        self.ui.btn_search_um.clicked.connect(
            lambda: open_search_dialog("Unidade de Medida", self.ui.um_field, "unidade_medida"))
        self.ui.btn_search_arm.clicked.connect(lambda: open_search_dialog("Armazém", self.ui.armazem_field, "armazem"))
        self.ui.btn_search_cc.clicked.connect(
            lambda: open_search_dialog("Centro de Custo", self.ui.cc_field, "centro_custo"))
        self.ui.btn_search_grupo.clicked.connect(lambda: open_search_dialog("Grupo", self.ui.grupo_field, "grupo"))

        self.ui.tipo_field.textChanged.connect(lambda: self.validate_required_fields("tipo", self.ui.tipo_field.text().upper()))
        self.ui.um_field.textChanged.connect(lambda: self.validate_required_fields("unidade_medida", self.ui.um_field.text().upper()))
        self.ui.armazem_field.textChanged.connect(lambda: self.validate_required_fields("armazem", self.ui.armazem_field.text().upper()))
        self.ui.cc_field.textChanged.connect(lambda: self.validate_required_fields("centro_custo", self.ui.cc_field.text().upper()))
        self.ui.grupo_field.textChanged.connect(lambda: self.validate_required_fields("grupo", self.ui.grupo_field.text().upper()))
        self.ui.grupo_field.textChanged.connect(self.on_grupo_field_changed)

    def validate_required_fields(self, entity, field):
        validated = execute_validate_query(entity, field)
        if validated is None:
            required_field = self.required_fields[entity]
            required_field.clear()
            exibir_mensagem("Eureka®", f"Nenhum resultado encontrado para o campo '{entity}' com o valor {field}", 'info')

    def on_grupo_field_changed(self, field_value):
        if field_value:
            self.fetch_group_description(field_value)

    def update_table(self):
        # Salvar os valores dos campos do formulário no atributo da classe 'selected_row_table' do tipo list []
        self.selected_row_table[1] = self.ui.descricao_field.text().upper()
        self.selected_row_table[2] = self.ui.desc_comp_field.text().upper()
        self.selected_row_table[3] = self.ui.tipo_field.text().upper()
        self.selected_row_table[4] = self.ui.um_field.text().upper()
        self.selected_row_table[5] = self.ui.armazem_field.text().upper()
        self.selected_row_table[6] = self.ui.grupo_field.text().upper()
        self.selected_row_table[7] = self.ui.desc_grupo_field.text().upper()
        self.selected_row_table[8] = self.ui.cc_field.text().upper()
        self.selected_row_table[9] = self.ui.bloquear_combobox.currentText()
        self.selected_row_table[13] = self.ui.endereco_field.text().upper()

    def verify_blank_required_fields(self):
        for field_name, field_object in self.required_fields.items():
            if not field_object.text():
                exibir_mensagem("Eureka®", f"O campo '{field_name}' é obrigatório e não pode estar vazio.", "info")
                self.required_field_is_blank = True
            else:
                self.required_field_is_blank = False

    def update_product(self):
        try:
            self.update_table()
            self.verify_blank_required_fields()
            if self.required_field_is_blank:
                return
            
            query = f"""
                UPDATE
                    PROTHEUS12_R27.dbo.SB1010 
                SET 
                    B1_DESC = N'{self.selected_row_table[1].ljust(100)}', -- 100
                    B1_XDESC2 = N'{self.selected_row_table[2].ljust(60)}', -- 60
                    B1_TIPO = N'{self.selected_row_table[3].ljust(2)}', -- 2
                    B1_UM = N'{self.selected_row_table[4].ljust(2)}', -- 2
                    B1_LOCPAD = N'{self.selected_row_table[5].ljust(2)}', -- 2
                    B1_GRUPO = N'{self.selected_row_table[6].ljust(4)}', -- 4
                    B1_ZZNOGRP = N'{self.selected_row_table[7].ljust(30)}', -- 30
                    B1_CC = N'{self.selected_row_table[8].ljust(9)}', -- 9
                    B1_MSBLQL = N'{'1' if self.selected_row_table[9] == 'Sim' else '2'}', -- 1
                    B1_ZZLOCAL = N'{self.selected_row_table[13].ljust(6)}' -- 6
                WHERE 
                    B1_COD LIKE '{self.selected_row_table[0]}%'
                """

            driver = '{SQL Server}'
            username, password, database, server = setup_mssql()
            with pyodbc.connect(
                    f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}') as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()

            # Fechar a janela após salvar
            self.accept()
        except Exception as ex:
            exibir_mensagem(f"Eureka® - Falha ao conectar no banco de dados",
                            f"Erro ao tentar alterar as informações do produto {self.selected_row_table[0]}.\n\n{str(ex)}\n\nContate o administrador do sistema.",
                            "error")

    def fetch_group_description(self, field_value):
        result = execute_validate_query("grupo", field_value)
        if result is not None:
            group_description = result[1].strip()
            self.ui.desc_grupo_field.setText(group_description)
        else:
            exibir_mensagem("Eureka®", f"Nenhum resultado encontrado para o campo 'Grupo' com o valor {field_value}", 'info')