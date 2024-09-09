from PyQt5.QtWidgets import QMainWindow

from src.app.utils.open_search_dialog import open_search_dialog
from src.qt.ui.ui_edit_product_window import Ui_EditProductWindow


class EditarProdutoItemWindow(QMainWindow):
    def __init__(self):
        super(EditarProdutoItemWindow, self).__init__()

        self.linha_completa = None
        self.setFixedSize(640, 600)
        self.ui = Ui_EditProductWindow()
        self.ui.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.ui.btn_close.clicked.connect(self.close)
        self.ui.btn_save.clicked.connect(self.atualizar_produto)
        self.ui.btn_search_um.clicked.connect(lambda: open_search_dialog(self.ui.um_field, "unidade_medida"))

    def atualizar_produto(self):
        # Recupera os valores editados
        self.linha_completa[1] = self.line_edit_desc.text()
        self.linha_completa[2] = self.line_edit_desc_compl.text()
        self.linha_completa[3] = self.line_edit_tipo.text()
        self.linha_completa[4] = self.line_edit_unid_med.text()
        self.linha_completa[5] = self.line_edit_armazem.text()
        self.linha_completa[6] = self.line_edit_grupo.text()
        self.linha_completa[8] = self.line_edit_centro_custo.text()
        self.linha_completa[9] = self.line_edit_bloqueado.text()
        self.linha_completa[13] = self.line_edit_endereco.text()

        # Fechar a janela após salvar
        self.accept()
