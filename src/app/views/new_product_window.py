from PyQt5 import QtWidgets

from src.app.utils.db_mssql import setup_mssql
from src.app.utils.insert_product import insert_product
from src.app.utils.load_session import load_session
from src.app.utils.open_search_dialog import open_search_dialog
from src.app.utils.utils import validate_required_fields, fetch_group_description
from src.qt.ui.ui_new_product_window import Ui_NewProductWindow


class NewProductWindow(QtWidgets.QDialog):
    def __init__(self):
        super(NewProductWindow, self).__init__()

        self.existe_cadastro = False
        self.driver = '{SQL Server}'
        self.username, self.password, self.database, self.server = setup_mssql()

        self.required_field_is_blank = False
        self.selected_row = []
        self.user_data = load_session()
        self.setFixedSize(640, 678)
        self.ui = Ui_NewProductWindow()
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
            "codigo": self.ui.codigo_field,
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
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(lambda: insert_product(self))
        self.ui.btn_search_tipo.clicked.connect(
            lambda: open_search_dialog("Tipo", self.ui.tipo_field, "tipo"))
        self.ui.btn_search_um.clicked.connect(
            lambda: open_search_dialog("Unidade de Medida", self.ui.um_field, "unidade_medida"))
        self.ui.btn_search_arm.clicked.connect(
            lambda: open_search_dialog("Armazém", self.ui.armazem_field, "armazem"))
        self.ui.btn_search_cc.clicked.connect(
            lambda: open_search_dialog("Centro de Custo", self.ui.cc_field, "centro_custo"))
        self.ui.btn_search_grupo.clicked.connect(lambda: open_search_dialog("Grupo", self.ui.grupo_field, "grupo"))

        self.ui.tipo_field.textChanged.connect(
            lambda: validate_required_fields(self,"tipo", self.ui.tipo_field.text().upper()))
        self.ui.um_field.textChanged.connect(
            lambda: validate_required_fields(self,"unidade_medida", self.ui.um_field.text().upper()))
        self.ui.armazem_field.textChanged.connect(
            lambda: validate_required_fields(self,"armazem", self.ui.armazem_field.text().upper()))
        self.ui.cc_field.textChanged.connect(
            lambda: validate_required_fields(self,"centro_custo", self.ui.cc_field.text().upper()))
        self.ui.grupo_field.textChanged.connect(self.on_grupo_field_changed)
        self.ui.grupo_field.textChanged.connect(
            lambda: validate_required_fields(self,"grupo", self.ui.grupo_field.text().upper()))

        self.ui.codigo_field.returnPressed.connect(lambda: insert_product(self))
        self.ui.descricao_field.returnPressed.connect(lambda: insert_product(self))
        self.ui.desc_comp_field.returnPressed.connect(lambda: insert_product(self))
        self.ui.tipo_field.returnPressed.connect(lambda: insert_product(self))
        self.ui.um_field.returnPressed.connect(lambda: insert_product(self))
        self.ui.armazem_field.returnPressed.connect(lambda: insert_product(self))
        self.ui.cc_field.returnPressed.connect(lambda: insert_product(self))
        self.ui.grupo_field.returnPressed.connect(lambda: insert_product(self))
        self.ui.endereco_field.returnPressed.connect(lambda: insert_product(self))
        self.ui.ncm_field.returnPressed.connect(lambda: insert_product(self))
        self.ui.peso_field.returnPressed.connect(lambda: insert_product(self))

    def on_grupo_field_changed(self, field_value):
        if field_value:
            fetch_group_description(self, field_value)
