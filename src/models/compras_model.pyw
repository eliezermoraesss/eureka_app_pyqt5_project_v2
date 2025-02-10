import locale
import os
import sys

# Caminho absoluto para o diretório onde o módulo src está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from datetime import datetime

import pandas as pd
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap, QIntValidator
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QTableWidget, QTableWidgetItem, QHeaderView, QStyle, QAction, QDateEdit, QLabel, \
    QSizePolicy, QTabWidget, QMenu, QDialog
from sqlalchemy import create_engine

from src.app.utils.consultar_onde_usado import executar_consulta_onde_usado
from src.app.utils.consultar_saldo_estoque import executar_saldo_em_estoque
from src.app.utils.consultar_ultimos_fornec import executar_ultimos_fornecedores
from src.app.utils.consultar_ultimas_nfe import consultar_ultimas_nfe
from src.app.utils.db_mssql import setup_mssql
from src.app.utils.load_session import load_session
from src.app.utils.utils import exibir_mensagem, copiar_linha, exportar_excel
from src.app.views.FilterDialog import FilterDialog
from src.app.utils.open_search_dialog import open_search_dialog
from src.dialog.loading_dialog import loading_dialog
from src.app.utils.consultar_nfe import visualizar_nfe
from src.app.utils.run_image_comparator import run_image_comparator_exe, run_image_comparator_model
from src.app.utils.autocomplete_feature import AutoCompleteManager
from src.app.utils.search_history_manager import SearchHistoryManager
from src.resources.styles.qss_compras import compras_qss
from src.app.views.solic_compras_window import SolicitacaoComprasWindow


class CustomLineEdit(QLineEdit):
    def __init__(self, entity_name, entity, nome_coluna=None, parent=None):
        super(CustomLineEdit, self).__init__(parent)
        self.entity_name = entity_name
        self.entity = entity
        self.nome_coluna = nome_coluna

    def mousePressEvent(self, event):
        # Chama a função open_search_dialog quando o QLineEdit for clicado
        open_search_dialog(self.entity_name, self, self.entity, self.nome_coluna, self.parentWidget())
        # Continue com o comportamento padrão
        super(CustomLineEdit, self).mousePressEvent(event)


def abrir_janela_solicitacao_compra():
    solic_window = SolicitacaoComprasWindow()
    solic_window.showMaximized()


class ComprasApp(QWidget):
    guia_fechada = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.filtro_dialog = None
        self.dataframe_original = None
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.lista_status_tabela = ['EM APROVAÇÃO', 'AGUARDANDO ENTREGA', 'ENTREGA PARCIAL',
                                    'PEDIDO ENCERRADO']

        user_data = load_session()
        username = user_data["username"]
        role = user_data["role"]

        self.username, self.password, self.database, self.server = setup_mssql()
        self.driver = '{SQL Server}'

        self.setWindowTitle(f"Eureka® Compras . {username} ({role})")
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

        self.engine = None
        self.dataframe = pd.DataFrame()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_enaplic_path = os.path.join(script_dir, '..', 'resources', 'images', 'LOGO.jpeg')
        self.logo_label = QLabel(self)
        self.logo_label.setObjectName('logo-enaplic')
        pixmap_logo = QPixmap(logo_enaplic_path).scaledToWidth(60)
        self.logo_label.setPixmap(pixmap_logo)
        self.logo_label.setAlignment(Qt.AlignRight)

        self.altura_linha = 30
        self.tamanho_fonte_tabela = 10
        self.fonte_tabela = 'Segoe UI'

        fonte_campos = "Segoe UI"
        tamanho_fonte_campos = 16

        self.table_area = QTableWidget(self)
        self.table_area.setColumnCount(0)
        self.table_area.setRowCount(0)
        self.table_area.setObjectName("table_area")

        self.tree = QTableWidget(self)
        self.tree.setColumnCount(0)
        self.tree.setRowCount(0)
        self.tree.setObjectName("result_table")
        self.tree.hide()

        self.nova_janela = None

        self.tabWidget = QTabWidget(self)  # Adicione um QTabWidget ao layout principal
        self.tabWidget.setTabsClosable(True)  # Adicione essa linha para permitir o fechamento de guias
        self.tabWidget.tabCloseRequested.connect(self.fechar_guia)
        self.tabWidget.setVisible(False)  # Inicialmente, a guia está invisível

        self.guias_abertas = []
        self.guias_abertas_onde_usado = []
        self.guias_abertas_saldo = []
        self.guias_abertas_ultimos_fornecedores = []
        self.guias_abertas_ultimas_nfe = []
        self.guias_abertas_visualizar_nfe = []

        self.label_line_number = QLabel("", self)
        self.label_line_number.setObjectName("label-line-number")
        self.label_line_number.setVisible(False)

        self.label_indicators = QLabel("", self)
        self.label_indicators.setObjectName("label-indicators")
        self.label_indicators.setVisible(False)
        self.label_indicators.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

        self.label_sc = QLabel("Solicitação de Compra:", self)
        self.label_sc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_pedido = QLabel("Pedido de Compra:", self)
        self.label_pedido.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_codigo = QLabel("Código:", self)
        self.label_codigo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_descricao_prod = QLabel("Descrição:", self)
        self.label_descricao_prod.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_contem_descricao_prod = QLabel("Contém na descrição:", self)
        self.label_contem_descricao_prod.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.label_qp = QLabel("Número da QP/QR:", self)
        self.label_qp.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_nf = QLabel("NF entrada:", self)
        self.label_nf.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_OP = QLabel("Número da OP:", self)
        self.label_OP.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_data_inicio = QLabel("A partir de:", self)
        self.label_data_fim = QLabel("Até:", self)
        self.label_armazem = QLabel("Armazém:", self)
        self.label_fornecedor = QLabel("Fornecedor (razão social):", self)
        self.label_nm_fantasia_forn = QLabel("Fornecedor (nome fantasia):", self)

        self.campo_sc = QLineEdit(self)
        self.campo_sc.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_sc.setMaxLength(6)
        self.campo_sc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.campo_sc.setValidator(QIntValidator(0, 999999, self))  # Aceitar somente números
        self.add_clear_button(self.campo_sc)

        self.campo_pedido = QLineEdit(self)
        self.campo_pedido.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_pedido.setMaxLength(6)
        self.campo_pedido.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.campo_pedido.setValidator(QIntValidator(0, 999999,self))
        self.add_clear_button(self.campo_pedido)

        self.campo_codigo = QLineEdit(self)
        self.campo_codigo.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_codigo.setMaxLength(13)
        self.campo_codigo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_clear_button(self.campo_codigo)

        self.campo_descricao = QLineEdit(self)
        self.campo_descricao.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_descricao.setMaxLength(60)
        self.campo_descricao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_clear_button(self.campo_descricao)

        self.campo_contem_descricao = QLineEdit(self)
        self.campo_contem_descricao.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_contem_descricao.setMaxLength(60)
        self.campo_contem_descricao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_clear_button(self.campo_contem_descricao)

        self.campo_qp = CustomLineEdit('QPS', 'qps', 'Código', self)
        self.campo_qp.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_qp.setMaxLength(6)
        self.campo_qp.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_clear_button(self.campo_qp)

        self.campo_doc_nf = QLineEdit(self)
        self.campo_doc_nf.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_doc_nf.setMaxLength(9)
        self.campo_doc_nf.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.campo_doc_nf.setValidator(QIntValidator(0, 999999999,self))
        self.add_clear_button(self.campo_doc_nf)

        self.campo_OP = QLineEdit(self)
        self.campo_OP.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_OP.setMaxLength(6)
        self.campo_OP.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.campo_OP.setValidator(QIntValidator(0, 999999,self))
        self.add_clear_button(self.campo_OP)

        self.campo_armazem = CustomLineEdit('Armazém', 'armazem', 'Código', self)
        self.campo_armazem.setMaxLength(2)
        self.campo_armazem.setObjectName('armazem')
        self.campo_armazem.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        # self.add_clear_button(self.campo_armazem)

        self.campo_razao_social_fornecedor = CustomLineEdit('Fornecedor', 'fornecedor', 'Razão social', self)
        self.campo_razao_social_fornecedor.setObjectName("forn-raz")
        self.campo_razao_social_fornecedor.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_razao_social_fornecedor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.campo_razao_social_fornecedor.setMaxLength(40)
        # self.add_clear_button(self.campo_razao_social_fornecedor)

        self.campo_nm_fantasia_fornecedor = CustomLineEdit('Fornecedor', 'fornecedor', 'Nome fantasia', self)
        self.campo_nm_fantasia_fornecedor.setObjectName("forn-fantasia")
        self.campo_nm_fantasia_fornecedor.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_nm_fantasia_fornecedor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.campo_nm_fantasia_fornecedor.setMaxLength(20)
        # self.add_clear_button(self.campo_nm_fantasia_fornecedor)

        self.campo_data_inicio = QDateEdit(self)
        self.campo_data_inicio.setFont(QFont(fonte_campos, 10))
        self.campo_data_inicio.setFixedWidth(150)
        self.campo_data_inicio.setCalendarPopup(True)
        self.campo_data_inicio.setDisplayFormat("dd/MM/yyyy")

        data_atual = QDate.currentDate()
        intervalo_meses = 12
        data_inicio = data_atual.addMonths(-intervalo_meses)
        self.campo_data_inicio.setDate(data_inicio)
        self.add_today_button(self.campo_data_inicio)

        self.campo_data_fim = QDateEdit(self)
        self.campo_data_fim.setFont(QFont(fonte_campos, 10))
        self.campo_data_fim.setFixedWidth(150)
        self.campo_data_fim.setCalendarPopup(True)
        self.campo_data_fim.setDisplayFormat("dd/MM/yyyy")
        self.campo_data_fim.setDate(QDate().currentDate())
        self.add_today_button(self.campo_data_fim)

        self.btn_consultar = QPushButton("Pesquisar", self)
        self.btn_consultar.clicked.connect(self.btn_pesquisar)
        self.btn_consultar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_onde_e_usado = QPushButton("Onde é usado?", self)
        self.btn_onde_e_usado.clicked.connect(lambda: executar_consulta_onde_usado(self, self.tree))
        self.btn_onde_e_usado.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_onde_e_usado.hide()

        self.btn_saldo_estoque = QPushButton("Saldos em Estoque", self)
        self.btn_saldo_estoque.clicked.connect(lambda: executar_saldo_em_estoque(self, self.tree))
        self.btn_saldo_estoque.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_saldo_estoque.hide()

        self.btn_ultimos_fornecedores = QPushButton("Últimos Fornecedores", self)
        self.btn_ultimos_fornecedores.clicked.connect(lambda: executar_ultimos_fornecedores(self, self.tree))
        self.btn_ultimos_fornecedores.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_ultimos_fornecedores.hide()

        self.btn_ultimas_nfe = QPushButton("Últimas Notas Fiscais", self)
        self.btn_ultimas_nfe.clicked.connect(lambda: consultar_ultimas_nfe(self, self.tree))
        self.btn_ultimas_nfe.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_ultimas_nfe.hide()

        self.btn_visualizar_nf = QPushButton("Visualizar Nota Fiscal", self)
        self.btn_visualizar_nf.clicked.connect(lambda: visualizar_nfe(self, self.tree))
        self.btn_visualizar_nf.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_visualizar_nf.hide()

        self.btn_limpar_filtro = QPushButton("Limpar filtros", self)
        self.btn_limpar_filtro.clicked.connect(self.limpar_filtros)
        self.btn_limpar_filtro.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_limpar_filtro.hide()

        self.btn_limpar = QPushButton("Limpar", self)
        self.btn_limpar.clicked.connect(self.clean_screen)
        self.btn_limpar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_nova_janela = QPushButton("Nova Janela", self)
        self.btn_nova_janela.clicked.connect(self.abrir_nova_janela)
        self.btn_nova_janela.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_solic_compra = QPushButton("Solicitação de Compra", self)
        self.btn_solic_compra.clicked.connect(abrir_janela_solicitacao_compra)
        self.btn_solic_compra.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_exportar_excel = QPushButton("Exportar Excel", self)
        self.btn_exportar_excel.clicked.connect(lambda: exportar_excel(self, self.tree))
        self.btn_exportar_excel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_exportar_excel.hide()

        self.btn_fechar = QPushButton("Fechar", self)
        self.btn_fechar.clicked.connect(self.close)
        self.btn_fechar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_home = QPushButton("HOME", self)
        self.btn_home.setObjectName("btn_home")
        self.btn_home.clicked.connect(self.return_to_main)
        self.btn_home.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_image_comparator = QPushButton("Image Comparator", self)
        self.btn_image_comparator.clicked.connect(lambda: run_image_comparator_model(self))
        self.btn_image_comparator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_image_comparator.hide()

        self.btn_toggle_footer = QPushButton("Ocultar Status", self)
        self.btn_toggle_footer.clicked.connect(self.toggle_footer)
        self.btn_toggle_footer.hide()

        self.field_name_list = [
            "codigo",
            "descricao",
            "contem_descricao",
            "ordem_producao",
            "qp",
            "solic_compras",
            "pedido_compras",
            "nf_entrada",
            "armazem",
            "fornecedor_razao",
            "fornecedor_fantasia"
        ]

        object_fields = {
            "codigo": self.campo_codigo,
            "descricao": self.campo_descricao,
            "contem_descricao": self.campo_contem_descricao,
            "ordem_producao": self.campo_OP,
            "qp": self.campo_qp,
            "solic_compras": self.campo_sc,
            "pedido_compras": self.campo_pedido,
            "nf_entrada": self.campo_doc_nf,
            "armazem": self.campo_armazem,
            "fornecedor_razao": self.campo_razao_social_fornecedor,
            "fornecedor_fantasia": self.campo_nm_fantasia_fornecedor
        }

        history_manager = SearchHistoryManager('compras')
        self.autocomplete_settings = AutoCompleteManager(history_manager)
        self.autocomplete_settings.setup_autocomplete(self.field_name_list, object_fields)

        self.campo_sc.returnPressed.connect(self.btn_pesquisar)
        self.campo_pedido.returnPressed.connect(self.btn_pesquisar)
        self.campo_doc_nf.returnPressed.connect(self.btn_pesquisar)
        self.campo_codigo.returnPressed.connect(self.btn_pesquisar)
        self.campo_descricao.returnPressed.connect(self.btn_pesquisar)
        self.campo_contem_descricao.returnPressed.connect(self.btn_pesquisar)
        self.campo_qp.returnPressed.connect(self.btn_pesquisar)
        self.campo_OP.returnPressed.connect(self.btn_pesquisar)
        self.campo_razao_social_fornecedor.returnPressed.connect(self.btn_pesquisar)
        self.campo_nm_fantasia_fornecedor.returnPressed.connect(self.btn_pesquisar)

        layout = QVBoxLayout()
        layout_campos_01 = QHBoxLayout()
        layout_campos_02 = QHBoxLayout()
        layout_button_03 = QHBoxLayout()
        layout_button_04 = QHBoxLayout()
        self.layout_buttons = QHBoxLayout()
        self.layout_footer_label = QHBoxLayout()

        container_sc = QVBoxLayout()
        container_sc.addWidget(self.label_sc)
        container_sc.addWidget(self.campo_sc)

        container_pedido = QVBoxLayout()
        container_pedido.addWidget(self.label_pedido)
        container_pedido.addWidget(self.campo_pedido)

        container_codigo = QVBoxLayout()
        container_codigo.addWidget(self.label_codigo)
        container_codigo.addWidget(self.campo_codigo)

        container_descricao_prod = QVBoxLayout()
        container_descricao_prod.addWidget(self.label_descricao_prod)
        container_descricao_prod.addWidget(self.campo_descricao)

        container_contem_descricao_prod = QVBoxLayout()
        container_contem_descricao_prod.addWidget(self.label_contem_descricao_prod)
        container_contem_descricao_prod.addWidget(self.campo_contem_descricao)

        container_op = QVBoxLayout()
        container_op.addWidget(self.label_OP)
        container_op.addWidget(self.campo_OP)

        container_qp = QVBoxLayout()
        container_qp.addWidget(self.label_qp)
        container_qp.addWidget(self.campo_qp)

        container_doc_nf = QVBoxLayout()
        container_doc_nf.addWidget(self.label_nf)
        container_doc_nf.addWidget(self.campo_doc_nf)

        container_data_ini = QVBoxLayout()
        container_data_ini.addWidget(self.label_data_inicio)
        container_data_ini.addWidget(self.campo_data_inicio)

        container_data_fim = QVBoxLayout()
        container_data_fim.addWidget(self.label_data_fim)
        container_data_fim.addWidget(self.campo_data_fim)

        container_campo_armazem = QVBoxLayout()
        container_campo_armazem.addWidget(self.label_armazem)
        container_campo_armazem.addWidget(self.campo_armazem)

        container_fornecedor = QVBoxLayout()
        container_fornecedor.addWidget(self.label_fornecedor)
        container_fornecedor.addWidget(self.campo_razao_social_fornecedor)

        container_nm_fantasia_forn = QVBoxLayout()
        container_nm_fantasia_forn.addWidget(self.label_nm_fantasia_forn)
        container_nm_fantasia_forn.addWidget(self.campo_nm_fantasia_fornecedor)

        layout_campos_01.addStretch()
        layout_campos_02.addStretch()
        layout_campos_01.addLayout(container_qp)
        layout_campos_01.addLayout(container_sc)
        layout_campos_01.addLayout(container_pedido)
        layout_campos_01.addLayout(container_doc_nf)
        layout_campos_01.addLayout(container_codigo)
        layout_campos_01.addLayout(container_descricao_prod)
        layout_campos_01.addLayout(container_contem_descricao_prod)
        layout_campos_01.addLayout(container_op)
        layout_campos_02.addLayout(container_data_ini)
        layout_campos_02.addLayout(container_data_fim)
        layout_campos_02.addLayout(container_campo_armazem)
        layout_campos_02.addLayout(container_fornecedor)
        layout_campos_02.addLayout(container_nm_fantasia_forn)
        layout_campos_01.addStretch()
        layout_campos_02.addStretch()

        layout_button_03.addStretch()
        layout_button_04.addStretch()
        layout_button_03.addWidget(self.btn_consultar)
        layout_button_03.addWidget(self.btn_solic_compra)
        layout_button_04.addWidget(self.btn_visualizar_nf)
        layout_button_04.addWidget(self.btn_ultimas_nfe)
        layout_button_04.addWidget(self.btn_ultimos_fornecedores)
        layout_button_04.addWidget(self.btn_saldo_estoque)
        layout_button_04.addWidget(self.btn_onde_e_usado)
        layout_button_03.addWidget(self.btn_nova_janela)
        layout_button_04.addWidget(self.btn_limpar_filtro)
        layout_button_03.addWidget(self.btn_limpar)
        layout_button_04.addWidget(self.btn_exportar_excel)
        layout_button_04.addWidget(self.btn_image_comparator)
        layout_button_04.addStretch()
        layout_button_03.addWidget(self.btn_fechar)
        layout_button_03.addWidget(self.btn_home)
        layout_button_03.addStretch()

        self.layout_footer_label.addStretch(1)
        self.layout_footer_label.addWidget(self.label_line_number)
        self.layout_footer_label.addWidget(self.label_indicators)
        self.layout_footer_label.addWidget(self.btn_toggle_footer)
        self.layout_footer_label.addStretch(1)
        self.layout_footer_label.addWidget(self.logo_label)

        layout.addLayout(layout_campos_01)
        layout.addLayout(layout_campos_02)
        layout.addLayout(layout_button_03)
        layout.addLayout(layout_button_04)
        layout.addLayout(self.layout_buttons)
        layout.addWidget(self.table_area)
        layout.addWidget(self.tree)
        layout.addLayout(self.layout_footer_label)

        self.setLayout(layout)

        self.setStyleSheet(compras_qss())

    # Method to toggle the footer visibility and adjust the table size
    def toggle_footer(self):
        if self.label_line_number.isVisible():
            self.label_line_number.hide()
            self.label_indicators.hide()
            self.btn_toggle_footer.setText("Exibir Status")
        else:
            self.label_line_number.show()
            self.label_indicators.show()
            self.btn_toggle_footer.setText("Ocultar Status")
        self.adjust_table_size()

    # Method to adjust the table size
    def adjust_table_size(self):
        if self.label_line_number.isVisible():
            self.tree.setGeometry(self.tree.x(), self.tree.y(), self.tree.width(), self.tree.height() - self.layout_footer_label.sizeHint().height())
        else:
            self.tree.setGeometry(self.tree.x(), self.tree.y(), self.tree.width(), self.tree.height() + self.layout_footer_label.sizeHint().height())

    def not_found_message(self, df):
        if not self.table_line_number(df.shape[0]):
            self.clean_screen()
            exibir_mensagem("Eureka!® Compras", 'Nenhum resultado encontrado nesta pesquisa.', "info")
            return False
        else:
            return True

    def btn_pesquisar(self):
        message = "🔄 Processando dados...\n\n⏱️ Por favor aguarde..."
        for field_name in self.field_name_list:
            self.autocomplete_settings.save_search_history(field_name)
        if self.dataframe_original is None:
            dialog = loading_dialog(self, "Eureka® Compras", message)
            self.executar_consulta()
            self.dataframe_original = self.dataframe.copy()
            filtered_df = self.filter_table()
            if not self.not_found_message(filtered_df):
                self.dataframe_original = None
                dialog.close()
                return
            self.atualizar_tabela(filtered_df)
            self.dataframe = filtered_df.copy()
            dialog.close()
        else:
            dialog = loading_dialog(self, "Eureka® Compras", message)
            filtered_df = self.filter_table()
            if not self.not_found_message(filtered_df):
                self.dataframe_original = None
                dialog.close()
                return
            self.atualizar_tabela(filtered_df)
            self.dataframe = filtered_df.copy()
            dialog.close()
        
    def return_to_main(self):
        self.close()  # Fecha a janela atual
        self.main_window.reopen()  # Reabre ou traz a janela principal ao foco

    def abrir_nova_janela(self):
        eng_window = ComprasApp(self.main_window)
        eng_window.showMaximized()
        self.main_window.sub_windows.append(eng_window)

    def add_today_button(self, date_edit):
        calendar = date_edit.calendarWidget()
        calendar.setGeometry(10, 10, 600, 400)
        btn_today = QPushButton("Hoje", calendar)
        btn_today.setObjectName("today_button")
        largura, altura = 50, 20
        btn_today.setGeometry(20, 5, largura, altura)
        btn_today.clicked.connect(lambda: date_edit.setDate(QDate.currentDate()))

    def fechar_guia(self, index):
        if index >= 0:
            try:
                codigo_guia_fechada = self.tabWidget.tabText(index)
                self.guias_abertas.remove(codigo_guia_fechada)

            # Por ter duas listas de controle de abas abertas, 'guias_abertas = []' e 'guias_abertas_onde_usado = []',
            # ao fechar uma guia ocorre uma exceção (ValueError) se o código não for encontrado em uma das listas.
            # Utilize try/except para contornar esse problema.
            except ValueError:
                codigo_guia_fechada = self.tabWidget.tabText(index).split(' - ')[1]
                try:
                    self.guias_abertas_onde_usado.remove(codigo_guia_fechada)
                except ValueError:
                    try:
                        self.guias_abertas_saldo.remove(codigo_guia_fechada)
                    except ValueError:
                        try:
                            self.guias_abertas_ultimos_fornecedores.remove(codigo_guia_fechada)
                        except ValueError:
                            try:
                                self.guias_abertas_ultimas_nfe.remove(codigo_guia_fechada)
                            except ValueError:
                                self.guias_abertas_visualizar_nfe.remove(codigo_guia_fechada)

            finally:
                self.tabWidget.removeTab(index)

                if not self.existe_guias_abertas():
                    # Se não houver mais guias abertas, remova a guia do layout principal
                    self.tabWidget.setVisible(False)
                    self.guia_fechada.emit()

    def existe_guias_abertas(self):
        return self.tabWidget.count() > 0

    def show_context_menu(self, position, table):
        indexes = table.selectedIndexes()
        if indexes:
            # Obtém o índice do item clicado
            index = table.indexAt(position)
            if not index.isValid():
                return

            # Seleciona a linha inteira
            table.selectRow(index.row())

            menu = QMenu()
            # A lib Qt garante que o objeto do menu será destruído após uso
            menu.setAttribute(Qt.WA_DeleteOnClose)

            context_menu_image_comparator = QAction('Abrir ImageComparator®', self)
            context_menu_image_comparator.triggered.connect(lambda: run_image_comparator_exe())

            context_menu_visualizar_nf = QAction('Visualizar Nota Fiscal', self)
            context_menu_visualizar_nf.triggered.connect(lambda: visualizar_nfe(self, table))

            context_menu_ultimo_fornecedor = QAction('Últimos Fornecedores', self)
            context_menu_ultimo_fornecedor.triggered.connect(lambda: executar_ultimos_fornecedores(self, table))

            context_menu_ultimas_nfe = QAction('Últimas Notas Fiscais', self)
            context_menu_ultimas_nfe.triggered.connect(lambda: consultar_ultimas_nfe(self, table))

            context_menu_consultar_onde_usado = QAction('Onde é usado?', self)
            context_menu_consultar_onde_usado.triggered.connect(lambda: executar_consulta_onde_usado(self, table))

            context_menu_saldo_estoque = QAction('Saldo em estoque', self)
            context_menu_saldo_estoque.triggered.connect(lambda: executar_saldo_em_estoque(self, table))

            context_menu_nova_janela = QAction('Nova janela', self)
            context_menu_nova_janela.triggered.connect(self.abrir_nova_janela)

            menu.addAction(context_menu_nova_janela)
            menu.addAction(context_menu_image_comparator)
            menu.addSeparator()
            menu.addAction(context_menu_consultar_onde_usado)
            menu.addAction(context_menu_saldo_estoque)
            menu.addSeparator()
            menu.addAction(context_menu_ultimo_fornecedor)
            menu.addAction(context_menu_ultimas_nfe)
            menu.addAction(context_menu_visualizar_nf)

            menu.exec_(table.viewport().mapToGlobal(position))

    def add_clear_button(self, line_edit):
        clear_icon = self.style().standardIcon(QStyle.SP_LineEditClearButton)

        line_edit_height = line_edit.height()
        pixmap = clear_icon.pixmap(line_edit_height - 4, line_edit_height - 4)
        larger_clear_icon = QIcon(pixmap)

        clear_action = QAction(larger_clear_icon, "Limpar", line_edit)
        clear_action.triggered.connect(lambda: self.clear_and_filter(line_edit))
        line_edit.addAction(clear_action, QLineEdit.TrailingPosition)

    def clear_and_filter(self, line_edit):
        line_edit.clear()
        self.btn_pesquisar()

    def configurar_tabela(self, dataframe):
        self.table_area.hide()
        self.tree.show()
        self.tree.setAlternatingRowColors(True)

        # Definir número de colunas e cabeçalhos
        self.tree.setColumnCount(len(dataframe.columns))
        self.tree.setHorizontalHeaderLabels(dataframe.columns)

        # Definir largura de colunas específicas
        self.tree.setColumnWidth(0, 190)  # Coluna 'ICONES DE STATUS'
        for col in range(1, len(dataframe.columns)):
            self.tree.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)

        # Configurar propriedades da tabela
        self.tree.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tree.setSelectionBehavior(QTableWidget.SelectRows)
        self.tree.setSelectionMode(QTableWidget.SingleSelection)
        self.tree.itemDoubleClicked.connect(copiar_linha)
        self.tree.setFont(QFont(self.fonte_tabela, self.tamanho_fonte_tabela))
        self.tree.verticalHeader().setDefaultSectionSize(self.altura_linha)

        try:
            self.tree.customContextMenuRequested.disconnect()
            self.tree.horizontalHeader().sectionClicked.disconnect(self.abrir_filtro)
        except TypeError:
            pass

        # Conectar sinal de clique para abrir o filtro
        self.tree.horizontalHeader().sectionClicked.connect(self.abrir_filtro)

        # Menu de contexto personalizado
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(lambda pos: self.show_context_menu(pos, self.tree))

    def configurar_tabela_tooltips(self, dataframe):
        # Mapa de tooltips correspondentes às colunas da consulta SQL
        tooltip_map = {
            " ": "VERMELHO:\nSolicitação sem pedido de compra\n\n"
                 "AZUL:\nEm aprovação\n\n"
                 "CINZA:\nAguardando entrega\n\n"
                 "LARANJA:\nEntrega parcial\n\n"
                 "VERDE:\nPedido de compra encerrado"
        }

        # Obtenha os cabeçalhos das colunas do dataframe
        headers = dataframe.columns

        # Adicione os cabeçalhos e os tooltips
        for i, header in enumerate(headers):
            item = QTableWidgetItem(header)
            tooltip = tooltip_map.get(header)
            item.setToolTip(tooltip)
            self.tree.setHorizontalHeaderItem(i, item)

    def clean_fields(self):
        self.campo_sc.clear()
        self.campo_pedido.clear()
        self.campo_codigo.clear()
        self.campo_descricao.clear()
        self.campo_contem_descricao.clear()
        self.campo_razao_social_fornecedor.clear()
        self.campo_nm_fantasia_fornecedor.clear()
        self.campo_qp.clear()
        self.campo_OP.clear()
        self.campo_armazem.clear()

    def clean_screen(self):
        self.table_area.show()
        self.tree.hide()

        self.clean_fields()

        self.tree.setColumnCount(0)
        self.tree.setRowCount(0)
        self.label_line_number.hide()
        self.label_indicators.hide()

        self.btn_exportar_excel.hide()
        self.btn_image_comparator.hide()
        self.btn_onde_e_usado.hide()
        self.btn_saldo_estoque.hide()
        self.btn_ultimos_fornecedores.hide()
        self.btn_ultimas_nfe.hide()
        self.btn_limpar_filtro.hide()
        self.btn_visualizar_nf.hide()
        self.btn_toggle_footer.hide()

        self.guias_abertas.clear()
        self.guias_abertas_onde_usado.clear()
        self.guias_abertas_saldo.clear()
        self.guias_abertas_ultimos_fornecedores.clear()
        self.guias_abertas_ultimas_nfe.clear()
        self.guias_abertas_visualizar_nfe.clear()

        while self.tabWidget.count():
            self.tabWidget.removeTab(0)
        self.tabWidget.setVisible(False)
        self.guia_fechada.emit()

    def button_visible_control(self, visible):
        if visible == "False":
            self.btn_exportar_excel.hide()
            self.btn_onde_e_usado.hide()
            self.btn_saldo_estoque.hide()
            self.btn_ultimos_fornecedores.hide()
            self.btn_ultimas_nfe.hide()
            self.btn_visualizar_nf.hide()
            self.btn_image_comparator.hide()
            self.btn_toggle_footer.hide()
        else:
            self.btn_exportar_excel.show()
            self.btn_onde_e_usado.show()
            self.btn_saldo_estoque.show()
            self.btn_ultimos_fornecedores.show()
            self.btn_ultimas_nfe.show()
            self.btn_visualizar_nf.show()
            self.btn_image_comparator.show()
            self.btn_toggle_footer.show()

    def controle_campos_formulario(self, status):
        self.campo_sc.setEnabled(status)
        self.campo_codigo.setEnabled(status)
        self.campo_descricao.setEnabled(status)
        self.campo_contem_descricao.setEnabled(status)
        self.campo_razao_social_fornecedor.setEnabled(status)
        self.campo_qp.setEnabled(status)
        self.campo_OP.setEnabled(status)
        self.campo_data_inicio.setEnabled(status)
        self.campo_data_fim.setEnabled(status)
        self.campo_armazem.setEnabled(status)
        self.btn_consultar.setEnabled(status)
        self.btn_exportar_excel.setEnabled(status)
        self.btn_saldo_estoque.setEnabled(status)
        self.btn_onde_e_usado.setEnabled(status)
        self.btn_ultimos_fornecedores.setEnabled(status)
        self.btn_image_comparator.setEnabled(status)
        self.btn_toggle_footer.setEnabled(status)

    def filter_table(self):
            filter_sc = self.campo_sc.text().strip()
            filter_pedido = self.campo_pedido.text().strip()
            filter_nf = self.campo_doc_nf.text().strip()
            filter_qp = self.campo_qp.text().strip()
            filter_op = self.campo_OP.text().strip()
            filter_codigo = self.campo_codigo.text().strip().upper()
            filter_armazem = self.campo_armazem.text().strip().upper()
            filter_razao_social_fornecedor = self.campo_razao_social_fornecedor.text().strip().upper()
            filter_nm_fantasia_fornecedor = self.campo_nm_fantasia_fornecedor.text().strip().upper()
            filter_descricao = self.campo_descricao.text().strip().upper()
            filter_contem_descricao = self.campo_contem_descricao.text().strip().upper()

            filtered_df = self.dataframe_original.copy()

            if filter_sc:
                filtered_df = filtered_df[filtered_df['SOLIC. COMPRA'].str.endswith(filter_sc, na=False)]
            if filter_pedido:
                filtered_df = filtered_df[filtered_df['PEDIDO COMPRA'].str.endswith(filter_pedido, na=False)]
            if filter_nf:
                filtered_df = filtered_df[filtered_df['DOC. NF ENTRADA'].str.endswith(filter_nf, na=False)]
            if filter_qp:
                filtered_df = filtered_df[filtered_df['QP/QR'].str.endswith(filter_qp, na=False)]
            if filter_op:
                filtered_df = filtered_df[filtered_df['OP'].str.endswith(filter_op, na=False)]
            if filter_codigo:
                filtered_df = filtered_df[filtered_df['CÓDIGO'].str.startswith(filter_codigo, na=False)]
            if filter_armazem:
                filtered_df = filtered_df[filtered_df['CÓD. ARMAZÉM'].str.startswith(filter_armazem, na=False)]
            if filter_razao_social_fornecedor:
                filtered_df = filtered_df[filtered_df['RAZÃO SOCIAL FORNECEDOR'].str.contains(filter_razao_social_fornecedor, na=False)]
            if filter_nm_fantasia_fornecedor:
                filtered_df = filtered_df[filtered_df['NOME FANTASIA FORNECEDOR'].str.contains(filter_nm_fantasia_fornecedor, na=False)]
            if filter_descricao:
                filtered_df = filtered_df[filtered_df['DESCRIÇÃO'].str.startswith(filter_descricao, na=False)]
            if filter_contem_descricao:
                filtered_df = filtered_df[filtered_df['DESCRIÇÃO'].str.contains(filter_contem_descricao, na=False)]

            return filtered_df

    def query_followup(self):
        data_inicio_formatada = self.campo_data_inicio.date().toString("yyyyMMdd")
        data_fim_formatada = self.campo_data_fim.date().toString("yyyyMMdd")

        if data_inicio_formatada != '' and data_fim_formatada != '':
            filtro_data = f"C7_EMISSAO >= '{data_inicio_formatada}' AND C7_EMISSAO <= '{data_fim_formatada}'"
        else:
            filtro_data = ''

        query = f"""
                SELECT
                    PC.C7_ZZNUMQP AS [QP/QR],
                    CASE
                        WHEN itemPedidoVenda.C6_XTPOPER = 2 THEN 'Sim'
                        ELSE 'Não'
                    END AS "QR?",
                    PC.C7_CONAPRO AS "APROVAÇÃO",
                    tabelaAprovacao.CR_DATALIB AS "DATA APROVAÇÃO", 
                    PC.C7_NUMSC AS "SOLIC. COMPRA",
                    PC.C7_NUM AS "PEDIDO COMPRA",
                    ITEM_NF.D1_DOC AS "DOC. NF ENTRADA",
                    PC.C7_PRODUTO AS "CÓDIGO",
                    PC.C7_DESCRI AS "DESCRIÇÃO",
                    PC.C7_UM AS "UN.",
                    PC.C7_QTDSOL AS "QTD. SOLIC. COMPRAS",
                    PC.C7_QUANT AS "QTD. PEDIDO COMPRA",
                    ITEM_NF.D1_QUANT AS "QTD. ENTREGUE",
                    CASE 
                        WHEN ITEM_NF.D1_QUANT IS NULL THEN PC.C7_QUANT 
                        ELSE PC.C7_QUANT - ITEM_NF.D1_QUANT
                    END AS "QTD. PENDENTE",
                    PC.C7_PRECO AS "VALOR UNIT. PC",
                    PC.C7_TOTAL AS "VALOR TOTAL PC",
                    ITEM_NF.D1_VUNIT AS "VALOR UNIT. NF",
                    ITEM_NF.D1_TOTAL AS "VALOR TOTAL NF",
                    PC.C7_DATPRF AS "PREVISÃO ENTREGA",
                    ITEM_NF.D1_DTDIGIT AS "DATA DE ENTREGA",
                    PC.C7_ENCER AS "STATUS PEDIDO COMPRA",
                    SC.C1_EMISSAO AS "SC ABERTA EM:",
                    PC.C7_EMISSAO AS "PC ABERTO EM:",
                    ITEM_NF.D1_EMISSAO AS "DATA EMISSÃO NF",
                    SC.C1_ITEM AS "ITEM SC",
                    PC.C7_ITEM AS "ITEM PC",
                    FORN.A2_COD AS "CÓD. FORNECEDOR",
                    FORN.A2_NOME AS "RAZÃO SOCIAL FORNECEDOR",
                    FORN.A2_NREDUZ AS "NOME FANTASIA FORNECEDOR",
                    PC.C7_LOCAL AS "CÓD. ARMAZÉM",
                    ARM.NNR_DESCRI AS "DESCRIÇÃO ARMAZÉM",
                    PROD.B1_ZZLOCAL AS "ENDEREÇO ALMOXARIFADO",
                    SC.C1_OBS AS "OBSERVAÇÃO SOLIC. COMPRA",
                    PC.C7_OBS AS "OBSERVAÇÃO PEDIDO DE COMPRA",
                    PC.C7_OBSM AS "OBSERVAÇÃO ITEM DO PEDIDO DE COMPRA",
                    US.USR_NOME AS "SOLICITANTE",
                    PC.S_T_A_M_P_ AS "PEDIDO DE COMPRA ABERTO EM:",
                    SC.C1_OP AS "OP"
                FROM 
                    {self.database}.dbo.SC7010 PC
                LEFT JOIN
                    {self.database}.dbo.SD1010 ITEM_NF
                ON 
                    PC.C7_NUM = ITEM_NF.D1_PEDIDO AND PC.C7_ITEM = ITEM_NF.D1_ITEMPC
                LEFT JOIN
                    {self.database}.dbo.SC1010 SC
                ON 
                    SC.C1_PEDIDO = PC.C7_NUM AND SC.C1_ITEMPED = PC.C7_ITEM
                LEFT JOIN
                    {self.database}.dbo.SA2010 FORN
                ON
                    FORN.A2_COD = PC.C7_FORNECE
                LEFT JOIN
                    {self.database}.dbo.NNR010 ARM
                ON
                    SC.C1_LOCAL = ARM.NNR_CODIGO
                LEFT JOIN 
                    {self.database}.dbo.SYS_USR US
                ON
                    SC.C1_SOLICIT = US.USR_CODIGO AND US.D_E_L_E_T_ <> '*'
                INNER JOIN 
                    {self.database}.dbo.SB1010 PROD
                ON 
                    PROD.B1_COD = PC.C7_PRODUTO
                LEFT JOIN
                    {self.database}.dbo.SC6010 itemPedidoVenda
                ON
                    PC.C7_ZZNUMQP = itemPedidoVenda.C6_NUM AND PC.C7_PRODUTO = itemPedidoVenda.C6_PRODUTO
                LEFT JOIN (
                    SELECT
                        CR_NUM,
                        MAX(CR_DATALIB) as CR_DATALIB
                        FROM {self.database}.dbo.SCR010
                        GROUP BY CR_NUM
                ) tabelaAprovacao
                ON
                    PC.C7_NUM = tabelaAprovacao.CR_NUM
                WHERE
                    {filtro_data}
                    AND PC.D_E_L_E_T_ <> '*'
                    AND PROD.D_E_L_E_T_ <> '*' 
                    ORDER BY PC.R_E_C_N_O_ DESC;
            """
        return query

    def atualizar_tabela(self, dataframe):
        self.tree.setRowCount(len(dataframe.index))
        self.tree.clearContents()
        self.tree.setRowCount(0)
        self.tree.setColumnCount(0)
        self.configurar_tabela(dataframe)
        self.configurar_tabela_tooltips(dataframe)

        # Construir caminhos relativos
        script_dir = os.path.dirname(os.path.abspath(__file__))
        red_icon = os.path.join(script_dir, '..', 'resources', 'images', 'red.png')
        gray_icon = os.path.join(script_dir, '..', 'resources', 'images', 'gray.png')
        blue_icon = os.path.join(script_dir, '..', 'resources', 'images', 'wait.png')
        green_icon = os.path.join(script_dir, '..', 'resources', 'images', 'green.png')
        orange_icon = os.path.join(script_dir, '..', 'resources', 'images', 'orange.png')

        red_icon = QIcon(red_icon)
        gray_icon = QIcon(gray_icon)
        blue_icon = QIcon(blue_icon)
        green_icon = QIcon(green_icon)
        orange_icon = QIcon(orange_icon)

        for i, (index, row) in enumerate(dataframe.iterrows()):
            self.tree.insertRow(i)
            for column_name, value in row.items():
                if value is not None:
                    if column_name == ' ':
                        item = QTableWidgetItem()
                        if row['STATUS PEDIDO COMPRA'] is not None:
                            if (row['STATUS PEDIDO COMPRA'].strip() == '' and row['DOC. NF ENTRADA'] is None
                                    and row['APROVAÇÃO'] in ['L', ' ']):
                                item.setIcon(gray_icon)
                                item.setText('AGUARDANDO ENTREGA')
                                dataframe.at[index, ' '] = 'AGUARDANDO ENTREGA'
                            elif (row['STATUS PEDIDO COMPRA'].strip() == '' and row['DOC. NF ENTRADA'] is None
                                  and row['APROVAÇÃO'] == 'B'):
                                item.setIcon(blue_icon)
                                item.setText('EM APROVAÇÃO')
                                dataframe.at[index, ' '] = 'EM APROVAÇÃO'
                            elif row['STATUS PEDIDO COMPRA'].strip() == '' and row['DOC. NF ENTRADA'] is not None:
                                item.setIcon(orange_icon)
                                item.setText('ENTREGA PARCIAL')
                                dataframe.at[index, ' '] = 'ENTREGA PARCIAL'
                            elif row['STATUS PEDIDO COMPRA'] == 'E':
                                item.setIcon(green_icon)
                                item.setText('PEDIDO ENCERRADO')
                                dataframe.at[index, ' '] = 'PEDIDO ENCERRADO'
                            item.setSizeHint(QSize(64, 64))
                        elif row['PEDIDO COMPRA'] is None:
                            item.setIcon(red_icon)
                            item.setText('SEM PEDIDO COMPRA')
                            dataframe.at[index, ' '] = 'SEM PEDIDO COMPRA'
                    else:
                        if column_name in ('QP/QR', 'SOLIC. COMPRA', 'DOC. NF ENTRADA'):
                            value = value.lstrip('0')
                        if column_name in ('QTD. SOLIC. COMPRAS', 'QTD. PEDIDO COMPRA', 'QTD. ENTREGUE',
                                           'VALOR UNIT. PC', 'VALOR TOTAL PC', 'VALOR UNIT. NF', 'VALOR TOTAL NF'):
                            if column_name in ('VALOR UNIT. PC', 'VALOR TOTAL PC', 'VALOR UNIT. NF', 'VALOR TOTAL NF'):
                                if not pd.isna(value):
                                    value = f"R$ {locale.format_string("%.2f", float(value), grouping=True)}"
                                else:
                                    value = ''
                            else:
                                value = float(value)
                                if value.is_integer():
                                    value = int(value)
                                else:
                                    value = locale.format_string("%.2f", value, grouping=True)

                        if (column_name in ('QTD. PEDIDO COMPRA', 'VALOR UNIT. PC', 'VALOR TOTAL PC', 'QTD. ENTREGUE',
                                            'VALOR UNIT. NF', 'VALOR TOTAL NF') and
                                value == 'nan'):
                            value = ''

                        if column_name == 'PEDIDO DE COMPRA ABERTO EM:' and pd.isna(value):
                            value = ''
                        if column_name == 'PEDIDO DE COMPRA ABERTO EM:' and not pd.isna(value) and value != '':
                            try:
                                # Converter para objeto datetime
                                datetime_value = pd.to_datetime(value, utc=True)
                                # Converter para o fuso horário UTC-3
                                datetime_value = datetime_value.tz_convert('America/Sao_Paulo')
                                # Remover os últimos 7 caracteres equivale a remover segundos e microsegundos
                                datetime_value = datetime_value.replace(microsecond=0)
                                # Converter de volta para string no formato desejado
                                value = datetime_value.strftime('%d/%m/%Y %H:%M:%S')
                            except ValueError:
                                # Lidar com valores que não podem ser convertidos para datetime
                                print(f"Erro ao converter {value} para datetime.")

                        if column_name == 'CONTADOR DE DIAS' and row['DOC. NF ENTRADA'] is None:
                            data_atual = datetime.now()
                            previsao_entrega_sem_formatacao = row['PREVISÃO ENTREGA']
                            if pd.notna(previsao_entrega_sem_formatacao):
                                previsao_entrega_obj = datetime.strptime(previsao_entrega_sem_formatacao, "%Y%m%d")
                                previsao_entrega_formatada = previsao_entrega_obj.strftime("%d/%m/%Y")
                                previsao_entrega = pd.to_datetime(previsao_entrega_formatada, dayfirst=True)
                                value = (previsao_entrega - data_atual).days
                        elif column_name == 'CONTADOR DE DIAS' and row['DOC. NF ENTRADA'] is not None:
                            value = ''
                        if column_name == 'QTD. PENDENTE' and pd.isna(value):
                            value = ''
                        elif column_name == 'QTD. PENDENTE' and value:
                            value = float(value)
                            if value.is_integer():
                                value = int(value)
                            else:
                                value = locale.format_string("%.2f", float(value), grouping=True)

                        if column_name == 'STATUS PEDIDO COMPRA' and value == 'E':
                            value = 'Encerrado'
                        elif column_name == 'STATUS PEDIDO COMPRA' and value.strip() == '':
                            value = ''

                        if column_name in ('DATA APROVAÇÃO', 'PREVISÃO ENTREGA', 'DATA DE ENTREGA', 'SC ABERTA EM:',
                                           'PC ABERTO EM:', 'DATA EMISSÃO NF') and not value.isspace():
                            data_obj = datetime.strptime(value, "%Y%m%d")
                            value = data_obj.strftime("%d/%m/%Y")

                        item = QTableWidgetItem(str(value).strip())

                        if column_name not in ('DESCRIÇÃO', 'OBSERVAÇÃO SOLIC. COMPRA', 'OBSERVAÇÃO PEDIDO DE COMPRA',
                                               'OBSERVAÇÃO ITEM DO PEDIDO DE COMPRA', 'RAZÃO SOCIAL FORNECEDOR',
                                               'NOME FANTASIA FORNECEDOR'):
                            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        if column_name in ('VALOR UNIT. PC', 'VALOR TOTAL PC', 'VALOR UNIT. NF', 'VALOR TOTAL NF'):
                            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    item = QTableWidgetItem('')
                self.tree.setItem(i, list(row.index).index(column_name), item)

        for i in range(self.tree.columnCount()):
            if self.tree.horizontalHeaderItem(i).text() == 'APROVAÇÃO':
                self.tree.setColumnHidden(i, True)
                break

        self.table_line_number(dataframe.shape[0])
        self.exibir_indicadores(dataframe)
        self.tree.viewport().update()
        # self.tree.setSortingEnabled(True)
        self.controle_campos_formulario(True)
        self.button_visible_control(True)

    def exibir_indicadores(self, df):
        coluna_status = ' '

        contagem_itens = {}
        contagem_pedidos = {}
        for status in self.lista_status_tabela:
            quantidade_itens = len(df[df[coluna_status] == status])
            contagem_itens[status] = quantidade_itens
            quantidade_pedidos_diferentes = df[df[coluna_status] == status]['QP/QR'].nunique()
            contagem_pedidos[status] = quantidade_pedidos_diferentes

        indicadores_table = f"""
                <table border="1" cellspacing="2" cellpadding="4" style="border-collapse: collapse; text-align: left; 
                width: 100%;">
                    <tr>
                        <th style="text-align: middle; vertical-align: middle;">Status</th>
                        <th style="text-align: right; vertical-align: middle;">Itens</th>
                        <th style="text-align: right; vertical-align: middle;">Pedidos</th>
                    </tr>
                    <tr>
                        <td style="vertical-align: middle;">EM APROVAÇÃO</td>
                        <td style="text-align: right; vertical-align: middle;">{contagem_itens['EM APROVAÇÃO']}</td>
                        <td style="text-align: right; vertical-align: middle;">{contagem_pedidos['EM APROVAÇÃO']}</td>
                    </tr>
                    <tr>
                        <td style="vertical-align: middle;">AGUARDANDO ENTREGA</td>
                        <td style="text-align: right; vertical-align: middle;">{contagem_itens['AGUARDANDO ENTREGA']}</td>
                        <td style="text-align: right; vertical-align: middle;">{contagem_pedidos['AGUARDANDO ENTREGA']}</td>
                    </tr>
                    <tr>
                        <td style="vertical-align: middle;">ENTREGA PARCIAL</td>
                        <td style="text-align: right; vertical-align: middle;">{contagem_itens['ENTREGA PARCIAL']}</td>
                        <td style="text-align: right; vertical-align: middle;">{contagem_pedidos['ENTREGA PARCIAL']}</td>
                    </tr>
                    <tr>
                        <td style="vertical-align: middle;">PEDIDO ENCERRADO</td>
                        <td style="text-align: right; vertical-align: middle;">{contagem_itens['PEDIDO ENCERRADO']}</td>
                        <td style="text-align: right; vertical-align: middle;">{contagem_pedidos['PEDIDO ENCERRADO']}</td>
                    </tr>
                </table>
            """
        self.label_indicators.setText(indicadores_table)
        self.label_indicators.show()

    def table_line_number(self, line_number):
        if line_number >= 1:
            if line_number > 1:
                message = f"Foram encontrados {line_number} itens"
            else:
                message = f"Foi encontrado {line_number} item"

            self.label_line_number.setText(f"{message}")
            self.label_line_number.show()
            return True
        else:
            self.controle_campos_formulario(True)
            self.button_visible_control(False)
            return False

    def executar_consulta(self):
        conn_str = (f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};'
                    f'PWD={self.password}')
        self.engine = create_engine(f'mssql+pyodbc:///?odbc_connect={conn_str}')
        try:
            query_consulta_filtro = self.query_followup()

            self.label_line_number.hide()
            self.label_indicators.hide()
            self.controle_campos_formulario(False)
            self.button_visible_control(False)

            self.dataframe = pd.read_sql(query_consulta_filtro, self.engine)
            self.dataframe.insert(0, ' ', '')
            self.dataframe[''] = ''
            self.dataframe.insert(16, 'CONTADOR DE DIAS', '')

        except Exception as ex:
            exibir_mensagem('Erro ao consultar TOTVS', f'Erro: {str(ex)}', 'error')

        finally:
            # Fecha a conexão com o banco de dados se estiver aberta
            if hasattr(self, 'engine'):
                self.engine.dispose()
                self.engine = None

    def abrir_filtro(self, logical_index):
        # Bloqueia sinais temporiariamente
        self.tree.horizontalHeader().blockSignals(True)
        # Pega o nome da coluna clicada
        nome_coluna = self.tree.horizontalHeaderItem(logical_index).text()

        # Check if filtro_dialog is already created and visible
        if getattr(self, 'filtro_dialog', None) is not None and self.filtro_dialog.isVisible():
            self.filtro_dialog.close()

        # Create and show a new instance of FilterDialog
        self.filtro_dialog = FilterDialog(self, nome_coluna, self.dataframe, self.lista_status_tabela)

        # Execute the dialog and wait for the user to close it
        if self.filtro_dialog.exec_() == QDialog.Accepted:
            # Get the selected filters from the dialog
            filtro_selecionado = self.filtro_dialog.get_filtros_selecionados()
            if filtro_selecionado:
                colunas_formatar = ['QTD. PEDIDO COMPRA', 'QTD. ENTREGUE', 'QTD. PENDENTE', 'VALOR UNIT. PC',
                                    'VALOR TOTAL PC', 'QTD. SOLIC. COMPRAS', 'VALOR UNIT. NF', 'VALOR TOTAL NF']

                # Função para formatação dos valores
                def formatar_valor(valor):
                    if isinstance(valor, float):
                        return '{:.1f}'.format(valor) if valor.is_integer() else '{:.2f}'.format(valor)
                    return valor

                # Aplicar formatação nas colunas especificas
                self.dataframe[colunas_formatar] = self.dataframe[colunas_formatar].map(formatar_valor)

                # Apply the filter to the dataframe
                self.dataframe = self.dataframe[self.dataframe[nome_coluna].isin(filtro_selecionado)]

                self.atualizar_tabela(self.dataframe)
                self.btn_limpar_filtro.show()
        # Reativa os sinais do cabeçalho
        self.tree.horizontalHeader().blockSignals(False)

    def limpar_filtros(self):
        dialog = loading_dialog(self, "Eureka®", "🤖 Removendo filtros...\n\nRestaurando a consulta inicial")
        self.clean_fields()
        self.dataframe = self.dataframe_original.copy()
        self.atualizar_tabela(self.dataframe_original)
        self.btn_limpar_filtro.hide()
        dialog.close()
