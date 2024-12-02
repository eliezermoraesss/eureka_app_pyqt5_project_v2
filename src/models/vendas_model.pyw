import locale
import os
import sys

# Caminho absoluto para o diretório onde o módulo src está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pandas as pd
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QTableWidget, QTableWidgetItem, QHeaderView, QStyle, QAction, QDateEdit, QLabel, \
    QSizePolicy, QTabWidget, QMenu, QDialog, QComboBox, QApplication, QFrame
from sqlalchemy import create_engine

from src.app.utils.consultar_onde_usado import executar_consulta_onde_usado
from src.app.utils.consultar_saldo_estoque import executar_saldo_em_estoque
from src.app.utils.consultar_ultimos_fornec import executar_ultimos_fornecedores
from src.app.utils.consultar_ultimas_nfe import consultar_ultimas_nfe
from src.app.utils.db_mssql import setup_mssql
from src.app.utils.load_session import load_session
from src.app.utils.utils import exibir_mensagem, copiar_linha, exportar_excel, abrir_desenho
from src.app.views.FilterDialog import FilterDialog
from src.app.utils.open_search_dialog import open_search_dialog
from src.dialog.loading_dialog import loading_dialog
from src.app.utils.run_image_comparator import run_image_comparator_exe, run_image_comparator_model


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


def format_number(value):
    if pd.notnull(value):
        value = float(value)
        if value.is_integer():
            return int(value)
        else:
            return locale.format_string("%.2f", value, grouping=True)
    else:
        return ''


class VendasApp(QWidget):
    guia_fechada = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.main_window = 'main_window'
        self.filtro_dialog = None
        self.df = pd.DataFrame()
        self.df_original = None
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.lista_status_tabela = ['ABERTO', 'FECHADO']

        user_data = load_session()
        username = user_data["username"]
        role = user_data["role"]

        self.engine = None
        self.username, self.password, self.database, self.server = setup_mssql()
        self.driver = '{SQL Server}'

        self.setWindowTitle(f"Eureka® Vendas . {username} ({role})")
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

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

        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_enaplic_path = os.path.join(script_dir, '..', 'resources', 'images', 'LOGO.jpeg')
        self.logo_label = QLabel(self)
        self.logo_label.setObjectName('logo-enaplic')
        pixmap_logo = QPixmap(logo_enaplic_path).scaledToWidth(30)
        self.logo_label.setPixmap(pixmap_logo)
        self.logo_label.setAlignment(Qt.AlignRight)

        self.label_title = QLabel("VENDAS", self)
        self.label_title.setObjectName('label-title')

        self.line = QFrame(self)
        self.line.setObjectName('line')
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.label_line_number = QLabel("", self)
        self.label_line_number.setObjectName("label-line-number")
        self.label_line_number.setVisible(False)

        self.label_indicators = QLabel("", self)
        self.label_indicators.setObjectName("label-indicators")
        self.label_indicators.setVisible(False)
        self.label_indicators.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

        self.label_pedido = QLabel("Pedido de Venda:", self)
        self.label_pedido.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.label_msg_nota = QLabel("Mensagem nota:", self)
        self.label_msg_nota.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.label_orcamento = QLabel("Orçamento:", self)
        self.label_orcamento.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.label_nf_saida = QLabel("NF Saída:", self)
        self.label_nf_saida.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.label_codigo = QLabel("Código:", self)
        self.label_codigo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.label_descricao_prod = QLabel("Descrição:", self)
        self.label_descricao_prod.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.label_contem_descricao_prod = QLabel("Contém na descrição:", self)
        self.label_contem_descricao_prod.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.label_data_inicio = QLabel("A partir de:", self)
        self.label_data_fim = QLabel("Até:", self)
        self.label_cliente = QLabel("Cliente:", self)
        self.label_status_pedido = QLabel("Status Pedido", self)
        self.label_tipo_pedido = QLabel("Tipo Pedido", self)

        self.campo_msg_nota = QLineEdit(self)
        self.campo_msg_nota.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_msg_nota.setMaxLength(6)
        self.campo_msg_nota.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_clear_button(self.campo_msg_nota)

        self.campo_pedido = QLineEdit(self)
        self.campo_pedido.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_pedido.setMaxLength(6)
        self.campo_pedido.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_clear_button(self.campo_pedido)

        self.campo_codigo = QLineEdit(self)
        self.campo_codigo.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_codigo.setMaxLength(13)
        self.campo_codigo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_clear_button(self.campo_codigo)

        self.campo_descricao_prod = QLineEdit(self)
        self.campo_descricao_prod.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_descricao_prod.setMaxLength(60)
        self.campo_descricao_prod.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_clear_button(self.campo_descricao_prod)

        self.campo_contem_descricao_prod = QLineEdit(self)
        self.campo_contem_descricao_prod.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_contem_descricao_prod.setMaxLength(60)
        self.campo_contem_descricao_prod.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_clear_button(self.campo_contem_descricao_prod)

        self.campo_doc_nf_entrada = QLineEdit(self)
        self.campo_doc_nf_entrada.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_doc_nf_entrada.setMaxLength(9)
        self.campo_doc_nf_entrada.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_clear_button(self.campo_doc_nf_entrada)

        self.campo_orcamento = QLineEdit(self)
        self.campo_orcamento.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_orcamento.setMaxLength(8)
        self.campo_orcamento.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_clear_button(self.campo_orcamento)

        self.campo_nome_cliente = CustomLineEdit('Cliente', 'cliente', 'Cliente', self)
        self.campo_nome_cliente.setObjectName("cliente")
        self.campo_nome_cliente.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_nome_cliente.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.campo_nome_cliente.setMaxLength(40)
        # self.add_clear_button(self.campo_nome_cliente)

        self.campo_data_inicio = QDateEdit(self)
        self.campo_data_inicio.setFont(QFont(fonte_campos, 10))
        self.campo_data_inicio.setFixedWidth(150)
        self.campo_data_inicio.setCalendarPopup(True)
        self.campo_data_inicio.setDisplayFormat("dd/MM/yyyy")

        data_atual = QDate.currentDate()
        intervalo_meses = 60
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

        self.btn_pesquisar = QPushButton("Pesquisar", self)
        self.btn_pesquisar.clicked.connect(self.executar_consulta)
        self.btn_pesquisar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_onde_e_usado = QPushButton("Onde é usado?", self)
        self.btn_onde_e_usado.clicked.connect(lambda: executar_consulta_onde_usado(self, self.tree))
        self.btn_onde_e_usado.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_onde_e_usado.hide()

        self.btn_saldo_estoque = QPushButton("Saldos em Estoque", self)
        self.btn_saldo_estoque.clicked.connect(lambda: executar_saldo_em_estoque(self, self.tree))
        self.btn_saldo_estoque.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_saldo_estoque.hide()

        self.btn_ultimos_fornecedores = QPushButton("Histórico de Fornecedores", self)
        self.btn_ultimos_fornecedores.clicked.connect(lambda: executar_ultimos_fornecedores(self, self.tree))
        self.btn_ultimos_fornecedores.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_ultimos_fornecedores.hide()

        self.btn_ultimas_nfe_entrada = QPushButton("Histórico de Nota Fiscal de Entrada", self)
        self.btn_ultimas_nfe_entrada.clicked.connect(lambda: consultar_ultimas_nfe(self, self.tree))
        self.btn_ultimas_nfe_entrada.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_ultimas_nfe_entrada.hide()

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

        self.btn_abrir_desenho = QPushButton("Abrir Desenho", self)
        self.btn_abrir_desenho.clicked.connect(lambda: abrir_desenho(self, self.tree))
        self.btn_abrir_desenho.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_abrir_desenho.hide()

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

        self.combobox_status_pedido = QComboBox(self)
        self.combobox_status_pedido.setEditable(False)
        self.combobox_status_pedido.setObjectName('combobox-status-pv')
        self.combobox_status_pedido.addItem('-', '1')
        self.combobox_status_pedido.addItem('Fechado', '2')
        self.combobox_status_pedido.addItem('Aberto', '3')

        self.combobox_tipo_pedido = QComboBox(self)
        self.combobox_tipo_pedido.setEditable(False)
        self.combobox_tipo_pedido.setObjectName('combobox-tipo-pv')
        self.combobox_tipo_pedido.addItem('-', '')
        self.combobox_tipo_pedido.addItem('QP', '1')
        self.combobox_tipo_pedido.addItem('QR', '2')
        self.combobox_tipo_pedido.addItem('Outros', '3')

        self.campo_pedido.returnPressed.connect(self.executar_consulta)
        self.campo_msg_nota.returnPressed.connect(self.executar_consulta)
        self.campo_orcamento.returnPressed.connect(self.executar_consulta)
        self.campo_doc_nf_entrada.returnPressed.connect(self.executar_consulta)
        self.campo_codigo.returnPressed.connect(self.executar_consulta)
        self.campo_descricao_prod.returnPressed.connect(self.executar_consulta)
        self.campo_contem_descricao_prod.returnPressed.connect(self.executar_consulta)
        self.campo_nome_cliente.returnPressed.connect(self.executar_consulta)

        layout = QVBoxLayout()
        layout_title = QHBoxLayout()
        layout_campos_01 = QHBoxLayout()
        layout_campos_02 = QHBoxLayout()
        layout_button_03 = QHBoxLayout()
        layout_button_04 = QHBoxLayout()
        self.layout_buttons = QHBoxLayout()
        self.layout_footer_label = QHBoxLayout()

        layout_title.addStretch(1)
        layout_title.addWidget(self.logo_label)
        layout_title.addWidget(self.label_title)
        layout_title.addStretch(1)

        container_sc = QVBoxLayout()
        container_sc.addWidget(self.label_msg_nota)
        container_sc.addWidget(self.campo_msg_nota)

        container_pedido = QVBoxLayout()
        container_pedido.addWidget(self.label_pedido)
        container_pedido.addWidget(self.campo_pedido)

        container_codigo = QVBoxLayout()
        container_codigo.addWidget(self.label_codigo)
        container_codigo.addWidget(self.campo_codigo)

        container_descricao_prod = QVBoxLayout()
        container_descricao_prod.addWidget(self.label_descricao_prod)
        container_descricao_prod.addWidget(self.campo_descricao_prod)

        container_contem_descricao_prod = QVBoxLayout()
        container_contem_descricao_prod.addWidget(self.label_contem_descricao_prod)
        container_contem_descricao_prod.addWidget(self.campo_contem_descricao_prod)

        container_op = QVBoxLayout()
        container_op.addWidget(self.label_orcamento)
        container_op.addWidget(self.campo_orcamento)

        container_doc_nf = QVBoxLayout()
        container_doc_nf.addWidget(self.label_nf_saida)
        container_doc_nf.addWidget(self.campo_doc_nf_entrada)

        container_data_ini = QVBoxLayout()
        container_data_ini.addWidget(self.label_data_inicio)
        container_data_ini.addWidget(self.campo_data_inicio)

        container_data_fim = QVBoxLayout()
        container_data_fim.addWidget(self.label_data_fim)
        container_data_fim.addWidget(self.campo_data_fim)

        container_cliente = QVBoxLayout()
        container_cliente.addWidget(self.label_cliente)
        container_cliente.addWidget(self.campo_nome_cliente)

        container_combobox_status_pv = QVBoxLayout()
        container_combobox_status_pv.addWidget(self.label_status_pedido)
        container_combobox_status_pv.addWidget(self.combobox_status_pedido)

        container_combobox_tipo_pv = QVBoxLayout()
        container_combobox_tipo_pv.addWidget(self.label_tipo_pedido)
        container_combobox_tipo_pv.addWidget(self.combobox_tipo_pedido)

        layout_campos_01.addLayout(container_pedido)
        layout_campos_01.addLayout(container_doc_nf)
        layout_campos_01.addLayout(container_sc)
        layout_campos_01.addLayout(container_op)
        layout_campos_01.addLayout(container_codigo)
        layout_campos_01.addLayout(container_descricao_prod)
        layout_campos_01.addLayout(container_contem_descricao_prod)
        layout_campos_02.addLayout(container_data_ini)
        layout_campos_02.addLayout(container_data_fim)
        layout_campos_02.addLayout(container_cliente)
        layout_campos_02.addLayout(container_combobox_status_pv)
        layout_campos_02.addLayout(container_combobox_tipo_pv)
        layout_campos_01.addStretch()
        layout_campos_02.addStretch()

        layout_button_03.addWidget(self.btn_pesquisar)
        layout_button_04.addWidget(self.btn_ultimas_nfe_entrada)
        layout_button_04.addWidget(self.btn_ultimos_fornecedores)
        layout_button_04.addWidget(self.btn_saldo_estoque)
        layout_button_04.addWidget(self.btn_onde_e_usado)
        layout_button_03.addWidget(self.btn_nova_janela)
        layout_button_04.addWidget(self.btn_limpar_filtro)
        layout_button_03.addWidget(self.btn_limpar)
        layout_button_04.addWidget(self.btn_abrir_desenho)
        layout_button_04.addWidget(self.btn_exportar_excel)
        layout_button_04.addWidget(self.btn_image_comparator)
        layout_button_04.addStretch()
        layout_button_03.addWidget(self.btn_fechar)
        layout_button_03.addWidget(self.btn_home)
        layout_button_03.addStretch()

        self.layout_footer_label.addStretch(1)
        self.layout_footer_label.addWidget(self.label_line_number)
        self.layout_footer_label.addWidget(self.label_indicators)
        self.layout_footer_label.addStretch(1)

        layout.addLayout(layout_title)
        layout.addWidget(self.line)
        layout.addLayout(layout_campos_01)
        layout.addLayout(layout_campos_02)
        layout.addLayout(layout_button_03)
        layout.addLayout(layout_button_04)
        layout.addLayout(self.layout_buttons)
        layout.addWidget(self.table_area)
        layout.addWidget(self.tree)
        layout.addLayout(self.layout_footer_label)

        self.setLayout(layout)

        self.setStyleSheet("""
            * {
                background-color: #363636;
            }
    
            QLabel, QCheckBox {
                color: #DFE0E2;
                font-size: 13px;
                font-weight: regular;
                padding-left: 10px; 
                font-style: "Segoe UI";
            }
            
            QLabel#label-title {
                margin: 5px;
                font-size: 22px;
                font-weight: bold;
            }
            
            QLabel#logo-enaplic {
                margin: 5px;
            }
            
            QCheckBox#checkbox-sc {
                margin-left: 10px;
                font-size: 13px;
                font-weight: normal;
            }
            
            QLabel#label-line-number {
                font-size: 16px;
                font-weight: normal;
            }
    
            QDateEdit, QComboBox {
                background-color: #EEEEEE;
                border: 1px solid #393E46;
                margin-bottom: 10px;
                padding: 5px 10px;
                border-radius: 10px;
                height: 24px;
                font-size: 16px;
            }
    
            QDateEdit::drop-down, QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
    
            QDateEdit::down-arrow, QComboBox::down-arrow {
                image: url(../resources/images/arrow.png);
                width: 10px;
                height: 10px;
            }
    
            QLineEdit {
                background-color: #EEEEEE;
                border: 1px solid #393E46;
                padding: 5px 10px;
                border-radius: 12px;
                font-size: 16px;
            }
            
            QLineEdit#cliente {
                padding: 5px 10px;
                border-radius: 10px;
                font-size: 16px;
                margin-bottom:  10px;
            }
    
            QPushButton {
                background-color: #3f37c9;
                color: #eeeeee;
                padding: 5px 10px;
                border-radius: 8px;
                font-style: "Segoe UI";
                font-size: 11px;
                height: 24px;
                font-weight: bold;
                margin: 5px;
            }
            
            QPushButton#btn_home {
                background-color: #c1121f;
            }
    
            QPushButton:hover, QPushButton:hover#btn_home {
                background-color: #EFF2F1;
                color: #3A0CA3
            }
    
            QPushButton:pressed, QPushButton:pressed#btn_home {
                background-color: #6703c5;
                color: #fff;
            }
            
            QTableWidget {
                border: 1px solid #000000;
            }
            
            QTableWidget#result_table {
                background-color: #EEEEEE;
            }
            
            QTableWidget#table_area {
                background-color: #363636;
            }
            
            QTableWidget QHeaderView::section {
                background-color: #393E46;
                color: #EEEEEE;
                font-weight: bold;
                height: 25px;
            }
    
            QTableWidget QHeaderView::section:horizontal {
                border-top: 1px solid #393E46;
                font-size: 11px;
                font-weight: bold;
                padding: 5px;
                height: 25px;
            }
    
            QTableWidget::item {
                font-weight: bold;
                padding-left: 10px;
            }
            
            QTableWidget::item:selected {
                color: #EEEEEE;
                font-weight: bold;
            }
            
            QFrame#line {
                color: white;
                background-color: white;
                border: 1px solid white;
                margin-bottom: 3px;
            }
        """)

    def return_to_main(self):
        self.close()  # Fecha a janela atual
        self.main_window.reopen()  # Reabre ou traz a janela principal ao foco

    def abrir_nova_janela(self):
        eng_window = VendasApp(self.main_window)
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

            context_menu_abrir_desenho = QAction('Abrir desenho', self)
            context_menu_abrir_desenho.triggered.connect(lambda: abrir_desenho(self, table))

            context_menu_image_comparator = QAction('Abrir ImageComparator®', self)
            context_menu_image_comparator.triggered.connect(lambda: run_image_comparator_exe())

            context_menu_ultimo_fornecedor = QAction('Histórico de Fornecedores', self)
            context_menu_ultimo_fornecedor.triggered.connect(lambda: executar_ultimos_fornecedores(self, table))

            context_menu_ultimas_nfe = QAction('Histórico de Notas Fiscais de Entrada', self)
            context_menu_ultimas_nfe.triggered.connect(lambda: consultar_ultimas_nfe(self, table))

            context_menu_consultar_onde_usado = QAction('Onde é usado?', self)
            context_menu_consultar_onde_usado.triggered.connect(lambda: executar_consulta_onde_usado(self, table))

            context_menu_saldo_estoque = QAction('Saldo em estoque', self)
            context_menu_saldo_estoque.triggered.connect(lambda: executar_saldo_em_estoque(self, table))

            context_menu_nova_janela = QAction('Nova janela', self)
            context_menu_nova_janela.triggered.connect(self.abrir_nova_janela)

            menu.addAction(context_menu_nova_janela)
            menu.addSeparator()
            menu.addAction(context_menu_abrir_desenho)
            menu.addAction(context_menu_image_comparator)
            menu.addSeparator()
            menu.addAction(context_menu_consultar_onde_usado)
            menu.addAction(context_menu_saldo_estoque)
            menu.addSeparator()
            menu.addAction(context_menu_ultimo_fornecedor)
            menu.addAction(context_menu_ultimas_nfe)

            menu.exec_(table.viewport().mapToGlobal(position))

    def add_clear_button(self, line_edit):
        clear_icon = self.style().standardIcon(QStyle.SP_LineEditClearButton)

        line_edit_height = line_edit.height()
        pixmap = clear_icon.pixmap(line_edit_height - 4, line_edit_height - 4)
        larger_clear_icon = QIcon(pixmap)

        clear_action = QAction(larger_clear_icon, "Limpar", line_edit)
        clear_action.triggered.connect(line_edit.clear)
        line_edit.addAction(clear_action, QLineEdit.TrailingPosition)

    def configurar_tabela(self, dataframe):
        self.table_area.hide()
        self.tree.show()
        self.tree.setAlternatingRowColors(True)

        # Definir número de colunas e cabeçalhos
        self.tree.setColumnCount(len(dataframe.columns))
        self.tree.setHorizontalHeaderLabels(dataframe.columns)

        # Definir largura de colunas específicas
        self.tree.setColumnWidth(0, 100)  # Coluna 'STATUS'
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

    def clean_screen(self):
        self.table_area.show()
        self.tree.hide()
        self.campo_msg_nota.clear()
        self.campo_pedido.clear()
        self.campo_codigo.clear()
        self.campo_descricao_prod.clear()
        self.campo_contem_descricao_prod.clear()
        self.campo_nome_cliente.clear()
        self.campo_orcamento.clear()
        self.combobox_status_pedido.setCurrentText('-')
        self.combobox_tipo_pedido.setCurrentText('-')
        self.tree.setColumnCount(0)
        self.tree.setRowCount(0)
        self.label_line_number.hide()
        self.label_indicators.hide()

        self.btn_abrir_desenho.hide()
        self.btn_exportar_excel.hide()
        self.btn_image_comparator.hide()
        self.btn_onde_e_usado.hide()
        self.btn_saldo_estoque.hide()
        self.btn_ultimos_fornecedores.hide()
        self.btn_ultimas_nfe_entrada.hide()
        self.btn_limpar_filtro.hide()

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
            self.btn_abrir_desenho.hide()
            self.btn_exportar_excel.hide()
            self.btn_onde_e_usado.hide()
            self.btn_saldo_estoque.hide()
            self.btn_ultimos_fornecedores.hide()
            self.btn_ultimas_nfe_entrada.hide()
            self.btn_image_comparator.hide()
        else:
            self.btn_abrir_desenho.show()
            self.btn_exportar_excel.show()
            self.btn_onde_e_usado.show()
            self.btn_saldo_estoque.show()
            self.btn_ultimos_fornecedores.show()
            self.btn_ultimas_nfe_entrada.show()
            self.btn_image_comparator.show()

    def controle_campos_formulario(self, status):
        self.campo_msg_nota.setEnabled(status)
        self.campo_codigo.setEnabled(status)
        self.campo_descricao_prod.setEnabled(status)
        self.campo_contem_descricao_prod.setEnabled(status)
        self.campo_nome_cliente.setEnabled(status)
        self.campo_orcamento.setEnabled(status)
        self.campo_data_inicio.setEnabled(status)
        self.campo_data_fim.setEnabled(status)
        self.combobox_status_pedido.setEnabled(status)
        self.btn_pesquisar.setEnabled(status)
        self.btn_exportar_excel.setEnabled(status)
        self.btn_saldo_estoque.setEnabled(status)
        self.btn_onde_e_usado.setEnabled(status)
        self.btn_ultimos_fornecedores.setEnabled(status)
        self.btn_image_comparator.setEnabled(status)

    def query_consulta(self):
        pedido_venda = self.campo_pedido.text().upper().strip()
        orcamento = self.campo_orcamento.text().upper().strip()
        doc_nf_saida = self.campo_doc_nf_entrada.text().upper().strip()
        codigo_produto = self.campo_codigo.text().upper().strip()
        nome_cliente = self.campo_nome_cliente.text().upper().strip()
        descricao_produto = self.campo_descricao_prod.text().upper().strip()
        contem_descricao = self.campo_contem_descricao_prod.text().upper().strip()
        mensagem_nota = self.campo_msg_nota.text().upper().strip()
        status_pedido = self.combobox_status_pedido.currentData()
        tipo_pedido = self.combobox_tipo_pedido.currentData()

        palavras_contem_descricao = contem_descricao.split('*')
        clausulas_contem_descricao = " AND ".join(
            [f"itemPedidoVenda.C6_DESCRI LIKE '%{palavra}%'" for palavra in palavras_contem_descricao])

        data_inicio_formatada = self.campo_data_inicio.date().toString("yyyyMMdd")
        data_fim_formatada = self.campo_data_fim.date().toString("yyyyMMdd")

        if data_inicio_formatada != '' and data_fim_formatada != '':
            filtro_data = f"AND C5_EMISSAO >= '{data_inicio_formatada}' AND C5_EMISSAO <= '{data_fim_formatada}'"
        else:
            filtro_data = ''

        query = f"""
                -- QUERY PARA PROJETAR INFORMAÇÕES REFERENTE AOS PEDIDOS DE VENDA E NOTAS FISCAIS DE SAÍDA
                -- @statusPedido = 1 (PV ABERTO/FECHADO)
                -- @statusPedido = 2 (PV FECHADO)
                -- @statusPedido = 3 (PV ABERTO) 
                DECLARE @statusPedido INT = {status_pedido};
                SELECT
                    CASE
                        WHEN C6_XTPOPER = 1 THEN 'QP'
                        WHEN C6_XTPOPER = 2 THEN 'QR'
                        ELSE 'Outros'
                    END AS 'TIPO PV',
                    C6_CLI AS 'CÓD. CLIENTE',
                    C5_ZZNOME AS 'CLIENTE',
                    C6_NUMORC AS 'ORÇAMENTO',
                    C6_NUM AS 'PV',
                    C5_EMISSAO 'PV ABERTO EM:',
                    CASE
                        WHEN C1_NUM IS NULL THEN '' 
                        ELSE C1_NUM
                    END AS 'SOLIC. COMPRA',
                    CASE 
                        WHEN C1_EMISSAO IS NULL THEN ''
                        ELSE C1_EMISSAO
                    END AS 'SC ABERTA EM:',
                    CASE 
                        WHEN C2_NUM IS NULL THEN ''
                        ELSE C2_NUM
                    END AS 'OP',
                    CASE 
                        WHEN C2_EMISSAO IS NULL THEN ''
                        ELSE C2_EMISSAO 
                    END AS 'OP ABERTA EM:',
                    C6_ENTREG AS 'DATA DE ENTREGA',
                    C6_PRODUTO AS 'CÓDIGO',
                    C6_DESCRI AS 'DESCRIÇÃO',
                    C6_UM AS 'UN.', 
                    C6_QTDVEN AS 'QTD. VENDA', 
                    C6_PRCVEN AS 'PREÇO VENDA R$', 
                    C6_VALOR AS 'TOTAL ITEM R$',
                    C6_DATFAT AS 'DATA DE FATURAMENTO',
                    CASE
                        WHEN C5_NOTA = 'XXXXXXXXX' THEN 'Resíduo'
                        ELSE C5_NOTA
                    END AS 'DOC. NF SAÍDA',
                    C5_MENNOTA AS 'MENSAGEM NOTA'
                FROM 
                    {self.database}.dbo.SC6010 itemPedidoVenda
                INNER JOIN
                    {self.database}.dbo.SC5010 cabecalhoPedidoVenda
                ON
                    itemPedidoVenda.C6_NUM = cabecalhoPedidoVenda.C5_NUM
                LEFT JOIN
                    SC1010 tabelaSolicCompras
                ON
                    itemPedidoVenda.C6_NUM = tabelaSolicCompras.C1_ZZNUMQP
                    AND itemPedidoVenda.C6_PRODUTO = tabelaSolicCompras.C1_PRODUTO
                    AND	itemPedidoVenda.D_E_L_E_T_ = tabelaSolicCompras.D_E_L_E_T_
                LEFT JOIN 
                    {self.database}.dbo.SC2010 tabelaOrdemDeProducao
                ON
                    itemPedidoVenda.C6_NUM = tabelaOrdemDeProducao.C2_ZZNUMQP
                    AND itemPedidoVenda.C6_PRODUTO = tabelaOrdemDeProducao.C2_PRODUTO
                    AND itemPedidoVenda.D_E_L_E_T_ = tabelaOrdemDeProducao.D_E_L_E_T_ 
                WHERE 
                    C6_XTPOPER LIKE '{tipo_pedido}%' -- C6_XTPOPER = 1 (QP) / 2 (QR) / 3 (ND - OUTROS)
                    AND	C6_NUM LIKE '%{pedido_venda}'
                    AND	C6_PRODUTO LIKE '{codigo_produto}%'
                    AND	C6_DESCRI LIKE '{descricao_produto}%'
                    AND	C6_NUMORC LIKE '%{orcamento}%'
                    AND C5_NOTA LIKE '%{doc_nf_saida}'
                    AND C5_ZZNOME LIKE '{nome_cliente}%'
                    AND C5_MENNOTA LIKE '%{mensagem_nota}%'
                    AND ((@statusPedido = 1 AND C5_NOTA LIKE '%{doc_nf_saida}') -- open/closed
                        OR (@statusPedido = 2 AND C5_NOTA LIKE '%{doc_nf_saida}' AND C5_NOTA <> '         ') -- closed
                        OR (@statusPedido = 3 AND C5_NOTA LIKE '%{doc_nf_saida}' AND C5_NOTA = '         ')) -- open
                    AND	itemPedidoVenda.D_E_L_E_T_ <> '*'
                    AND cabecalhoPedidoVenda.D_E_L_E_T_ <> '*'
                    AND {clausulas_contem_descricao}
                    {filtro_data}
                ORDER BY 
                    itemPedidoVenda.R_E_C_N_O_ DESC;
                """

        return query

    def atualizar_tabela(self, dataframe):
        self.tree.setRowCount(len(dataframe.index))
        self.tree.clearContents()
        self.tree.setRowCount(0)
        self.tree.setColumnCount(0)
        self.configurar_tabela(dataframe)
        # self.tree.setSortingEnabled(False)

        # Construir caminhos relativos
        script_dir = os.path.dirname(os.path.abspath(__file__))
        no_pc = os.path.join(script_dir, '..', 'resources', 'images', 'red.png')
        end_order_path = os.path.join(script_dir, '..', 'resources', 'images', 'green.png')

        no_pc = QIcon(no_pc)
        end_order = QIcon(end_order_path)

        for i, (index, row) in enumerate(dataframe.iterrows()):
            self.tree.insertRow(i)
            for column_name, value in row.items():
                if value is not None:
                    if column_name == 'STATUS':
                        item = QTableWidgetItem()
                        if row['DOC. NF SAÍDA'] != '         ':
                            item.setIcon(end_order)
                            item.setText('FECHADO')
                            dataframe.at[index, 'STATUS'] = 'FECHADO'
                        else:
                            item.setIcon(no_pc)
                            item.setText('ABERTO')
                            dataframe.at[index, 'STATUS'] = 'ABERTO'
                    else:
                        item = QTableWidgetItem(str(value).strip())
                        if column_name in ['CLIENTE', 'DESCRIÇÃO', 'MENSAGEM NOTA']:
                            item.setTextAlignment(Qt.AlignLeft)
                        elif column_name in ['PREÇO VENDA R$', 'TOTAL ITEM R$']:
                            item.setTextAlignment(Qt.AlignRight)
                        else:
                            item.setTextAlignment(Qt.AlignCenter)
                else:
                    item = QTableWidgetItem('')
                self.tree.setItem(i, list(row.index).index(column_name), item)

        self.table_line_number(dataframe.shape[0])
        self.exibir_indicadores(dataframe)
        self.tree.viewport().update()
        # self.tree.setSortingEnabled(True)
        self.controle_campos_formulario(True)
        self.button_visible_control(True)

    def exibir_indicadores(self, dataframe):
        coluna_status = 'STATUS'
        pv_aberto = dataframe[coluna_status].apply(
            lambda x: x.strip() == 'ABERTO' if isinstance(x, str) else True).sum()
        pv_fechado = dataframe[coluna_status].apply(
            lambda x: x.strip() == 'FECHADO' if isinstance(x, str) else True).sum()

        indicadores_table = f"""
                <table border="1" cellspacing="2" cellpadding="4" style="border-collapse: collapse; text-align: left; 
                width: 100%;">
                    <tr>
                        <th style="text-align: middle; vertical-align: middle;">STATUS PV</th>
                        <th style="text-align: right; vertical-align: middle;">QUANTIDADE</th>
                    </tr>
                    <tr>
                        <td style="vertical-align: middle;">ABERTO</td>
                        <td style="text-align: right; vertical-align: middle;">{pv_aberto}</td>
                    </tr>
                    <tr>
                        <td style="vertical-align: middle;">FECHADO</td>
                        <td style="text-align: right; vertical-align: middle;">{pv_fechado}</td>
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
            return False
        else:
            self.controle_campos_formulario(True)
            self.button_visible_control(False)
            return True

    def executar_consulta(self):
        query_consulta_filtro = self.query_consulta()

        self.label_line_number.hide()
        self.label_indicators.hide()
        self.controle_campos_formulario(False)
        self.button_visible_control(False)

        conn_str = (f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};'
                    f'PWD={self.password}')
        self.engine = create_engine(f'mssql+pyodbc:///?odbc_connect={conn_str}')

        try:
            self.df = pd.read_sql(query_consulta_filtro, self.engine)
            self.df.insert(0, 'STATUS', '')

            remove_zero_columns = ['ORÇAMENTO', 'PV', 'SOLIC. COMPRA', 'DOC. NF SAÍDA']
            self.df[remove_zero_columns] = self.df[remove_zero_columns].apply(
                lambda x: x.str.lstrip('0'))
            
            date_columns = ['PV ABERTO EM:', 'SC ABERTA EM:', 'OP ABERTA EM:', 'DATA DE ENTREGA', 'DATA DE FATURAMENTO']
            self.df[date_columns] = self.df[date_columns].apply(lambda col: pd.to_datetime(
                col, format='%Y%m%d', errors='coerce').dt.strftime('%d/%m/%Y').fillna(''))

            format_number_columns = ['QTD. VENDA', 'PREÇO VENDA R$', 'TOTAL ITEM R$']
            self.df[format_number_columns] = self.df[format_number_columns].apply(
                lambda col: pd.to_numeric(col, errors='coerce').apply(format_number))

            line_number = self.df.shape[0]

            if self.table_line_number(line_number):
                self.clean_screen()
                exibir_mensagem("EUREKA® Vendas", 'Nenhum resultado encontrado nesta pesquisa.', "info")
                return

            dialog = loading_dialog(self, "Carregando...", "🤖 Processando dados do TOTVS..."
                                                           "\n\n🤖 Por favor, aguarde.\n\nEureka®")

            self.atualizar_tabela(self.df)
            self.df_original = self.df.copy()
            dialog.close()

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
        self.filtro_dialog = FilterDialog(self, nome_coluna, self.df, self.lista_status_tabela)

        # Execute the dialog and wait for the user to close it
        if self.filtro_dialog.exec_() == QDialog.Accepted:
            # Get the selected filters from the dialog
            filtro_selecionado = self.filtro_dialog.get_filtros_selecionados()
            if filtro_selecionado:
                # Apply the filter to the dataframe
                self.df = self.df[self.df[nome_coluna].isin(filtro_selecionado)]

                self.atualizar_tabela(self.df)
                self.btn_limpar_filtro.show()
        # Reativa os sinais do cabeçalho
        self.tree.horizontalHeader().blockSignals(False)

    def limpar_filtros(self):
        dialog = loading_dialog(self, "Eureka®", "🤖 Removendo filtros...\n\nRestaurando a consulta inicial")
        self.atualizar_tabela(self.df_original)
        self.btn_limpar_filtro.hide()
        self.df = self.df_original.copy()
        dialog.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VendasApp()
    window.showMaximized()
    sys.exit(app.exec_())
