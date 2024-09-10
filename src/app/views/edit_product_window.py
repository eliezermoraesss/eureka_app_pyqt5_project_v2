from PyQt5 import QtWidgets

from src.app.utils.open_search_dialog import open_search_dialog
from src.qt.ui.ui_edit_product_window import Ui_EditProductWindow


class EditarProdutoItemWindow(QtWidgets.QDialog):
    def __init__(self, selected_row_table):
        super(EditarProdutoItemWindow, self).__init__()

        self.selected_row_table = selected_row_table
        self.setFixedSize(640, 600)
        self.ui = Ui_EditProductWindow()
        self.ui.setupUi(self)
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
        self.ui.btn_search_um.clicked.connect(lambda: open_search_dialog("Unidade de Medida", self.ui.um_field, "unidade_medida"))
        self.ui.btn_search_arm.clicked.connect(lambda: open_search_dialog("Armazém", self.ui.armazem_field, "armazem"))
        self.ui.btn_search_cc.clicked.connect(lambda: open_search_dialog("Centro de Custo", self.ui.cc_field, "centro_custo"))
        self.ui.btn_search_grupo.clicked.connect(lambda: open_search_dialog("Grupo", self.ui.grupo_field, "grupo"))

    def update_table(self):
        # Recupera os valores editados
        self.selected_row_table[1] = self.ui.descricao_field.text()
        self.selected_row_table[2] = self.ui.desc_comp_field.text()
        self.selected_row_table[3] = self.ui.tipo_field.text()
        self.selected_row_table[4] = self.ui.um_field.text()
        self.selected_row_table[5] = self.ui.armazem_field.text()
        self.selected_row_table[6] = self.ui.grupo_field.text()
        self.selected_row_table[8] = self.ui.cc_field.text()
        self.selected_row_table[9] = self.ui.bloquear_combobox.currentText()
        self.selected_row_table[13] = self.ui.endereco_field.text()

    def update_product(self):
        self.update_table()

        # Fechar a janela após salvar
        self.accept()
