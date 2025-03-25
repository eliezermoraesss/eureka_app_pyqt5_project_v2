import pyodbc
from PyQt5.QtWidgets import QMessageBox

from src.app.utils.common_query import insert_query
from src.app.utils.save_log_database import save_log_database
from src.app.utils.utils import tratar_campo_codigo, validar_ncm, validar_peso


def insert_product(self):
    codigo = tratar_campo_codigo(self.ui.codigo_field)
    ncm = self.ui.ncm_field.text()
    peso = self.ui.peso_field.text()
    try:
        self.verify_blank_required_fields()
        if self.required_field_is_blank:
            return

        if not validar_ncm(ncm):
            QMessageBox.information(self, "Eureka® Validação de campo",
                                    f"O NCM não existe!\nUtilize um código existente e tente novamente.")
            return

        if not validar_peso(peso):
            QMessageBox.information(self, "Eureka® Validação de campo",
                                    f"O Peso Líquido deve ser maior do que zero!")
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
        print(ex)
        QMessageBox.warning(self, f"Eureka® - Falha ao conectar no banco de dados",
                            f"Erro ao tentar cadastrar novo produto no TOTVS.\n\n{str(ex)}\n\nContate o "
                            f"administrador do sistema.")