import pyodbc
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from src.app.utils.db_mssql import setup_mssql
from src.app.utils.load_session import load_session
from src.app.utils.open_search_dialog import open_search_dialog
from src.app.utils.save_log_database import save_log_database
from src.app.utils.search_queries import select_query
from src.app.utils.utils import format_log_description, execute_validate_query, validar_ncm, validar_peso
from src.qt.ui.ui_edit_product_window import Ui_EditProductWindow


class EditarProdutoItemWindow(QtWidgets.QDialog):
    def __init__(self, selected_row):
        super(EditarProdutoItemWindow, self).__init__()

        self.required_field_is_blank = False
        self.selected_row = selected_row
        self.user_data = load_session()
        self.setFixedSize(640, 639)
        self.ui = Ui_EditProductWindow()
        self.ui.setupUi(self)
        self.entity_names = {
            "descricao": "DESCRIÇÃO",
            "tipo": "TIPO",
            "unidade_medida": "UNID. MEDIDA",
            "armazem": "ARMAZÉM",
            "centro_custo": "CENTRO DE CUSTO",
            "grupo": "GRUPO",
            "ncm": "NCM",
            "peso_liquido": "PESO LÍQUIDO"
        }
        self.required_fields = {
            "descricao": self.ui.descricao_field,
            "tipo": self.ui.tipo_field,
            "unidade_medida": self.ui.um_field,
            "armazem": self.ui.armazem_field,
            "centro_custo": self.ui.cc_field,
            "grupo": self.ui.grupo_field,
            "ncm": self.ui.ncm_field,
            "peso_liquido": self.ui.peso_field
        }
        self.init_ui()

    def init_ui(self):
        self.ui.type_label.setText(self.selected_row[0])
        self.ui.descricao_field.setText(self.selected_row[1])
        self.ui.desc_comp_field.setText(self.selected_row[2])
        self.ui.tipo_field.setText(self.selected_row[3])
        self.ui.um_field.setText(self.selected_row[4])
        self.ui.armazem_field.setText(self.selected_row[6])
        self.ui.cc_field.setText(self.selected_row[9])
        self.ui.grupo_field.setText(self.selected_row[7])
        self.ui.desc_grupo_field.setText(self.selected_row[8])
        self.ui.bloquear_combobox.setCurrentText(self.selected_row[10])
        self.ui.endereco_field.setText(self.selected_row[15])
        self.ui.ncm_field.setText(self.selected_row[16])
        self.ui.peso_field.setText(self.selected_row[17])

        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self.update_product)
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
        
        self.ui.descricao_field.returnPressed.connect(self.update_product)
        self.ui.desc_comp_field.returnPressed.connect(self.update_product)
        self.ui.tipo_field.returnPressed.connect(self.update_product)
        self.ui.um_field.returnPressed.connect(self.update_product)
        self.ui.armazem_field.returnPressed.connect(self.update_product)
        self.ui.cc_field.returnPressed.connect(self.update_product)
        self.ui.grupo_field.returnPressed.connect(self.update_product)
        self.ui.endereco_field.returnPressed.connect(self.update_product)
        self.ui.ncm_field.returnPressed.connect(self.update_product)
        self.ui.peso_field.returnPressed.connect(self.update_product)

    def validate_required_fields(self, entity, field):
        if field != '':
            validated = execute_validate_query(entity, field)
            if validated is None:
                required_field = self.required_fields[entity]
                required_field.clear()
                QMessageBox.information(self, "Eureka® Validação de campo",
                                        f"O valor {field} não é válido para o campo {self.entity_names[entity]}.")
        elif entity == 'grupo':
            self.ui.desc_grupo_field.setText("")

    def on_grupo_field_changed(self, field_value):
        if field_value:
            self.fetch_group_description(field_value)

    def update_table(self):
        # Salvar os valores dos campos do formulário no atributo da classe 'selected_row_table' do tipo list []
        self.selected_row[0] = self.ui.type_label.text().upper().strip()
        self.selected_row[1] = self.ui.descricao_field.text().upper().strip()
        self.selected_row[2] = self.ui.desc_comp_field.text().upper().strip()
        self.selected_row[3] = self.ui.tipo_field.text().upper().strip()
        self.selected_row[4] = self.ui.um_field.text().upper().strip()
        self.selected_row[6] = self.ui.armazem_field.text().upper().strip()
        self.selected_row[7] = self.ui.grupo_field.text().upper().strip()
        self.selected_row[8] = self.ui.desc_grupo_field.text().upper().strip()
        self.selected_row[9] = self.ui.cc_field.text().upper().strip()
        self.selected_row[10] = self.ui.bloquear_combobox.currentText()
        self.selected_row[15] = self.ui.endereco_field.text().upper().strip()
        self.selected_row[16] = self.ui.ncm_field.text().upper().strip()
        self.selected_row[17] = self.ui.peso_field.text().replace(',', '.').strip()

    def verify_blank_required_fields(self):
        self.required_field_is_blank = False
        for field_name, field_object in self.required_fields.items():
            if field_name != 'centro_custo' and not field_object.text():
                QMessageBox.information(self, 'Eureka®', f"O campo {self.entity_names[field_name]} é obrigatório e não "
                                                         f"pode estar vazio.")
                self.required_field_is_blank = True

    def update_product(self):
        try:
            ncm = self.ui.ncm_field.text()
            peso = self.ui.peso_field.text()

            if not validar_ncm(ncm):
                QMessageBox.information(self, "Eureka® Validação de campo",
                                        f"O NCM não existe!\nUtilize um código existente e tente novamente.")
                return

            if not validar_peso(peso):
                QMessageBox.information(self, "Eureka® Validação de campo",
                                        f"O Peso Líquido deve ser maior do que zero!")
                return

            selected_row_before_changed = self.selected_row.copy()
            self.update_table()
            selected_row_after_changed = self.selected_row
            self.verify_blank_required_fields()
            if self.required_field_is_blank:
                return

            query = f"""
                UPDATE
                    PROTHEUS12_R27.dbo.SB1010 
                SET
                    B1_DESC = ?,
                    B1_XDESC2 = ?,
                    B1_TIPO = ?,
                    B1_UM = ?,
                    B1_LOCPAD = ?,
                    B1_GRUPO = ?,
                    B1_ZZNOGRP = ?,
                    B1_CC = ?,
                    B1_MSBLQL = ?,
                    B1_ZZLOCAL = ?,
                    B1_POSIPI = ?,
                    B1_PESO = ?
                WHERE 
                    B1_COD = ?
                """
                
            data = [
                self.selected_row[1].ljust(100),
                self.selected_row[2].ljust(60),
                self.selected_row[3].ljust(2),
                self.selected_row[4].ljust(2),
                self.selected_row[6].ljust(2),
                self.selected_row[7].ljust(4),
                self.selected_row[8].ljust(30),
                self.selected_row[9].ljust(9),
                '1' if self.selected_row[10] == 'Sim' else '2',
                self.selected_row[15].ljust(6),
                self.selected_row[16].ljust(10),
                self.selected_row[17],
                self.selected_row[0]
            ]

            driver = '{SQL Server}'
            username, password, database, server = setup_mssql()
            with pyodbc.connect(
                    f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}') as conn:
                cursor = conn.cursor()
                cursor.execute(query, data)
                conn.commit()

            # Fechar a janela após salvar
            self.accept()

            log_description = "Alteração de produto\n" + format_log_description(selected_row_before_changed, selected_row_after_changed)
            save_log_database(self.user_data, log_description, selected_row_after_changed[0])

            QMessageBox.information(self, f"Eureka®",
                               f"Alteração realizada com sucesso!")

        except Exception as ex:
            QMessageBox.warning(self, f"Eureka® - Falha ao conectar no banco de dados",
                                f"Erro ao tentar alterar as informações do produto {self.selected_row[0]}.\n\n{str(ex)}\n\nContate o administrador do sistema.")

    def fetch_group_description(self, field_value):
        result = execute_validate_query("grupo", field_value)
        if result is not None:
            group_description = result[1].strip()
            self.ui.desc_grupo_field.setText(group_description)
        else:
            QMessageBox.information(self, "Eureka®",
                                    f"Nenhum resultado encontrado para o campo GRUPO com o valor {field_value}")
