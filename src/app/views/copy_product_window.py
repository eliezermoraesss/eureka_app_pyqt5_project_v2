import pyodbc
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from src.app.utils.common_query import insert_query
from src.app.utils.db_mssql import setup_mssql
from src.app.utils.load_session import load_session
from src.app.utils.open_search_dialog import open_search_dialog
from src.app.utils.save_log_database import save_log_database
from src.app.utils.search_queries import select_query
from src.qt.ui.ui_copy_product_window import Ui_CopyProductWindow
from src.app.utils.utils import tratar_campo_codigo


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
        QMessageBox.warning(None, f"Eureka® - Falha ao conectar no banco de dados",
                            f"Erro ao consultar {field}.\n\n{str(ex)}\n\nContate o administrador do sistema.")


class CopyProdutoItemWindow(QtWidgets.QDialog):
    def __init__(self, selected_row):
        super(CopyProdutoItemWindow, self).__init__()

        self.selected_row = selected_row
        self.existe_cadastro = False
        self.driver = '{SQL Server}'
        self.username, self.password, self.database, self.server = setup_mssql()

        self.required_field_is_blank = False
        self.user_data = load_session()
        self.setFixedSize(640, 600)
        self.ui = Ui_CopyProductWindow()
        self.ui.setupUi(self)
        self.entity_names = {
            "codigo": "CÓDIGO",
            "descricao": "DESCRIÇÃO",
            "tipo": "TIPO",
            "unidade_medida": "UNID. MEDIDA",
            "armazem": "ARMAZÉM",
            "centro_custo": "CENTRO DE CUSTO",
            "grupo": "GRUPO"
        }
        self.required_fields = {
            "codigo": self.ui.codigo_field,
            "descricao": self.ui.descricao_field,
            "tipo": self.ui.tipo_field,
            "unidade_medida": self.ui.um_field,
            "armazem": self.ui.armazem_field,
            "centro_custo": self.ui.cc_field,
            "grupo": self.ui.grupo_field
        }
        self.init_ui()

    def init_ui(self):
        self.ui.descricao_field.setText(self.selected_row[1])
        self.ui.desc_comp_field.setText(self.selected_row[2])
        self.ui.tipo_field.setText(self.selected_row[3])
        self.ui.um_field.setText(self.selected_row[4])
        self.ui.armazem_field.setText(self.selected_row[5])
        self.ui.cc_field.setText(self.selected_row[8])
        self.ui.grupo_field.setText(self.selected_row[6])
        self.ui.desc_grupo_field.setText(self.selected_row[7])
        self.ui.bloquear_combobox.setCurrentText(self.selected_row[9])
        self.ui.endereco_field.setText(self.selected_row[13])

        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self.insert_product)
        self.ui.btn_search_tipo.clicked.connect(lambda: open_search_dialog("Tipo", self.ui.tipo_field, "tipo"))
        self.ui.btn_search_um.clicked.connect(
            lambda: open_search_dialog("Unidade de Medida", self.ui.um_field, "unidade_medida"))
        self.ui.btn_search_arm.clicked.connect(lambda: open_search_dialog("Armazém", self.ui.armazem_field, "armazem"))
        self.ui.btn_search_cc.clicked.connect(
            lambda: open_search_dialog("Centro de Custo", self.ui.cc_field, "centro_custo"))
        self.ui.btn_search_grupo.clicked.connect(lambda: open_search_dialog("Grupo", self.ui.grupo_field, "grupo"))

        self.ui.tipo_field.textChanged.connect(
            lambda: self.validate_required_fields("tipo", self.ui.tipo_field.text().upper()))
        self.ui.um_field.textChanged.connect(
            lambda: self.validate_required_fields("unidade_medida", self.ui.um_field.text().upper()))
        self.ui.armazem_field.textChanged.connect(
            lambda: self.validate_required_fields("armazem", self.ui.armazem_field.text().upper()))
        self.ui.cc_field.textChanged.connect(
            lambda: self.validate_required_fields("centro_custo", self.ui.cc_field.text().upper()))
        self.ui.grupo_field.textChanged.connect(self.on_grupo_field_changed)
        self.ui.grupo_field.textChanged.connect(
            lambda: self.validate_required_fields("grupo", self.ui.grupo_field.text().upper()))

        self.ui.codigo_field.returnPressed.connect(self.insert_product)
        self.ui.descricao_field.returnPressed.connect(self.insert_product)
        self.ui.desc_comp_field.returnPressed.connect(self.insert_product)
        self.ui.tipo_field.returnPressed.connect(self.insert_product)
        self.ui.um_field.returnPressed.connect(self.insert_product)
        self.ui.armazem_field.returnPressed.connect(self.insert_product)
        self.ui.cc_field.returnPressed.connect(self.insert_product)
        self.ui.grupo_field.returnPressed.connect(self.insert_product)
        self.ui.endereco_field.returnPressed.connect(self.insert_product)

    def validate_required_fields(self, entity, field):
        if field != '':
            validated = execute_validate_query(entity, field)
            if validated is None:
                required_field = self.required_fields[entity]
                required_field.clear()
                QMessageBox.information(self, "Eureka®",
                                        f"Nenhum resultado encontrado para o campo {self.entity_names[entity]} com o "
                                        f"valor {field}")
        elif entity == 'grupo':
            self.ui.desc_grupo_field.setText("")

    def on_grupo_field_changed(self, field_value):
        if field_value:
            self.fetch_group_description(field_value)

    def verify_blank_required_fields(self):
        self.required_field_is_blank = False
        for field_name, field_object in self.required_fields.items():
            if field_name != 'centro_custo' and not field_object.text():
                QMessageBox.information(self, 'Eureka®', f"O campo {self.entity_names[field_name]} é obrigatório e não "
                                                         f"pode estar vazio.")
                self.required_field_is_blank = True

    def verificar_se_existe_cadastro(self, codigo):
        try:
            with pyodbc.connect(
                    f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}') as conn:
                query = f"SELECT B1_COD FROM PROTHEUS12_R27.dbo.SB1010 WHERE B1_COD LIKE '{codigo}%' AND D_E_L_E_T_ <> '*';"
                cursor = conn.cursor()
                result = cursor.execute(query).fetchone()

                if result is not None:
                    QMessageBox.warning(None, f"Eureka® {codigo}", f"Já existe cadastro deste produto.\nVerifique e tente novamente!")
                    return True
                else:
                    return False

        except Exception as ex:
            QMessageBox.warning(self, f"Eureka® - Erro ao consultar banco de dados TOTVS",
                                f"Não foi possível obter última chave primária da tabela de produtos SB1010.\n\n{str(ex)}"
                                f"\n\nContate o administrador do sistema.")
            return None

    def insert_product(self):
        codigo = tratar_campo_codigo(self.ui.codigo_field)
        try:
            self.verify_blank_required_fields()
            if self.required_field_is_blank:
                return

            if self.verificar_se_existe_cadastro(codigo):
                return
            else:
                with pyodbc.connect(
                        f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}') as conn:
                    query = insert_query(self)
                    cursor = conn.cursor()
                    cursor.execute(query)
                    conn.commit()

                # Fechar a janela após salvar
                self.accept()
                log_description = f"Cadastro de novo produto"
                save_log_database(self.user_data, log_description, codigo)

                QMessageBox.information(self, f"Eureka® Engenharia",
                                        f"Produto cadastrado com sucesso!")

        except Exception as ex:
            QMessageBox.warning(self, f"Eureka® - Falha ao conectar no banco de dados",
                                f"Erro ao tentar cadastrar novo produto no TOTVS.\n\n{str(ex)}\n\nContate o "
                                f"administrador do sistema.")

    def fetch_group_description(self, field_value):
        result = execute_validate_query("grupo", field_value)
        if result is not None:
            group_description = result[1].strip()
            self.ui.desc_grupo_field.setText(group_description)
        else:
            QMessageBox.information(self, "Eureka®",
                                    f"Nenhum resultado encontrado para o campo GRUPO com o valor {field_value}")

    def nova_chave_primaria(self):
        try:
            with pyodbc.connect(
                    f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}') as conn:
                query = f"SELECT TOP 1 R_E_C_N_O_ FROM PROTHEUS12_R27.dbo.SB1010 ORDER BY R_E_C_N_O_ DESC;"
                cursor = conn.cursor()
                result = cursor.execute(query).fetchone()

                return result[0] + 1

        except Exception as ex:
            QMessageBox.warning(self, f"Eureka® - Erro ao consultar banco de dados TOTVS",
                                f"Não foi possível obter última chave primária da tabela de produtos SB1010.\n\n{str(ex)}"
                                f"\n\nContate o administrador do sistema.")
            return None
