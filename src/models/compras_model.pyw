import locale
import sys
import pyodbc
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QStyle, QAction, QDateEdit, QLabel, \
    QComboBox, QSizePolicy, QTabWidget, QMenu, QCheckBox
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QDate, QProcess, pyqtSignal, QSize
import pyperclip
import pandas as pd
import ctypes
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from sqlalchemy import create_engine
import os


def exibir_mensagem(title, message, icon_type):
    root = tk.Tk()
    root.withdraw()
    root.lift()  # Garante que a janela esteja na frente
    root.title(title)
    root.attributes('-topmost', True)

    if icon_type == 'info':
        messagebox.showinfo(title, message)
    elif icon_type == 'warning':
        messagebox.showwarning(title, message)
    elif icon_type == 'error':
        messagebox.showerror(title, message)

    root.destroy()


def ajustar_largura_coluna_descricao(tree_widget):
    header = tree_widget.horizontalHeader()
    header.setSectionResizeMode(1, QHeaderView.ResizeToContents)


def add_today_button(date_edit):
    calendar = date_edit.calendarWidget()
    calendar.setGeometry(10, 10, 600, 400)
    btn_today = QPushButton("Hoje", calendar)
    largura, altura = 50, 20
    btn_today.setGeometry(20, 5, largura, altura)
    btn_today.clicked.connect(lambda: date_edit.setDate(QDate.currentDate()))


def copiar_linha(item):
    if item is not None:
        valor_campo = item.text()
        pyperclip.copy(str(valor_campo))


def setup_mssql():
    caminho_do_arquivo = (r"\\192.175.175.4\f\INTEGRANTES\ELIEZER\PROJETO SOLIDWORKS "
                          r"TOTVS\libs-python\user-password-mssql\USER_PASSWORD_MSSQL_PROD.txt")
    try:
        with open(caminho_do_arquivo, 'r') as arquivo:
            string_lida = arquivo.read()
            username_txt, password_txt, database_txt, server_txt = string_lida.split(';')
            return username_txt, password_txt, database_txt, server_txt

    except FileNotFoundError:
        ctypes.windll.user32.MessageBoxW(0,
                                         "Erro ao ler credenciais de acesso ao banco de dados MSSQL.\n\nBase de "
                                         "dados ERP TOTVS PROTHEUS.\n\nPor favor, informe ao desenvolvedor/TI "
                                         "sobre o erro exibido.\n\nTenha um bom dia! ツ",
                                         "CADASTRO DE ESTRUTURA - TOTVS®", 16 | 0)
        sys.exit()

    except Exception as ex:
        ctypes.windll.user32.MessageBoxW(0, f"Ocorreu um erro ao ler o arquivo: {ex}", "CADASTRO DE ESTRUTURA - TOTVS®",
                                         16 | 0)
        sys.exit()


def numero_linhas_consulta(query_consulta):
    order_by_sc_somente_com_pedido = f"""ORDER BY PC.R_E_C_N_O_ DESC;"""
    order_by_sc_sem_e_com_pedido = f"""ORDER BY "SC" DESC;"""

    query_sem_order_by = ""
    if order_by_sc_somente_com_pedido in query_consulta:
        query_sem_order_by = query_consulta.replace(order_by_sc_somente_com_pedido, "")
    elif order_by_sc_sem_e_com_pedido in query_consulta:
        query_sem_order_by = query_consulta.replace(order_by_sc_sem_e_com_pedido, "")

    query = f"""
        SELECT 
            COUNT(*) AS total_records
        FROM 
            ({query_sem_order_by}
            )
        AS combined_results;
    """
    return query


class ComprasApp(QWidget):
    guia_fechada = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("EUREKA® Compras - v2.0")
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

        self.interromper_consulta_sql = False
        self.tree = QTableWidget(self)
        self.tree.setColumnCount(0)
        self.tree.setRowCount(0)

        self.nova_janela = None
        self.process = QProcess(self)

        self.tabWidget = QTabWidget(self)  # Adicione um QTabWidget ao layout principal
        self.tabWidget.setTabsClosable(True)  # Adicione essa linha para permitir o fechamento de guias
        self.tabWidget.tabCloseRequested.connect(self.fechar_guia)
        self.tabWidget.setVisible(False)  # Inicialmente, a guia está invisível

        self.guias_abertas = []
        self.guias_abertas_onde_usado = []
        self.guias_abertas_saldo = []
        self.guias_abertas_ultimos_fornecedores = []

        self.label_line_number = QLabel("", self)
        self.label_line_number.setObjectName("label-line-number")
        self.label_line_number.setVisible(False)

        self.checkbox_exibir_somente_sc_com_pedido = QCheckBox("Ocultar Solicitação de Compras EM ABERTO", self)
        self.checkbox_exibir_somente_sc_com_pedido.setObjectName("checkbox-sc")

        self.label_sc = QLabel("Solic. Compra:", self)
        self.label_sc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_pedido = QLabel("Ped. de Compra:", self)
        self.label_pedido.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_codigo = QLabel("Código:", self)
        self.label_codigo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_descricao_prod = QLabel("Descrição:", self)
        self.label_descricao_prod.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_contem_descricao_prod = QLabel("Contém na descrição:", self)
        self.label_contem_descricao_prod.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.label_qp = QLabel("Número QP:", self)
        self.label_qp.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_OP = QLabel("Número OP:", self)
        self.label_OP.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_data_inicio = QLabel("Data inicial SC:", self)
        self.label_data_fim = QLabel("Data final SC:", self)
        self.label_armazem = QLabel("Armazém:", self)
        self.label_fornecedor = QLabel("Fornecedor Razão Social:", self)
        self.label_nm_fantasia_forn = QLabel("Fornecedor Nome Fantasia:", self)

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
        add_today_button(self.campo_data_inicio)

        self.campo_data_fim = QDateEdit(self)
        self.campo_data_fim.setFont(QFont(fonte_campos, 10))
        self.campo_data_fim.setFixedWidth(150)
        self.campo_data_fim.setCalendarPopup(True)
        self.campo_data_fim.setDisplayFormat("dd/MM/yyyy")
        self.campo_data_fim.setDate(QDate().currentDate())
        add_today_button(self.campo_data_fim)

        self.btn_consultar = QPushButton("Pesquisar", self)
        self.btn_consultar.clicked.connect(self.executar_consulta)
        self.btn_consultar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_abrir_engenharia = QPushButton("Engenharia", self)
        self.btn_abrir_engenharia.setObjectName("btn_engenharia")
        self.btn_abrir_engenharia.clicked.connect(self.abrir_modulo_engenharia)
        self.btn_abrir_engenharia.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_onde_e_usado = QPushButton("Onde é usado?", self)
        self.btn_onde_e_usado.clicked.connect(lambda: self.executar_consulta_onde_usado(self.tree))
        self.btn_onde_e_usado.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_onde_e_usado.setEnabled(False)

        self.btn_saldo_estoque = QPushButton("Saldos em Estoque", self)
        self.btn_saldo_estoque.clicked.connect(lambda: self.executar_saldo_em_estoque(self.tree))
        self.btn_saldo_estoque.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_saldo_estoque.setEnabled(False)

        self.btn_ultimos_fornecedores = QPushButton("Fornecedores", self)
        self.btn_ultimos_fornecedores.clicked.connect(lambda: self.executar_ultimos_fornecedores(self.tree))
        self.btn_ultimos_fornecedores.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_ultimos_fornecedores.setEnabled(False)

        self.btn_limpar = QPushButton("Limpar", self)
        self.btn_limpar.clicked.connect(self.limpar_campos)
        self.btn_limpar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_parar_consulta = QPushButton("Parar consulta")
        self.btn_parar_consulta.clicked.connect(self.parar_consulta)
        self.btn_parar_consulta.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_parar_consulta.setVisible(False)

        self.btn_nova_janela = QPushButton("Nova Janela", self)
        self.btn_nova_janela.clicked.connect(self.abrir_nova_janela)
        self.btn_nova_janela.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_exportar_excel = QPushButton("Exportar Excel", self)
        self.btn_exportar_excel.clicked.connect(self.exportar_excel)
        self.btn_exportar_excel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_exportar_excel.setEnabled(False)

        self.btn_fechar = QPushButton("Fechar", self)
        self.btn_fechar.clicked.connect(self.fechar_janela)
        self.btn_fechar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.campo_sc.returnPressed.connect(self.executar_consulta)
        self.campo_pedido.returnPressed.connect(self.executar_consulta)
        self.campo_codigo.returnPressed.connect(self.executar_consulta)
        self.campo_descricao_prod.returnPressed.connect(self.executar_consulta)
        self.campo_contem_descricao_prod.returnPressed.connect(self.executar_consulta)
        self.campo_qp.returnPressed.connect(self.executar_consulta)
        self.campo_OP.returnPressed.connect(self.executar_consulta)
        self.campo_razao_social_fornecedor.returnPressed.connect(self.executar_consulta)
        self.campo_nm_fantasia_fornecedor.returnPressed.connect(self.executar_consulta)

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

        layout_campos_01.addLayout(container_sc)
        layout_campos_01.addLayout(container_pedido)
        layout_campos_01.addLayout(container_op)
        layout_campos_01.addLayout(container_qp)
        layout_campos_01.addLayout(container_codigo)
        layout_campos_01.addLayout(container_descricao_prod)
        layout_campos_01.addLayout(container_contem_descricao_prod)
        layout_campos_02.addLayout(container_data_ini)
        layout_campos_02.addLayout(container_data_fim)
        layout_campos_02.addLayout(container_combobox_armazem)
        layout_campos_02.addLayout(container_fornecedor)
        layout_campos_02.addLayout(container_nm_fantasia_forn)
        layout_campos_02.addWidget(self.checkbox_exibir_somente_sc_com_pedido)
        layout_campos_01.addStretch()
        layout_campos_02.addStretch()

        self.layout_buttons.addWidget(self.btn_consultar)
        self.layout_buttons.addWidget(self.btn_parar_consulta)
        self.layout_buttons.addWidget(self.btn_ultimos_fornecedores)
        self.layout_buttons.addWidget(self.btn_saldo_estoque)
        self.layout_buttons.addWidget(self.btn_onde_e_usado)
        self.layout_buttons.addWidget(self.btn_nova_janela)
        self.layout_buttons.addWidget(self.btn_limpar)
        self.layout_buttons.addWidget(self.btn_exportar_excel)
        self.layout_buttons.addWidget(self.btn_abrir_engenharia)
        self.layout_buttons.addWidget(self.btn_fechar)
        self.layout_buttons.addStretch()

        self.layout_footer_label.addStretch(1)
        self.layout_footer_label.addWidget(self.label_line_number)
        self.layout_footer_label.addStretch(1)
        self.layout_footer_label.addWidget(self.logo_label)

        layout.addLayout(layout_campos_01)
        layout.addLayout(layout_campos_02)
        layout.addLayout(self.layout_buttons)
        layout.addWidget(self.tree)
        layout.addLayout(self.layout_footer_label)

        self.setLayout(layout)

        self.setStyleSheet("""
            * {
                background-color: #373A40;
            }
    
            QLabel, QCheckBox {
                color: #DFE0E2;
                font-size: 12px;
                font-weight: bold;
                padding-left: 10px; 
            }
            
            QCheckBox#checkbox-sc {
                margin-left: 10px;
                font-size: 16px;
                font-weight: normal;
            }
            
            QLabel#label-line-number {
                font-size: 16px;
                font-weight: normal;
            }
    
            QDateEdit, QComboBox {
                background-color: #EEEEEE;
                border: 1px solid #262626;
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
                border: 1px solid #262626;
                padding: 5px 10px;
                border-radius: 10px;
                font-size: 16px;
            }
            
            QLineEdit#forn-raz, QLineEdit#forn-fantasia {
                padding: 5px 10px;
                border-radius: 10px;
                font-size: 16px;
                margin-bottom:  20px;
            }
    
            QPushButton {
                background-color: #AF125A;
                color: #eeeeee;
                padding: 7px 10px;
                border: 2px solid #AF125A;
                border-radius: 8px;
                font-size: 12px;
                height: 20px;
                font-weight: bold;
                margin: 10px 5px 5px 5px;
            }
            
            QPushButton#btn_engenharia {
                border: 2px solid #0a79f8;
                background-color: #0a79f8;
            }
    
            QPushButton:hover, QPushButton:hover#btn_engenharia {
                background-color: #EFF2F1;
                color: #3A0CA3
            }
    
            QPushButton:pressed, QPushButton:pressed#btn_engenharia {
                background-color: #6703c5;
                color: #fff;
            }
    
            QTableWidget {
                border: 1px solid #000000;
                background-color: #686D76;
                padding-left: 10px;
                margin: 5px 15px 0px 0px;
            }
    
            QTableWidget QHeaderView::section {
                background-color: #262626;
                color: #A7A6A6;
                padding: 5px;
                height: 18px;
            }
    
            QTableWidget QHeaderView::section:horizontal {
                border-top: 1px solid #333;
            }
    
            QTableWidget::item {
                background-color: #363636;
                color: #EEEEEE;
                font-weight: bold;
                padding-right: 8px;
                padding-left: 8px;
            }
    
            QTableWidget::item:selected {
                background-color: #000000;
                color: #EEEEEE;
                font-weight: bold;
            }
        """)

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
                        self.guias_abertas_ultimos_fornecedores.remove(codigo_guia_fechada)

            finally:
                self.tabWidget.removeTab(index)

                if not self.existe_guias_abertas():
                    # Se não houver mais guias abertas, remova a guia do layout principal
                    self.tabWidget.setVisible(False)
                    self.guia_fechada.emit()

    def existe_guias_abertas(self):
        return self.tabWidget.count() > 0

    def showContextMenu(self, position, table):
        indexes = table.selectedIndexes()
        if indexes:
            # Obtém o índice do item clicado
            index = table.indexAt(position)
            if not index.isValid():
                return

            # Seleciona a linha inteira
            table.selectRow(index.row())

            menu = QMenu()

            context_menu_ultimo_fornecedor = QAction('Fornecedores', self)
            context_menu_ultimo_fornecedor.triggered.connect(lambda: self.executar_ultimos_fornecedores(table))

            context_menu_consultar_onde_usado = QAction('Onde é usado?', self)
            context_menu_consultar_onde_usado.triggered.connect(lambda: self.executar_consulta_onde_usado(table))

            context_menu_saldo_estoque = QAction('Saldo em estoque', self)
            context_menu_saldo_estoque.triggered.connect(lambda: self.executar_saldo_em_estoque(table))

            context_menu_nova_janela = QAction('Nova janela', self)
            context_menu_nova_janela.triggered.connect(lambda: self.abrir_nova_janela())

            menu.addAction(context_menu_ultimo_fornecedor)
            menu.addAction(context_menu_consultar_onde_usado)
            menu.addAction(context_menu_saldo_estoque)
            menu.addAction(context_menu_nova_janela)

            menu.exec_(table.viewport().mapToGlobal(position))

    def abrir_nova_janela(self):
        if not self.nova_janela or not self.nova_janela.isVisible():
            self.nova_janela = ComprasApp()
            self.nova_janela.setGeometry(self.x() + 50, self.y() + 50, self.width(), self.height())
            self.nova_janela.show()

    def add_clear_button(self, line_edit):
        clear_icon = self.style().standardIcon(QStyle.SP_LineEditClearButton)

        line_edit_height = line_edit.height()
        pixmap = clear_icon.pixmap(line_edit_height - 4, line_edit_height - 4)
        larger_clear_icon = QIcon(pixmap)

        clear_action = QAction(larger_clear_icon, "Limpar", line_edit)
        clear_action.triggered.connect(line_edit.clear)
        line_edit.addAction(clear_action, QLineEdit.TrailingPosition)

    def exportar_excel(self):
        desktop_path = os.path.join(os.path.expanduser("~"), 'Desktop')

        now = datetime.now()
        default_filename = f'COMPRAS-report_{now.today().strftime('%Y-%m-%d_%H%M%S')}.xlsx'

        file_path, _ = QFileDialog.getSaveFileName(self, 'Salvar como', os.path.join(desktop_path, default_filename),
                                                   'Arquivos Excel (*.xlsx);;Todos os arquivos (*)')

        if file_path:
            data = self.obter_dados_tabela()
            column_headers = [self.tree.horizontalHeaderItem(i).text() for i in range(self.tree.columnCount())]
            df = pd.DataFrame(data, columns=column_headers)

            writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Dados', index=False)

            workbook = writer.book
            worksheet = writer.sheets['Dados']

            for i, col in enumerate(df.columns):
                max_len = df[col].astype(str).map(len).max()
                worksheet.set_column(i, i, max_len + 2)

            writer.close()

            os.startfile(file_path)

    def obter_dados_tabela(self):
        # Obter os dados da tabela
        data = []
        for i in range(self.tree.rowCount()):
            row_data = []
            for j in range(self.tree.columnCount()):
                item = self.tree.item(i, j)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append("")
            data.append(row_data)
        return data

    def configurar_tabela(self, dataframe):
        self.tree.setColumnCount(len(dataframe.columns))
        self.tree.setHorizontalHeaderLabels(dataframe.columns)
        self.tree.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tree.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tree.setSelectionBehavior(QTableWidget.SelectRows)
        self.tree.setSelectionMode(QTableWidget.SingleSelection)
        self.tree.itemDoubleClicked.connect(copiar_linha)
        self.tree.setFont(QFont(self.fonte_tabela, self.tamanho_fonte_tabela))
        self.tree.verticalHeader().setDefaultSectionSize(self.altura_linha)
        self.tree.horizontalHeader().sectionClicked.connect(self.ordenar_tabela)
        self.tree.horizontalHeader().setStretchLastSection(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(lambda pos: self.showContextMenu(pos, self.tree))

    def ordenar_tabela(self, logical_index):
        # Obter o índice real da coluna (considerando a ordem de classificação)
        index = self.tree.horizontalHeader().sortIndicatorOrder()

        # Definir a ordem de classificação
        order = Qt.AscendingOrder if index == 0 else Qt.DescendingOrder

        # Ordenar a tabela pela coluna clicada
        self.tree.sortItems(logical_index, order)

    def limpar_campos(self):
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
        self.btn_consultar.setEnabled(status)
        self.btn_exportar_excel.setEnabled(status)
        self.btn_saldo_estoque.setEnabled(status)
        self.btn_onde_e_usado.setEnabled(status)
        self.btn_ultimos_fornecedores.setEnabled(status)

    def query_consulta_followup(self):

        numero_sc = self.campo_sc.text().upper().strip()
        numero_pedido = self.campo_pedido.text().upper().strip()
        numero_qp = self.campo_qp.text().upper().strip()
        numero_op = self.campo_OP.text().upper().strip()
        codigo_produto = self.campo_codigo.text().upper().strip()
        razao_social_fornecedor = self.campo_razao_social_fornecedor.text().upper().strip()
        nome_fantasia_fornecedor = self.campo_nm_fantasia_fornecedor.text().upper().strip()
        descricao_produto = self.campo_descricao_prod.text().upper().strip()
        contem_descricao = self.campo_contem_descricao_prod.text().upper().strip()
        checkbox_sc_somente_com_pedido = self.checkbox_exibir_somente_sc_com_pedido.isChecked()

        if numero_pedido.strip() != '':
            numero_pedido_tabela_solic = numero_pedido
        else:
            numero_pedido_tabela_solic = '      '

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

        common_select = f"""
                SELECT
                    SC.C1_ZZNUMQP AS "QP",
                    SC.C1_NUM AS "SC",
                    SC.C1_ITEM AS "Item SC",
                    SC.C1_QUANT AS "Qtd. SC",
                    SC.C1_PEDIDO AS "Ped. Compra",
                    SC.C1_ITEMPED AS "Item Ped.",
                    PC.C7_QUANT AS "Qtd. Ped.",
                    PC.C7_PRECO AS "Preço Unit. (R$)",
                    PC.C7_TOTAL AS "Sub-total (R$)",
                    PC.C7_DATPRF AS "Previsão Entrega",
                    ITEM_NF.D1_DOC AS "Nota Fiscal Ent.",
                    ITEM_NF.D1_QUANT AS "Qtd. Entregue",
                    CASE 
                        WHEN ITEM_NF.D1_QUANT IS NULL THEN SC.C1_QUJE 
                        ELSE SC.C1_QUJE - ITEM_NF.D1_QUANT
                    END AS "Qtd. Pendente",
                    ITEM_NF.D1_DTDIGIT AS "Data Entrega",
                    PC.C7_ENCER AS "Status Ped. Compra",
                    SC.C1_PRODUTO AS "Código",
                    SC.C1_DESCRI AS "Descrição",
                    SC.C1_UM AS "UM",
                    PROD.B1_ZZLOCAL AS "Endereço:",
                    SC.C1_EMISSAO AS "Emissão SC",
                    PC.C7_EMISSAO AS "Emissão PC",
                    ITEM_NF.D1_EMISSAO AS "Emissão NF",
                    SC.C1_ORIGEM AS "Origem",
                    SC.C1_OBS AS "Observação",
                    SC.C1_LOCAL AS "Cod. Armazém",
                    ARM.NNR_DESCRI AS "Desc. Armazém",
                    SC.C1_IMPORT AS "Importado?",
                    PC.C7_OBS AS "Observações",
                    PC.C7_OBSM AS "Observações item",
                    FORN.A2_COD AS "Cód. Forn.",
                    FORN.A2_NOME AS "Raz. Soc. Forn.",
                    FORN.A2_NREDUZ AS "Nom. Fantasia Forn.",
                    US.USR_NOME AS "Solicitante",
                    PC.S_T_A_M_P_ AS "Aberto em:",
                    SC.C1_OP AS "OP"
                FROM 
                    {database}.dbo.SC7010 PC
                LEFT JOIN
                    {database}.dbo.SD1010 ITEM_NF
                ON 
                    PC.C7_NUM = ITEM_NF.D1_PEDIDO AND PC.C7_ITEM = ITEM_NF.D1_ITEMPC
                LEFT JOIN
                    {database}.dbo.SC1010 SC
                ON 
                    SC.C1_PEDIDO = PC.C7_NUM AND SC.C1_ITEMPED = PC.C7_ITEM
                LEFT JOIN
                    {database}.dbo.SA2010 FORN
                ON
                    FORN.A2_COD = PC.C7_FORNECE 
                LEFT JOIN
                    {database}.dbo.NNR010 ARM
                ON
                    SC.C1_LOCAL = ARM.NNR_CODIGO
                LEFT JOIN 
                    {database}.dbo.SYS_USR US
                ON
                    SC.C1_SOLICIT = US.USR_CODIGO AND US.D_E_L_E_T_ <> '*'
                INNER JOIN 
                    {database}.dbo.SB1010 PROD
                ON 
                    PROD.B1_COD = SC.C1_PRODUTO
            """

        solic_com_pedido_where = f"""
                WHERE
                    PC.C7_NUM LIKE '%{numero_pedido}'
                    AND PC.C7_NUMSC LIKE '%{numero_sc}'
                    AND PC.C7_ZZNUMQP LIKE '%{numero_qp}'
                    AND PC.C7_PRODUTO LIKE '{codigo_produto}%'
                    AND SC.C1_DESCRI LIKE '{descricao_produto}%'
                    AND {clausulas_contem_descricao}
                    AND SC.C1_OP LIKE '%{numero_op}' 
                    AND FORN.A2_NOME LIKE '%{razao_social_fornecedor}'
                    AND FORN.A2_NREDUZ LIKE '%{nome_fantasia_fornecedor}%'
                    AND SC.C1_LOCAL LIKE '{cod_armazem}%' {filtro_data}
                    AND PC.D_E_L_E_T_ <> '*'
                    AND SC.D_E_L_E_T_ <> '*'
                    AND PROD.D_E_L_E_T_ <> '*' ORDER BY PC.R_E_C_N_O_ DESC;
            """

        solic_sem_pedido_where = f"""
                WHERE
                    PC.C7_NUM LIKE '%{numero_pedido}'
                    AND PC.C7_NUMSC LIKE '%{numero_sc}'
                    AND PC.C7_ZZNUMQP LIKE '%{numero_qp}'
                    AND PC.C7_PRODUTO LIKE '{codigo_produto}%'
                    AND SC.C1_DESCRI LIKE '{descricao_produto}%'
                    AND {clausulas_contem_descricao}
                    AND SC.C1_OP LIKE '%{numero_op}' 
                    AND FORN.A2_NOME LIKE '%{razao_social_fornecedor}'
                    AND FORN.A2_NREDUZ LIKE '%{nome_fantasia_fornecedor}%'
                    AND SC.C1_LOCAL LIKE '{cod_armazem}%' {filtro_data}
                    AND PC.D_E_L_E_T_ <> '*'
                    AND SC.D_E_L_E_T_ <> '*'
                    AND PROD.D_E_L_E_T_ <> '*' 

                UNION ALL

                SELECT 
                    SC.C1_ZZNUMQP AS "QP",
                    SC.C1_NUM AS "SC",
                    SC.C1_ITEM AS "Item SC",
                    SC.C1_QUANT AS "Qtd. SC",
                    NULL AS "Ped. Compra",
                    NULL AS "Item Ped.",
                    NULL AS "Qtd. Ped.",
                    NULL AS "Preço Unit. (R$)",
                    NULL AS "Sub-total (R$)",
                    NULL AS "Previsão Entrega",
                    NULL AS "Nota Fiscal Ent.",
                    NULL AS "Qtd. Entregue",
                    NULL AS "Qtd. Pendente",
                    NULL AS "Data Entrega",
                    NULL AS "Status Ped. Compra",
                    SC.C1_PRODUTO AS "Código",
                    SC.C1_DESCRI AS "Descrição",
                    SC.C1_UM AS "UM",
                    PROD.B1_ZZLOCAL AS "Endereço:",
                    SC.C1_EMISSAO AS "Emissão SC",
                    NULL AS "Emissão PC",
                    NULL AS "Emissão NF",
                    SC.C1_ORIGEM AS "Origem",
                    SC.C1_OBS AS "Observação",
                    SC.C1_LOCAL AS "Cod. Armazém",
                    ARM.NNR_DESCRI AS "Desc. Armazém",
                    SC.C1_IMPORT AS "Importado?",
                    NULL AS "Observações",
                    NULL AS "Observações item",
                    NULL AS "Cód. Forn.",
                    NULL AS "Raz. Soc. Forn.",
                    NULL AS "Nom. Fantasia Forn.",
                    US.USR_NOME AS "Solicitante",
                    NULL AS "Aberto em:",
                    SC.C1_OP AS "OP"
                FROM 
                    {database}.dbo.SC1010 SC
                LEFT JOIN
                    {database}.dbo.NNR010 ARM
                ON 
                    SC.C1_LOCAL = ARM.NNR_CODIGO
                LEFT JOIN 
                    {database}.dbo.SYS_USR US
                ON 
                    SC.C1_SOLICIT = US.USR_CODIGO AND US.D_E_L_E_T_ <> '*'
                INNER JOIN 
                    {database}.dbo.SB1010 PROD
                ON 
                    PROD.B1_COD = SC.C1_PRODUTO
                WHERE 
                    SC.C1_PEDIDO LIKE '%{numero_pedido_tabela_solic}'
                    AND SC.C1_NUM LIKE '%{numero_sc}'
                    AND SC.C1_ZZNUMQP LIKE '%{numero_qp}'
                    AND SC.C1_PRODUTO LIKE '{codigo_produto}%'
                    AND SC.C1_DESCRI LIKE '{descricao_produto}%'
                    AND {clausulas_contem_descricao}
                    AND SC.C1_OP LIKE '%{numero_op}'
                    AND SC.C1_LOCAL LIKE '{cod_armazem}%'
                    AND SC.D_E_L_E_T_ <> '*' {filtro_data}
                    AND PROD.D_E_L_E_T_ <> '*'
                    AND SC.C1_COTACAO <> 'XXXXXX' ORDER BY "SC" DESC;
            """

        if checkbox_sc_somente_com_pedido:
            return common_select + solic_com_pedido_where
        else:
            return common_select + solic_sem_pedido_where

    def executar_consulta(self):
        query_consulta_filtro = self.query_consulta_followup()
        query_contagem_linhas = numero_linhas_consulta(query_consulta_filtro)

        self.label_line_number.hide()
        self.controle_campos_formulario(False)

        conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
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

                data_atual = datetime.now()
            else:
                exibir_mensagem("EUREKA® Compras", 'Nada encontrado!', "info")
                self.controle_campos_formulario(True)
                return

            dataframe = pd.read_sql(query_consulta_filtro, self.engine)
            dataframe.insert(0, 'Status PC', '')
            dataframe[''] = ''
            dataframe.insert(11, 'Dias em atraso', '')

            self.configurar_tabela(dataframe)
            self.configurar_tabela_tooltips(dataframe)

            self.tree.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
            self.tree.setRowCount(0)

            # Construir caminhos relativos
            script_dir = os.path.dirname(os.path.abspath(__file__))
            no_pc = os.path.join(script_dir, '..', 'resources', 'images', 'red.png')
            no_order_path = os.path.join(script_dir, '..', 'resources', 'images', 'gray.png')
            wait_order_path = os.path.join(script_dir, '..', 'resources', 'images', 'wait.png')
            end_order_path = os.path.join(script_dir, '..', 'resources', 'images', 'green.png')

            no_pc = QIcon(no_pc)
            no_order = QIcon(no_order_path)
            wait_delivery = QIcon(wait_order_path)
            end_order = QIcon(end_order_path)

            for i, row in dataframe.iterrows():
                if self.interromper_consulta_sql:
                    break

                self.tree.setSortingEnabled(False)
                self.tree.insertRow(i)

                for j, value in enumerate(row):
                    if value is not None:
                        if j == 0:
                            item = QTableWidgetItem()
                            if row['Status Ped. Compra'] is not None:
                                if row['Status Ped. Compra'].strip() == '' and row['Nota Fiscal Ent.'] is None:
                                    item.setIcon(no_order)
                                elif row['Status Ped. Compra'].strip() == '' and row['Nota Fiscal Ent.'] is not None:
                                    item.setIcon(wait_delivery)
                                elif row['Status Ped. Compra'] == 'E':
                                    item.setIcon(end_order)
                                item.setSizeHint(QSize(64, 64))
                            elif row['Ped. Compra'] is None:
                                item.setIcon(no_pc)
                        else:
                            if j in (4, 7, 8, 9, 13):
                                value = locale.format_string("%.2f", value, grouping=True)

                            if j in (7, 8, 9, 13) and value == 'nan':
                                value = '-'
                            if j == 35 and pd.isna(value):
                                value = '-'

                            if j == 11 and row['Nota Fiscal Ent.'] is None:
                                previsao_entrega_sem_formatacao = row['Previsão Entrega']
                                if pd.notna(previsao_entrega_sem_formatacao):
                                    previsao_entrega_obj = datetime.strptime(previsao_entrega_sem_formatacao, "%Y%m%d")
                                    previsao_entrega_formatada = previsao_entrega_obj.strftime("%d/%m/%Y")
                                    previsao_entrega = pd.to_datetime(previsao_entrega_formatada, dayfirst=True)
                                    value = (data_atual - previsao_entrega).days
                            elif j == 11 and row['Nota Fiscal Ent.'] is not None:
                                value = '-'
                            if j == 14 and pd.isna(value):  # COLUNA QTD. ENTREGUE
                                value = '-'
                            elif j == 14 and value:  # COLUNA QTD. PENDENTE
                                value = round(value, 2)

                            if j == 16 and value == 'E':
                                value = 'Encerrado'
                            elif j == 16 and value.strip() == '':
                                value = '-'

                            if j == 24 and value.strip() == 'MATA650':  # Indica na coluna 'Origem' se o item foi
                                # empenhado ou será comprado
                                value = 'Empenho'
                            elif j == 24 and value.strip() == '':
                                value = 'Compras'

                            if j == 28 and value.strip() == 'N':  # Escreve sim ou não na coluna 'Importado?'
                                value = 'Não'
                            elif j == 28 and value.strip() == '':
                                value = 'Sim'

                            if j in (10, 15, 21, 22, 23) and not value.isspace():  # Formatação das datas no formato
                                # dd/mm/YYYY
                                data_obj = datetime.strptime(value, "%Y%m%d")
                                value = data_obj.strftime("%d/%m/%Y")

                            item = QTableWidgetItem(str(value).strip())

                            if j not in (18, 25, 29, 30, 32, 33):  # Alinhamento a esquerda de colunas
                                item.setTextAlignment(Qt.AlignCenter)
                    else:
                        item = QTableWidgetItem('')

                    self.tree.setItem(i, j, item)

                # QCoreApplication.processEvents()

            self.tree.setSortingEnabled(True)
            self.controle_campos_formulario(True)

        except Exception as ex:
            exibir_mensagem('Erro ao consultar TOTVS', f'Erro: {str(ex)}', 'error')

        finally:
            # Fecha a conexão com o banco de dados se estiver aberta
            if hasattr(self, 'engine'):
                self.engine.dispose()
                self.engine = None
            self.interromper_consulta_sql = False

    def configurar_tabela_tooltips(self, dataframe):
        # Mapa de tooltips correspondentes às colunas da consulta SQL
        tooltip_map = {
            "Status PC": "VERMELHO - SC sem Pedido de Compra\nCINZA - Aguardando entrega\nAZUL - Entrega "
                         "parcial\nVERDE - Pedido de compra encerrado"
        }

        # Obtenha os cabeçalhos das colunas do dataframe
        headers = dataframe.columns

        # Adicione os cabeçalhos e os tooltips
        for i, header in enumerate(headers):
            item = QTableWidgetItem(header)
            tooltip = tooltip_map.get(header)
            item.setToolTip(tooltip)
            self.tree.setHorizontalHeaderItem(i, item)

    def fechar_janela(self):
        self.close()

    def parar_consulta(self):
        self.interromper_consulta_sql = True
        if hasattr(self, 'engine') and self.engine is not None:
            self.engine.dispose()
        self.controle_campos_formulario(True)

    def abrir_modulo_engenharia(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, 'engenharia_model.pyw')
        self.process.start("python", [script_path])

    def executar_consulta_onde_usado(self, table):
        item_selecionado = table.currentItem()
        codigo, descricao = None, None

        if item_selecionado:
            header = table.horizontalHeader()
            codigo_col = None
            descricao_col = None

            for col in range(header.count()):
                header_text = table.horizontalHeaderItem(col).text()
                if header_text == 'Código':
                    codigo_col = col
                elif header_text == 'Descrição':
                    descricao_col = col

            if codigo_col is not None and descricao_col is not None:
                codigo = table.item(item_selecionado.row(), codigo_col).text()
                descricao = table.item(item_selecionado.row(), descricao_col).text()

            if codigo not in self.guias_abertas_onde_usado and codigo is not None:
                query_onde_usado = f"""
                    SELECT 
                        STRUT.G1_COD AS "Código", 
                        PROD.B1_DESC "Descrição"
                    FROM 
                        {database}.dbo.SG1010 STRUT 
                    INNER JOIN 
                        {database}.dbo.SB1010 PROD 
                    ON 
                        G1_COD = B1_COD 
                    WHERE G1_COMP = '{codigo}' 
                        AND STRUT.G1_REVFIM <> 'ZZZ' 
                        AND STRUT.D_E_L_E_T_ <> '*'
                    ORDER BY B1_DESC ASC;
                """
                self.guias_abertas_onde_usado.append(codigo)
                try:
                    conn = pyodbc.connect(
                        f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')

                    cursor_tabela = conn.cursor()
                    cursor_tabela.execute(query_onde_usado)

                    nova_guia_estrutura = QWidget()
                    layout_nova_guia_estrutura = QVBoxLayout()
                    layout_cabecalho = QHBoxLayout()

                    tabela_onde_usado = QTableWidget(nova_guia_estrutura)

                    tabela_onde_usado.setContextMenuPolicy(Qt.CustomContextMenu)
                    tabela_onde_usado.customContextMenuRequested.connect(
                        lambda pos: self.showContextMenu(pos, tabela_onde_usado))

                    tabela_onde_usado.setColumnCount(len(cursor_tabela.description))
                    tabela_onde_usado.setHorizontalHeaderLabels([desc[0] for desc in cursor_tabela.description])

                    # Tornar a tabela somente leitura
                    tabela_onde_usado.setEditTriggers(QTableWidget.NoEditTriggers)

                    # Configurar a fonte da tabela
                    fonte_tabela = QFont("Segoe UI", 8)  # Substitua por sua fonte desejada e tamanho
                    tabela_onde_usado.setFont(fonte_tabela)

                    # Ajustar a altura das linhas
                    altura_linha = 22  # Substitua pelo valor desejado
                    tabela_onde_usado.verticalHeader().setDefaultSectionSize(altura_linha)

                    for i, row in enumerate(cursor_tabela.fetchall()):
                        tabela_onde_usado.insertRow(i)
                        for j, value in enumerate(row):
                            valor_formatado = str(value).strip()

                            item = QTableWidgetItem(valor_formatado)
                            tabela_onde_usado.setItem(i, j, item)

                    tabela_onde_usado.setSortingEnabled(True)

                    # Ajustar automaticamente a largura da coluna "Descrição"
                    ajustar_largura_coluna_descricao(tabela_onde_usado)

                    layout_cabecalho.addWidget(QLabel(f'Onde é usado?\n\n{codigo} - {descricao}'),
                                               alignment=Qt.AlignLeft)
                    layout_nova_guia_estrutura.addLayout(layout_cabecalho)
                    layout_nova_guia_estrutura.addWidget(tabela_onde_usado)
                    nova_guia_estrutura.setLayout(layout_nova_guia_estrutura)

                    nova_guia_estrutura.setStyleSheet("""                                           
                        * {
                            background-color: #262626;
                        }

                        QLabel {
                            color: #A7A6A6;
                            font-size: 18px;
                            font-weight: bold;
                        }

                        QTableWidget {
                            border: 1px solid #000000;
                        }

                        QTableWidget QHeaderView::section {
                            background-color: #575a5f;
                            color: #fff;
                            padding: 5px;
                            height: 18px;
                        }

                        QTableWidget QHeaderView::section:horizontal {
                            border-top: 1px solid #333;
                        }

                        QTableWidget::item:selected {
                            background-color: #0066ff;
                            color: #fff;
                            font-weight: bold;
                        }        
                    """)

                    if not self.existe_guias_abertas():
                        # Se não houver guias abertas, adicione a guia ao layout principal
                        self.layout().addWidget(self.tabWidget)
                        self.tabWidget.setVisible(True)

                    self.tabWidget.addTab(nova_guia_estrutura, f"Onde é usado? - {codigo}")
                    tabela_onde_usado.itemDoubleClicked.connect(copiar_linha)

                except pyodbc.Error as ex:
                    print(f"Falha na consulta de estrutura. Erro: {str(ex)}")

                finally:
                    self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(nova_guia_estrutura))
                    conn.close()

    def executar_saldo_em_estoque(self, table):
        item_selecionado = table.currentItem()
        codigo, descricao = None, None

        if item_selecionado:
            header = table.horizontalHeader()
            codigo_col = None
            descricao_col = None

            for col in range(header.count()):
                header_text = table.horizontalHeaderItem(col).text()
                if header_text == 'Código':
                    codigo_col = col
                elif header_text == 'Descrição':
                    descricao_col = col

            if codigo_col is not None and descricao_col is not None:
                codigo = table.item(item_selecionado.row(), codigo_col).text()
                descricao = table.item(item_selecionado.row(), descricao_col).text()

            if codigo not in self.guias_abertas_saldo and codigo is not None:
                query_saldo = f"""
                    SELECT 
                        B2_QATU AS "Saldo Atual",
                        EST.B2_QATU - EST.B2_QEMP AS "Qtd. Disponível",
                        B2_QEMP AS "Qtd. Empenhada",
                        B2_SALPEDI AS "Qtd. Prev. Entrada",
                        PROD.B1_UM AS "Unid. Med.",
                        B2_VATU1 AS "Valor Saldo Atual (R$)", 
                        B2_CM1 AS "Custo Unit. (R$)",
                        B2_DMOV AS "Dt. Últ. Mov.", 
                        B2_HMOV AS "Hora Últ. Mov.",
                        B2_DINVENT AS "Dt. Últ. Inventário"
                    FROM 
                        {database}.dbo.SB2010 EST
                    INNER JOIN
                        {database}.dbo.SB1010 PROD
                    ON
                        PROD.B1_COD = EST.B2_COD 
                    WHERE 
                        B2_COD = '{codigo}';
                """
                self.guias_abertas_saldo.append(codigo)
                try:
                    conn_saldo = pyodbc.connect(
                        f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')

                    cursor_saldo_estoque = conn_saldo.cursor()
                    cursor_saldo_estoque.execute(query_saldo)

                    nova_guia_saldo = QWidget()
                    layout_nova_guia_saldo = QVBoxLayout()
                    layout_cabecalho = QHBoxLayout()

                    tabela_saldo_estoque = QTableWidget(nova_guia_saldo)

                    tabela_saldo_estoque.setColumnCount(len(cursor_saldo_estoque.description))
                    tabela_saldo_estoque.setHorizontalHeaderLabels(
                        [desc[0] for desc in cursor_saldo_estoque.description])

                    tabela_saldo_estoque.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

                    # Tornar a tabela somente leitura
                    tabela_saldo_estoque.setEditTriggers(QTableWidget.NoEditTriggers)

                    # Configurar a fonte da tabela1
                    fonte_tabela = QFont("Segoe UI", 10)  # Substitua por sua fonte desejada e tamanho
                    tabela_saldo_estoque.setFont(fonte_tabela)

                    # Ajustar a altura das linhas
                    altura_linha = 20  # Substitua pelo valor desejado
                    tabela_saldo_estoque.verticalHeader().setDefaultSectionSize(altura_linha)

                    for i, row in enumerate(cursor_saldo_estoque.fetchall()):
                        tabela_saldo_estoque.insertRow(i)
                        for j, value in enumerate(row):

                            if j in (0, 1, 2, 3, 5, 6):
                                value = locale.format_string("%.2f", value, grouping=True)

                            elif j in (7, 9) and not value.isspace():
                                data_obj = datetime.strptime(value, "%Y%m%d")
                                value = data_obj.strftime("%d/%m/%Y")

                            valor_formatado = str(value).strip()
                            item = QTableWidgetItem(valor_formatado)
                            item.setTextAlignment(Qt.AlignCenter)
                            tabela_saldo_estoque.setItem(i, j, item)

                    tabela_saldo_estoque.setSortingEnabled(True)

                    layout_cabecalho.addWidget(QLabel(f'Saldos em Estoque\n\n{codigo} - {descricao}'),
                                               alignment=Qt.AlignLeft)
                    layout_nova_guia_saldo.addLayout(layout_cabecalho)
                    layout_nova_guia_saldo.addWidget(tabela_saldo_estoque)
                    nova_guia_saldo.setLayout(layout_nova_guia_saldo)

                    nova_guia_saldo.setStyleSheet("""                                           
                        * {
                            background-color: #262626;
                        }

                        QLabel {
                            color: #A7A6A6;
                            font-size: 18px;
                            font-weight: bold;
                        }

                        QTableWidget {
                            border: 1px solid #000000;
                        }

                        QTableWidget QHeaderView::section {
                            background-color: #575a5f;
                            color: #fff;
                            padding: 5px;
                            height: 18px;
                        }

                        QTableWidget QHeaderView::section:horizontal {
                            border-top: 1px solid #333;
                        }

                        QTableWidget::item:selected {
                            background-color: #0066ff;
                            color: #fff;
                            font-weight: bold;
                        }        
                    """)

                    if not self.existe_guias_abertas():
                        # Se não houver guias abertas, adicione a guia ao layout principal
                        self.layout().addWidget(self.tabWidget)
                        self.tabWidget.setVisible(True)

                    self.tabWidget.addTab(nova_guia_saldo, f"Saldos em Estoque - {codigo}")
                    tabela_saldo_estoque.itemDoubleClicked.connect(copiar_linha)

                except pyodbc.Error as ex:
                    print(f"Falha na consulta de estrutura. Erro: {str(ex)}")

                finally:
                    self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(nova_guia_saldo))
                    conn_saldo.close()

    def executar_ultimos_fornecedores(self, table):
        item_selecionado = table.currentItem()
        codigo, descricao = None, None

        if item_selecionado:
            header = table.horizontalHeader()
            codigo_col = None
            descricao_col = None

            for col in range(header.count()):
                header_text = table.horizontalHeaderItem(col).text()
                if header_text == 'Código':
                    codigo_col = col
                elif header_text == 'Descrição':
                    descricao_col = col

            if codigo_col is not None and descricao_col is not None:
                codigo = table.item(item_selecionado.row(), codigo_col).text()
                descricao = table.item(item_selecionado.row(), descricao_col).text()

            if codigo not in self.guias_abertas_ultimos_fornecedores and codigo is not None:
                query = f"""
                    SELECT 
                        A5_FORNECE AS "Cód. Forn.", 
                        A5_NOMEFOR AS "Razão Social",
                        FORN.A2_NREDUZ AS "Nome Fantasia",
                        A5_QUANT01 AS "Qtd. 1ª compra",
                        A5_QUANT02 AS "Qtd. 2ª compra",
                        A5_QUANT03 AS "Qtd. 3ª compra",
                        A5_PRECO01 AS "Preço 1ª compra",
                        A5_PRECO02 AS "Preço 2ª compra",
                        A5_PRECO03 AS "Preço 3ª compra",
                        A5_DTCOM01 AS "Data 1ª compra",
                        A5_DTCOM02 AS "Data 2ª compra",
                        A5_DTCOM03 AS "Data 3ª compra",
                        A5_CODPRF AS "Cód. no fornecedor"
                    FROM 
                        {database}.dbo.SA5010 FP
                    INNER JOIN
                        {database}.dbo.SA2010 FORN
                    ON
                        FP.A5_FORNECE = FORN.A2_COD 
                    WHERE 
                        A5_PRODUTO LIKE '{codigo}%'
                    ORDER BY FORN.A2_NREDUZ ASC;
                """
                self.guias_abertas_ultimos_fornecedores.append(codigo)
                try:
                    conn_saldo = pyodbc.connect(
                        f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')

                    cursor = conn_saldo.cursor()
                    cursor.execute(query)

                    nova_guia_ult_forn = QWidget()
                    layout_nova_guia_ult_forn = QVBoxLayout()
                    layout_cabecalho = QHBoxLayout()

                    tabela_ult_fornecedores = QTableWidget(nova_guia_ult_forn)

                    tabela_ult_fornecedores.setColumnCount(len(cursor.description))
                    tabela_ult_fornecedores.setHorizontalHeaderLabels(
                        [desc[0] for desc in cursor.description])

                    tabela_ult_fornecedores.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

                    # Tornar a tabela somente leitura
                    tabela_ult_fornecedores.setEditTriggers(QTableWidget.NoEditTriggers)

                    # Configurar a fonte da tabela1
                    fonte_tabela = QFont("Segoe UI", 10)  # Substitua por sua fonte desejada e tamanho
                    tabela_ult_fornecedores.setFont(fonte_tabela)

                    # Ajustar a altura das linhas
                    altura_linha = 20  # Substitua pelo valor desejado
                    tabela_ult_fornecedores.verticalHeader().setDefaultSectionSize(altura_linha)

                    for i, row in enumerate(cursor.fetchall()):
                        tabela_ult_fornecedores.insertRow(i)
                        for j, value in enumerate(row):
                            valor_formatado = str(value).strip()
                            item = QTableWidgetItem(valor_formatado)
                            item.setTextAlignment(Qt.AlignCenter)
                            tabela_ult_fornecedores.setItem(i, j, item)

                    tabela_ult_fornecedores.setSortingEnabled(True)

                    layout_cabecalho.addWidget(QLabel(f'Fornecedores\n\n{codigo} - {descricao}'),
                                               alignment=Qt.AlignLeft)
                    layout_nova_guia_ult_forn.addLayout(layout_cabecalho)

                    layout_nova_guia_ult_forn.addWidget(tabela_ult_fornecedores)
                    nova_guia_ult_forn.setLayout(layout_nova_guia_ult_forn)

                    nova_guia_ult_forn.setStyleSheet("""                                           
                        * {
                            background-color: #262626;
                        }

                        QLabel {
                            color: #A7A6A6;
                            font-size: 18px;
                            font-weight: bold;
                        }

                        QTableWidget {
                            border: 1px solid #000000;
                        }

                        QTableWidget QHeaderView::section {
                            background-color: #575a5f;
                            color: #fff;
                            padding: 5px;
                            height: 18px;
                        }

                        QTableWidget QHeaderView::section:horizontal {
                            border-top: 1px solid #333;
                        }

                        QTableWidget::item:selected {
                            background-color: #0066ff;
                            color: #fff;
                            font-weight: bold;
                        }        
                    """)

                    if not self.existe_guias_abertas():
                        # Se não houver guias abertas, adicione a guia ao layout principal
                        self.layout().addWidget(self.tabWidget)
                        self.tabWidget.setVisible(True)

                    self.tabWidget.addTab(nova_guia_ult_forn, f"Saldos em Estoque - {codigo}")
                    tabela_ult_fornecedores.itemDoubleClicked.connect(copiar_linha)

                except pyodbc.Error as ex:
                    print(f"Falha na consulta de estrutura. Erro: {str(ex)}")

                finally:
                    self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(nova_guia_ult_forn))
                    conn_saldo.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ComprasApp()
    username, password, database, server = setup_mssql()
    driver = '{SQL Server}'

    window.showMaximized()
    sys.exit(app.exec_())
