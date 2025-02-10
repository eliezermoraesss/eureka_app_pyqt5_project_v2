import locale
import os
import sys

# Caminho absoluto para o diretório onde o módulo src está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from datetime import datetime

import pandas as pd
from PyQt5.QtCore import Qt, QDate, QProcess, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QTableWidget, QTableWidgetItem, QHeaderView, QStyle, QAction, QDateEdit, QLabel, \
    QComboBox, QSizePolicy, QTabWidget, QMenu, QCheckBox
from sqlalchemy import create_engine

from src.app.utils.consultar_onde_usado import executar_consulta_onde_usado
from src.app.utils.consultar_saldo_estoque import executar_saldo_em_estoque
from src.app.utils.consultar_ultimos_fornec import executar_ultimos_fornecedores
from src.app.utils.consultar_ultimas_nfe import consultar_ultimas_nfe
from src.app.utils.db_mssql import setup_mssql
from src.app.utils.load_session import load_session
from src.app.utils.utils import exibir_mensagem, copiar_linha, abrir_nova_janela, exportar_excel


class SolicitacaoComprasWindow(QWidget):
    guia_fechada = pyqtSignal()

    def __init__(self):
        super().__init__()
        user_data = load_session()
        username = user_data["username"]
        role = user_data["role"]
        self.username, self.password, self.database, self.server = setup_mssql()
        self.driver = '{SQL Server}'

        self.setWindowTitle(f"Eureka® Compras - Solicitação de Compras  . {username} ({role})")
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

        self.engine = None
        self.combobox_armazem = QComboBox(self)
        self.combobox_armazem.setEditable(False)
        self.combobox_armazem.setObjectName('combobox-armazem')

        self.combobox_armazem.addItem("", None)

        armazens = {
            "01": "MATERIA PRIMA",
            "02": "PROD. INTERMEDIARIO",
            "03": "PROD. COMERCIAIS",
            "04": "PROD. ACABADOS",
            "05": "MAT.PRIMA IMP.INDIR.",
            "06": "PROD. ELETR.NACIONAL",
            "07": "PROD.ELETR.IMP.DIRET",
            "08": "SRV INDUSTRIALIZACAO",
            "09": "SRV TERCEIROS",
            "10": "PROD.COM.IMP.INDIR.",
            "11": "PROD.COM.IMP.DIRETO",
            "12": "MAT.PRIMA IMP.DIR.ME",
            "13": "E.P.I-MAT.SEGURANCA",
            "14": "PROD.ELETR.IMP.INDIR",
            "22": "ATIVOS",
            "60": "PROD-FERR CONSUMIVEI",
            "61": "EMBALAGENS",
            "70": "SERVICOS GERAIS",
            "71": "PRODUTOS AUTOMOTIVOS",
            "77": "OUTROS",
            "80": "SUCATAS",
            "85": "SERVICOS PRESTADOS",
            "96": "ARMAZ.NAO APLICAVEL",
            "97": "TRAT. SUPERFICIAL"
        }

        for key, value in armazens.items():
            self.combobox_armazem.addItem(key + ' - ' + value, key)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_enaplic_path = os.path.join(script_dir, '..', '..', 'resources', 'images', 'LOGO.jpeg')
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

        self.label_line_number = QLabel("", self)
        self.label_line_number.setObjectName("label-line-number")
        self.label_line_number.setVisible(False)

        self.checkbox_exibir_somente_sc_com_pedido = QCheckBox("Ocultar Solic. de Compras SEM Pedido de Compras", self)
        self.checkbox_exibir_somente_sc_com_pedido.setObjectName("checkbox-sc")
        self.checkbox_exibir_somente_sc_com_pedido.setVisible(False)

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

        self.label_qp = QLabel("Número da QP:", self)
        self.label_qp.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_OP = QLabel("Número da OP:", self)
        self.label_OP.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_data_inicio = QLabel("A partir de:", self)
        self.label_data_fim = QLabel("Até:", self)
        self.label_armazem = QLabel("Armazém:", self)
        self.label_fornecedor = QLabel("Razão social fornecedor:", self)
        self.label_nm_fantasia_forn = QLabel("Nome Fantasia fornecedor:", self)

        self.campo_sc = QLineEdit(self)
        self.campo_sc.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_sc.setMaxLength(6)
        self.campo_sc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_clear_button(self.campo_sc)

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

        self.campo_qp = QLineEdit(self)
        self.campo_qp.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_qp.setMaxLength(6)
        self.campo_qp.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_clear_button(self.campo_qp)

        self.campo_OP = QLineEdit(self)
        self.campo_OP.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_OP.setMaxLength(6)
        self.campo_OP.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_clear_button(self.campo_OP)

        self.campo_razao_social_fornecedor = QLineEdit(self)
        self.campo_razao_social_fornecedor.setObjectName("forn-raz")
        self.campo_razao_social_fornecedor.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_razao_social_fornecedor.setMaximumWidth(250)  # Ajuste conforme necessário
        self.campo_razao_social_fornecedor.setMaxLength(40)
        # self.add_clear_button(self.campo_razao_social_fornecedor)

        self.campo_nm_fantasia_fornecedor = QLineEdit(self)
        self.campo_nm_fantasia_fornecedor.setObjectName("forn-fantasia")
        self.campo_nm_fantasia_fornecedor.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_nm_fantasia_fornecedor.setMaximumWidth(250)  # Ajuste conforme necessário
        self.campo_nm_fantasia_fornecedor.setMaxLength(40)
        self.campo_nm_fantasia_fornecedor.setMaxLength(40)
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

        self.btn_sc = QPushButton("Pesquisar", self)
        self.btn_sc.clicked.connect(self.executar_consulta_solic_compras)
        self.btn_sc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_onde_e_usado = QPushButton("Onde é usado?", self)
        self.btn_onde_e_usado.clicked.connect(lambda: executar_consulta_onde_usado(self, self.tree))
        self.btn_onde_e_usado.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_onde_e_usado.hide()

        self.btn_saldo_estoque = QPushButton("Saldos em Estoque", self)
        self.btn_saldo_estoque.clicked.connect(lambda: executar_saldo_em_estoque(self, self.tree))
        self.btn_saldo_estoque.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_saldo_estoque.hide()

        self.btn_ultimos_fornecedores = QPushButton("Últimos fornecedores", self)
        self.btn_ultimos_fornecedores.clicked.connect(lambda: executar_ultimos_fornecedores(self, self.tree))
        self.btn_ultimos_fornecedores.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_ultimos_fornecedores.hide()

        self.btn_ultimas_nfe = QPushButton("Últimas Notas Fiscais", self)
        self.btn_ultimas_nfe.clicked.connect(lambda: consultar_ultimas_nfe(self, self.tree))
        self.btn_ultimas_nfe.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_ultimas_nfe.hide()

        self.btn_limpar = QPushButton("Limpar", self)
        self.btn_limpar.clicked.connect(self.clean_screen)
        self.btn_limpar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_nova_janela = QPushButton("Nova Janela", self)
        self.btn_nova_janela.clicked.connect(lambda : abrir_nova_janela(self, SolicitacaoComprasWindow()))
        self.btn_nova_janela.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_exportar_excel = QPushButton("Exportar Excel", self)
        self.btn_exportar_excel.clicked.connect(lambda: exportar_excel(self, self.tree))
        self.btn_exportar_excel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_exportar_excel.hide()

        self.btn_fechar = QPushButton("Fechar", self)
        self.btn_fechar.clicked.connect(self.close)
        self.btn_fechar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.campo_sc.returnPressed.connect(self.executar_consulta_solic_compras)
        self.campo_pedido.returnPressed.connect(self.executar_consulta_solic_compras)
        self.campo_codigo.returnPressed.connect(self.executar_consulta_solic_compras)
        self.campo_descricao_prod.returnPressed.connect(self.executar_consulta_solic_compras)
        self.campo_contem_descricao_prod.returnPressed.connect(self.executar_consulta_solic_compras)
        self.campo_qp.returnPressed.connect(self.executar_consulta_solic_compras)
        self.campo_OP.returnPressed.connect(self.executar_consulta_solic_compras)
        self.campo_razao_social_fornecedor.returnPressed.connect(self.executar_consulta_solic_compras)
        self.campo_nm_fantasia_fornecedor.returnPressed.connect(self.executar_consulta_solic_compras)

        layout = QVBoxLayout()
        layout_campos_01 = QHBoxLayout()
        layout_campos_02 = QHBoxLayout()
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
        container_descricao_prod.addWidget(self.campo_descricao_prod)

        container_contem_descricao_prod = QVBoxLayout()
        container_contem_descricao_prod.addWidget(self.label_contem_descricao_prod)
        container_contem_descricao_prod.addWidget(self.campo_contem_descricao_prod)

        container_op = QVBoxLayout()
        container_op.addWidget(self.label_OP)
        container_op.addWidget(self.campo_OP)

        container_qp = QVBoxLayout()
        container_qp.addWidget(self.label_qp)
        container_qp.addWidget(self.campo_qp)

        container_data_ini = QVBoxLayout()
        container_data_ini.addWidget(self.label_data_inicio)
        container_data_ini.addWidget(self.campo_data_inicio)

        container_data_fim = QVBoxLayout()
        container_data_fim.addWidget(self.label_data_fim)
        container_data_fim.addWidget(self.campo_data_fim)

        container_combobox_armazem = QVBoxLayout()
        container_combobox_armazem.addWidget(self.label_armazem)
        container_combobox_armazem.addWidget(self.combobox_armazem)

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
        layout_campos_01.addLayout(container_codigo)
        layout_campos_01.addLayout(container_descricao_prod)
        layout_campos_01.addLayout(container_contem_descricao_prod)
        layout_campos_01.addLayout(container_op)
        layout_campos_02.addLayout(container_data_ini)
        layout_campos_02.addLayout(container_data_fim)
        layout_campos_02.addLayout(container_combobox_armazem)
        layout_campos_02.addLayout(container_fornecedor)
        layout_campos_02.addLayout(container_nm_fantasia_forn)
        layout_campos_02.addWidget(self.checkbox_exibir_somente_sc_com_pedido)
        layout_campos_01.addStretch()
        layout_campos_02.addStretch()

        self.layout_buttons.addStretch()
        self.layout_buttons.addWidget(self.btn_sc)
        self.layout_buttons.addWidget(self.btn_ultimos_fornecedores)
        self.layout_buttons.addWidget(self.btn_ultimas_nfe)
        self.layout_buttons.addWidget(self.btn_saldo_estoque)
        self.layout_buttons.addWidget(self.btn_onde_e_usado)
        self.layout_buttons.addWidget(self.btn_nova_janela)
        self.layout_buttons.addWidget(self.btn_limpar)
        self.layout_buttons.addWidget(self.btn_exportar_excel)
        self.layout_buttons.addWidget(self.btn_fechar)
        self.layout_buttons.addStretch()

        self.layout_footer_label.addStretch(1)
        self.layout_footer_label.addWidget(self.label_line_number)
        self.layout_footer_label.addStretch(1)
        self.layout_footer_label.addWidget(self.logo_label)

        layout.addLayout(layout_campos_01)
        layout.addLayout(layout_campos_02)
        layout.addLayout(self.layout_buttons)
        layout.addWidget(self.table_area)
        layout.addWidget(self.tree)
        layout.addLayout(self.layout_footer_label)

        self.setLayout(layout)

        self.setStyleSheet("""
            * {
                background-color: #393E46;
            }
    
            QLabel, QCheckBox {
                color: #DFE0E2;
                font-size: 13px;
                font-weight: regular;
                padding-left: 10px; 
                font-style: "Segoe UI";
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
                margin-bottom: 20px;
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
            
            QLineEdit#forn-raz, QLineEdit#forn-fantasia {
                padding: 5px 10px;
                border-radius: 10px;
                font-size: 16px;
                margin-bottom:  20px;
            }
    
            QPushButton {
                background-color: #347928;
                color: #eeeeee;
                padding: 7px 10px;
                border: 2px solid #347928;
                border-radius: 12px;
                font-style: "Segoe UI";
                font-size: 13px;
                height: 20px;
                font-weight: bold;
                margin: 10px 5px 5px 5px;
            }
            
            QPushButton#btn_engenharia {
                border: 2px solid #0a79f8;
                background-color: #0a79f8;
            }
            
            QPushButton#PCP {
                border: 2px solid #DC5F00;
                background-color: #DC5F00;
            }
    
            QPushButton:hover, QPushButton:hover#btn_engenharia, QPushButton#PCP:hover {
                background-color: #EFF2F1;
                color: #3A0CA3
            }
    
            QPushButton:pressed, QPushButton:pressed#btn_engenharia, QPushButton#PCP:pressed {
                background-color: #6703c5;
                color: #fff;
            }
            
            QTableWidget#result_table {
                background-color: #EEEEEE;
            }
            
            QTableWidget#table_area {
                background-color: #393E46;
            }
            
            QTableWidget QHeaderView::section {
                background-color: #302c2c;
                color: #EEEEEE;
                font-weight: bold;
                height: 25px;
            }
    
            QTableWidget QHeaderView::section:horizontal {
                border-top: 1px solid #333;
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
        """)

    def add_today_button(self, date_edit):
        calendar = date_edit.calendarWidget()
        calendar.setGeometry(10, 10, 600, 400)
        btn_today = QPushButton("Hoje", calendar)
        btn_today.setObjectName("today_button")
        largura, altura = 50, 20
        btn_today.setGeometry(20, 5, largura, altura)
        btn_today.clicked.connect(lambda: date_edit.setDate(QDate.currentDate()))

    def numero_linhas_consulta(self, query_consulta):
        order_by_followup = f"""ORDER BY PC.R_E_C_N_O_ DESC;"""
        order_by_sc = f"""ORDER BY "SOLIC. COMPRA" DESC;"""

        query_sem_order_by = ""
        if order_by_followup in query_consulta:
            query_sem_order_by = query_consulta.replace(order_by_followup, "")
        elif order_by_sc in query_consulta:
            query_sem_order_by = query_consulta.replace(order_by_sc, "")

        query = f"""
            SELECT 
                COUNT(*) AS total_records
            FROM 
                ({query_sem_order_by}
                )
            AS combined_results;
        """
        return query

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
                            self.guias_abertas_ultimas_nfe.remove(codigo_guia_fechada)

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

            context_menu_ultimo_fornecedor = QAction('Últimos fornecedores', self)
            context_menu_ultimo_fornecedor.triggered.connect(lambda: executar_ultimos_fornecedores(self, table))

            context_menu_ultimas_nfe = QAction('Últimas Notas Fiscais', self)
            context_menu_ultimas_nfe.triggered.connect(lambda: consultar_ultimas_nfe(self, table))
            menu.addAction(context_menu_ultimas_nfe)

            context_menu_consultar_onde_usado = QAction('Onde é usado?', self)
            context_menu_consultar_onde_usado.triggered.connect(lambda: executar_consulta_onde_usado(self, table))

            context_menu_saldo_estoque = QAction('Saldo em estoque', self)
            context_menu_saldo_estoque.triggered.connect(lambda: executar_saldo_em_estoque(self, table))

            context_menu_nova_janela = QAction('Nova janela', self)
            context_menu_nova_janela.triggered.connect(lambda: abrir_nova_janela(self, SolicitacaoComprasWindow()))

            menu.addAction(context_menu_ultimo_fornecedor)
            menu.addAction(context_menu_consultar_onde_usado)
            menu.addAction(context_menu_saldo_estoque)
            menu.addAction(context_menu_nova_janela)

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
        self.tree.setColumnWidth(0, 20)  # Coluna 'ICONES DE STATUS' (índice 0) com 100px
        for col in range(1, len(dataframe.columns)):
            self.tree.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)

        # Configurar propriedades da tabela
        self.tree.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tree.setSelectionBehavior(QTableWidget.SelectRows)
        self.tree.setSelectionMode(QTableWidget.SingleSelection)
        self.tree.itemDoubleClicked.connect(copiar_linha)
        self.tree.setFont(QFont(self.fonte_tabela, self.tamanho_fonte_tabela))
        self.tree.verticalHeader().setDefaultSectionSize(self.altura_linha)

        # Conectar sinal de clique para ordenar a tabela
        self.tree.horizontalHeader().sectionClicked.connect(self.ordenar_tabela)

        # Permitir que a última coluna se estenda para preencher o espaço
        self.tree.horizontalHeader().setStretchLastSection(True)

        # Menu de contexto personalizado
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(lambda pos: self.show_context_menu(pos, self.tree))

    def ordenar_tabela(self, logical_index):
        # Obter o índice real da coluna (considerando a ordem de classificação)
        index = self.tree.horizontalHeader().sortIndicatorOrder()

        # Definir a ordem de classificação
        order = Qt.AscendingOrder if index == 0 else Qt.DescendingOrder

        # Ordenar a tabela pela coluna clicada
        self.tree.sortItems(logical_index, order)

    def clean_screen(self):
        self.table_area.show()
        self.tree.hide()
        self.campo_sc.clear()
        self.campo_pedido.clear()
        self.campo_codigo.clear()
        self.campo_descricao_prod.clear()
        self.campo_contem_descricao_prod.clear()
        self.campo_razao_social_fornecedor.clear()
        self.campo_nm_fantasia_fornecedor.clear()
        self.campo_qp.clear()
        self.campo_OP.clear()
        self.tree.setColumnCount(0)
        self.tree.setRowCount(0)
        self.checkbox_exibir_somente_sc_com_pedido.setChecked(False)
        self.label_line_number.hide()

        self.btn_exportar_excel.hide()
        self.btn_onde_e_usado.hide()
        self.btn_saldo_estoque.hide()
        self.btn_ultimos_fornecedores.hide()
        self.btn_ultimas_nfe.hide()

        self.guias_abertas.clear()
        self.guias_abertas_onde_usado.clear()
        self.guias_abertas_saldo.clear()
        self.guias_abertas_ultimos_fornecedores.clear()
        self.guias_abertas_ultimas_nfe.clear()

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
        else:
            self.btn_exportar_excel.show()
            self.btn_onde_e_usado.show()
            self.btn_saldo_estoque.show()
            self.btn_ultimos_fornecedores.show()
            self.btn_ultimas_nfe.show()

    def controle_campos_formulario(self, status):
        self.campo_sc.setEnabled(status)
        self.campo_codigo.setEnabled(status)
        self.campo_descricao_prod.setEnabled(status)
        self.campo_contem_descricao_prod.setEnabled(status)
        self.campo_razao_social_fornecedor.setEnabled(status)
        self.campo_qp.setEnabled(status)
        self.campo_OP.setEnabled(status)
        self.campo_data_inicio.setEnabled(status)
        self.campo_data_fim.setEnabled(status)
        self.combobox_armazem.setEnabled(status)
        self.btn_exportar_excel.setEnabled(status)
        self.btn_saldo_estoque.setEnabled(status)
        self.btn_onde_e_usado.setEnabled(status)
        self.btn_ultimos_fornecedores.setEnabled(status)

    def query_solic_compras(self):
        numero_sc = self.campo_sc.text().upper().strip()
        numero_pedido = self.campo_pedido.text().upper().strip()
        numero_qp = self.campo_qp.text().upper().strip()
        numero_op = self.campo_OP.text().upper().strip()
        codigo_produto = self.campo_codigo.text().upper().strip()
        descricao_produto = self.campo_descricao_prod.text().upper().strip()
        contem_descricao = self.campo_contem_descricao_prod.text().upper().strip()

        cod_armazem = self.combobox_armazem.currentData()
        if cod_armazem is None:
            cod_armazem = ''

        palavras_contem_descricao = contem_descricao.split('*')
        clausulas_contem_descricao = " AND ".join(
            [f"SC.C1_DESCRI LIKE '%{palavra}%'" for palavra in palavras_contem_descricao])

        data_inicio_formatada = self.campo_data_inicio.date().toString("yyyyMMdd")
        data_fim_formatada = self.campo_data_fim.date().toString("yyyyMMdd")

        if data_fim_formatada != '' and data_fim_formatada != '':
            filtro_data = f"AND C1_EMISSAO >= '{data_inicio_formatada}' AND C1_EMISSAO <= '{data_fim_formatada}'"
        else:
            filtro_data = ''

        query_solic_compras = f"""
                SELECT
                    SC.C1_ZZNUMQP AS "QP",
                    SC.C1_PEDIDO AS "PEDIDO DE COMPRA",
                    SC.C1_NUM AS "SOLIC. COMPRA",
                    SC.C1_PRODUTO AS "CÓDIGO",
                    SC.C1_DESCRI AS "DESCRIÇÃO",
                    SC.C1_QUANT AS "QTD. SOLIC. COMPRAS",
                    SC.C1_UM AS "UN.",
                    SC.C1_EMISSAO AS "SC ABERTA EM:",
                    SC.C1_ITEM AS "ITEM SC",
                    SC.C1_ITEMPED AS "ITEM PC",
                    SC.C1_GRPRD AS "GRUPO",
                    SC.C1_LOCAL AS "CÓD. ARMAZÉM",
                    ARM.NNR_DESCRI AS "DESCRIÇÃO ARMAZÉM",
                    SC.C1_FORNECE AS "CÓD. FORNECEDOR",
                    PROD.B1_ZZLOCAL AS "ENDEREÇO ALMOXARIFADO",
                    SC.C1_OBS AS "OBSERVAÇÃO SOLIC. COMPRA",
                    US.USR_NOME AS "SOLICITANTE",
                    SC.C1_OP AS "OP"
                FROM 
                    {self.database}.dbo.SC1010 SC
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
                    PROD.B1_COD = SC.C1_PRODUTO
                WHERE 
                    SC.C1_NUM LIKE '%{numero_sc}'
                    AND SC.C1_PEDIDO LIKE '%{numero_pedido}'
                    AND SC.C1_ZZNUMQP LIKE '%{numero_qp}'
                    AND SC.C1_PRODUTO LIKE '{codigo_produto}%'
                    AND SC.C1_DESCRI LIKE '{descricao_produto}%'
                    AND {clausulas_contem_descricao}
                    AND SC.C1_OP LIKE '%{numero_op}'
                    AND SC.C1_LOCAL LIKE '{cod_armazem}%'
                    AND SC.D_E_L_E_T_ <> '*' {filtro_data}
                    AND PROD.D_E_L_E_T_ <> '*'
                    ORDER BY "SOLIC. COMPRA" DESC;
            """
        return query_solic_compras

    def executar_consulta_solic_compras(self):
        query = self.query_solic_compras()
        query_contagem_linhas = self.numero_linhas_consulta(query)

        self.label_line_number.hide()
        self.controle_campos_formulario(False)
        self.button_visible_control(False)

        conn_str = f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}'
        self.engine = create_engine(f'mssql+pyodbc:///?odbc_connect={conn_str}')

        try:
            dataframe_line_number = pd.read_sql(query_contagem_linhas, self.engine)
            line_number = dataframe_line_number.iloc[0, 0]

            if line_number >= 1:
                if line_number > 1:
                    message = f"Foram encontradas {line_number} linhas"
                else:
                    message = f"Foi encontrada {line_number} linha"

                self.label_line_number.setText(f"{message}")
                self.label_line_number.show()

            else:
                exibir_mensagem("EUREKA® Compras", 'Nada encontrado!', "info")
                self.controle_campos_formulario(True)
                self.button_visible_control(False)
                return

            dataframe = pd.read_sql(query, self.engine)
            dataframe.insert(0, ' ', '')
            dataframe[''] = ''

            self.configurar_tabela(dataframe)
            self.configurar_tabela_tooltips(dataframe)

            self.tree.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
            self.tree.setRowCount(0)

            # Construir caminhos relativos
            script_dir = os.path.dirname(os.path.abspath(__file__))
            sc_open = os.path.join(script_dir, '..', 'resources', 'images', 'red.png')
            end_order_path = os.path.join(script_dir, '..', 'resources', 'images', 'green.png')

            sc_open = QIcon(sc_open)
            end_order = QIcon(end_order_path)

            for i, row in dataframe.iterrows():
                self.tree.setSortingEnabled(False)
                self.tree.insertRow(i)

                for column_name, value in row.items():
                    if value is not None:
                        if column_name == ' ':
                            item = QTableWidgetItem()
                            if row['PEDIDO DE COMPRA'] is not None:
                                if row['PEDIDO DE COMPRA'].strip() == '':
                                    item.setIcon(sc_open)
                                elif row['PEDIDO DE COMPRA'].strip() != '':
                                    item.setIcon(end_order)
                                item.setSizeHint(QSize(64, 64))
                        else:
                            if column_name == 'QTD. SOLIC. COMPRA' and pd.isna(value):
                                value = ''
                            elif column_name == 'QTD. SOLIC. COMPRA' and value:
                                value = round(value, 2)
                                value = locale.format_string("%.2f", value, grouping=True)

                            if column_name == 'C1_EMISSAO' and not value.isspace():
                                data_obj = datetime.strptime(value, "%Y%m%d")
                                value = data_obj.strftime("%d/%m/%Y")

                            item = QTableWidgetItem(str(value).strip())

                            if column_name not in ('DESCRIÇÃO', 'OBSERVAÇÃO SOLIC. COMPRA'):
                                item.setTextAlignment(Qt.AlignCenter)
                    else:
                        item = QTableWidgetItem('')

                    self.tree.setItem(i, list(row.index).index(column_name), item)

            self.tree.setSortingEnabled(True)
            self.controle_campos_formulario(True)
            self.button_visible_control(True)

        except Exception as ex:
            exibir_mensagem('Erro ao consultar TOTVS', f'Erro: {str(ex)}', 'error')

        finally:
            # Fecha a conexão com o banco de dados se estiver aberta
            if hasattr(self, 'engine'):
                self.engine.dispose()
                self.engine = None

    def configurar_tabela_tooltips(self, dataframe):
        # Mapa de tooltips correspondentes às colunas da consulta SQL
        tooltip_map = {
            " ": "VERMELHO: SC sem Pedido de Compra\nVERDE: Pedido de compra encerrado"
        }

        # Obtenha os cabeçalhos das colunas do dataframe
        headers = dataframe.columns

        # Adicione os cabeçalhos e os tooltips
        for i, header in enumerate(headers):
            item = QTableWidgetItem(header)
            tooltip = tooltip_map.get(header)
            item.setToolTip(tooltip)
            self.tree.setHorizontalHeaderItem(i, item)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SolicitacaoComprasWindow()
    username, password, database, server = setup_mssql()
    driver = '{SQL Server}'
    window.showMaximized()
    sys.exit(app.exec_())
