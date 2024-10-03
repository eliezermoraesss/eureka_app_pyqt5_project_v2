import locale
import os
import sys

# Caminho absoluto para o diretório onde o módulo src está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from datetime import datetime

import pandas as pd
from PyQt5.QtCore import Qt, QDate, QProcess, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QTableWidget, QTableWidgetItem, QHeaderView, QStyle, QAction, QDateEdit, QLabel, QSizePolicy, QTabWidget, QMenu, \
    QFrame
from sqlalchemy import create_engine

from src.app.utils.consultar_estrutura import executar_consulta_estrutura
from src.app.utils.consultar_onde_usado import executar_consulta_onde_usado
from src.app.utils.consultar_saldo_estoque import executar_saldo_em_estoque
from src.app.utils.db_mssql import setup_mssql
from src.app.utils.load_session import load_session
from src.app.utils.utils import exibir_mensagem, abrir_desenho, abrir_nova_janela, exportar_excel, copiar_linha
from src.app.utils.open_search_dialog import open_search_dialog
from src.dialog.loading_dialog import loading_dialog


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


class PcpApp(QWidget):
    guia_fechada = pyqtSignal()

    def __init__(self):
        super().__init__()
        user_data = load_session()
        username = user_data["username"]
        role = user_data["role"]

        self.username, self.password, self.database, self.server = setup_mssql()
        self.driver = '{SQL Server}'

        self.setWindowTitle(f"Eureka® PCP . {username} ({role})")
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

        self.engine = None
        self.interromper_consulta_sql = False
        self.tree = QTableWidget(self)
        self.tree.setColumnCount(0)
        self.tree.setRowCount(0)
        self.nova_janela = None

        self.tabWidget = QTabWidget(self)  # Adicione um QTabWidget ao layout principal
        self.tabWidget.setTabsClosable(True)  # Adicione essa linha para permitir o fechamento de guias
        self.tabWidget.tabCloseRequested.connect(self.fechar_guia)
        self.tabWidget.setVisible(False)  # Inicialmente, a guia está invisível

        self.guias_abertas = []
        self.guias_abertas_onde_usado = []
        self.guias_abertas_saldo = []

        self.altura_linha = 30
        self.tamanho_fonte_tabela = 10

        self.fonte_tabela = 'Segoe UI'
        fonte_campos = "Segoe UI"
        tamanho_fonte_campos = 16

        self.setStyleSheet("""
            * {
                background-color: #373A40;
            }

            QLabel {
                color: #DFE0E2;
                font-size: 12px;
                font-weight: bold;
                padding-left: 3px;
            }
            
            QLabel#label-line-number {
                font-size: 16px;
                font-weight: normal;
            }
            
            QLabel#label-title {
                margin: 10px;
                font-size: 30px;
                font-weight: bold;
            }
            
            QDateEdit {
                background-color: #DFE0E2;
                border: 1px solid #262626;
                margin-bottom: 20px;
                padding: 5px 10px;
                border-radius: 10px;
                height: 24px;
                font-size: 16px;
            }
            
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            
            QDateEdit::down-arrow {
                image: url(../resources/images/arrow.png);
                width: 10px;
                height: 10px;
            }

            QLineEdit {
                background-color: #EEEEEE;
                border: 1px solid #262626;
                padding: 5px 10px;
                border-radius: 10px;
                height: 24px;
                font-size: 16px;
            }

            QPushButton {
                background-color: #EB5B00;
                color: #EEEEEE;
                padding: 7px 10px;
                border: 2px;
                border-radius: 8px;
                font-size: 12px;
                height: 20px;
                font-weight: bold;
                margin: 0px 5px 10px 5px;
            }
            
            QPushButton#btn_engenharia {
                background-color: #0a79f8;
            }
            
            QPushButton#btn_compras {
                background-color: #836FFF;
            }
            
             QPushButton#btn_qps_concluidas {
                background-color: #00ADB5;
            }

            QPushButton:hover, QPushButton:hover#btn_engenharia, QPushButton:hover#btn_compras, 
            QPushButton:hover#btn_qps_concluidas { background-color: #E84545; color: #fff }
    
            QPushButton:pressed, QPushButton:pressed#btn_engenharia, QPushButton:pressed#btn_compras, 
            QPushButton:pressed#btn_qps_concluidas { background-color: #6703c5; color: #fff; }

            QTableWidget {
                border: 1px solid #000000;
                background-color: #686D76;
                padding-left: 10px;
                margin: 0;
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
                color: #fff;
                font-weight: bold;
                padding-right: 8px;
                padding-left: 8px;
            }

            QTableWidget::item:selected {
                background-color: #000000;
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
        
        self.label_title = QLabel("PCP", self)
        self.label_title.setObjectName('label-title')

        self.line = QFrame(self)
        self.line.setObjectName('line')
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_enaplic_path = os.path.join(script_dir, '..', 'resources', 'images', 'LOGO.jpeg')
        self.logo_label = QLabel(self)
        self.logo_label.setObjectName('logo-enaplic')
        pixmap_logo = QPixmap(logo_enaplic_path).scaledToWidth(50)
        self.logo_label.setPixmap(pixmap_logo)
        self.logo_label.setAlignment(Qt.AlignRight)

        self.label_codigo = QLabel("Código:", self)
        self.label_descricao_prod = QLabel("Descrição:", self)
        self.label_contem_descricao_prod = QLabel("Contém na descrição:", self)
        self.label_contem_descricao_prod.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_OP = QLabel("Número OP:", self)
        self.label_qp = QLabel("Número QP:", self)
        self.label_data_inicio = QLabel("Data inicial:", self)
        self.label_data_inicio.setObjectName("data-inicio")
        self.label_data_fim = QLabel("Data final:", self)
        self.label_data_fim.setObjectName("data-fim")
        self.label_campo_observacao = QLabel("Observação:", self)
        self.label_line_number = QLabel("", self)
        self.label_line_number.setVisible(False)

        self.campo_codigo = QLineEdit(self)
        self.campo_codigo.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_codigo.setMaxLength(13)
        self.campo_codigo.setFixedWidth(170)
        self.add_clear_button(self.campo_codigo)

        self.campo_descricao_prod = QLineEdit(self)
        self.campo_descricao_prod.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_descricao_prod.setMaxLength(60)
        self.campo_descricao_prod.setFixedWidth(280)
        self.add_clear_button(self.campo_descricao_prod)

        self.campo_contem_descricao_prod = QLineEdit(self)
        self.campo_contem_descricao_prod.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_contem_descricao_prod.setMaxLength(60)
        self.campo_contem_descricao_prod.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_clear_button(self.campo_contem_descricao_prod)

        self.campo_qp = CustomLineEdit('QPS', 'qps', 'Código', self)
        self.campo_qp.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_qp.setMaxLength(6)
        self.campo_qp.setFixedWidth(110)
        self.add_clear_button(self.campo_qp)

        self.campo_OP = QLineEdit(self)
        self.campo_OP.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_OP.setMaxLength(6)
        self.campo_OP.setFixedWidth(110)
        self.add_clear_button(self.campo_OP)

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

        self.campo_observacao = QLineEdit(self)
        self.campo_observacao.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_observacao.setMaxLength(60)
        self.campo_observacao.setFixedWidth(400)
        self.add_clear_button(self.campo_observacao)

        self.btn_consultar = QPushButton("Pesquisar", self)
        self.btn_consultar.clicked.connect(self.executar_consulta)
        self.btn_consultar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_consultar_estrutura = QPushButton("Consultar Estrutura", self)
        self.btn_consultar_estrutura.clicked.connect(lambda: executar_consulta_estrutura(self, self.tree))
        self.btn_consultar_estrutura.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_consultar_estrutura.hide()

        self.btn_qps_concluidas = QPushButton("Gestão QPS", self)
        self.btn_qps_concluidas.setObjectName("btn_qps_concluidas")
        self.btn_qps_concluidas.clicked.connect(self.abrir_modulo_qps_concluidas)
        self.btn_qps_concluidas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_abrir_compras = QPushButton("Compras", self)
        self.btn_abrir_compras.setObjectName("btn_compras")
        self.btn_abrir_compras.clicked.connect(self.abrir_modulo_compras)
        self.btn_abrir_compras.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_abrir_engenharia = QPushButton("Engenharia", self)
        self.btn_abrir_engenharia.setObjectName("btn_engenharia")
        self.btn_abrir_engenharia.clicked.connect(self.abrir_modulo_engenharia)
        self.btn_abrir_engenharia.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_onde_e_usado = QPushButton("Onde é usado?", self)
        self.btn_onde_e_usado.clicked.connect(lambda: executar_consulta_onde_usado(self, self.tree))
        self.btn_onde_e_usado.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_onde_e_usado.hide()

        self.btn_saldo_estoque = QPushButton("Saldos em Estoque", self)
        self.btn_saldo_estoque.clicked.connect(lambda: executar_saldo_em_estoque(self, self.tree))
        self.btn_saldo_estoque.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_saldo_estoque.hide()

        self.btn_limpar = QPushButton("Limpar", self)
        self.btn_limpar.clicked.connect(self.clean_screen)
        self.btn_limpar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_nova_janela = QPushButton("Nova Janela", self)
        self.btn_nova_janela.clicked.connect(lambda: abrir_nova_janela(self, PcpApp()))
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
        self.btn_fechar.clicked.connect(self.fechar_janela)
        self.btn_fechar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.campo_codigo.returnPressed.connect(self.executar_consulta)
        self.campo_qp.returnPressed.connect(self.executar_consulta)
        self.campo_OP.returnPressed.connect(self.executar_consulta)
        self.campo_descricao_prod.returnPressed.connect(self.executar_consulta)
        self.campo_contem_descricao_prod.returnPressed.connect(self.executar_consulta)
        self.campo_observacao.returnPressed.connect(self.executar_consulta)

        layout = QVBoxLayout()
        layout_title = QHBoxLayout()
        layout_campos_01 = QHBoxLayout()
        layout_campos_02 = QHBoxLayout()
        self.layout_buttons = QHBoxLayout()
        self.layout_footer_label = QHBoxLayout()
        
        layout_title.addStretch(1)
        layout_title.addWidget(self.logo_label)
        layout_title.addWidget(self.label_title)
        layout_title.addStretch(1)
        
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

        container_observacao = QVBoxLayout()
        container_observacao.addWidget(self.label_campo_observacao)
        container_observacao.addWidget(self.campo_observacao)

        layout_campos_01.addLayout(container_qp)
        layout_campos_01.addLayout(container_op)
        layout_campos_01.addLayout(container_codigo)
        layout_campos_01.addLayout(container_descricao_prod)
        layout_campos_01.addLayout(container_contem_descricao_prod)
        layout_campos_01.addLayout(container_observacao)
        layout_campos_02.addLayout(container_data_ini)
        layout_campos_02.addLayout(container_data_fim)
        layout_campos_01.addStretch()
        layout_campos_02.addStretch()

        self.layout_buttons.addWidget(self.btn_consultar)
        self.layout_buttons.addWidget(self.btn_consultar_estrutura)
        self.layout_buttons.addWidget(self.btn_onde_e_usado)
        self.layout_buttons.addWidget(self.btn_saldo_estoque)
        self.layout_buttons.addWidget(self.btn_nova_janela)
        self.layout_buttons.addWidget(self.btn_limpar)
        self.layout_buttons.addWidget(self.btn_abrir_desenho)
        self.layout_buttons.addWidget(self.btn_exportar_excel)
        self.layout_buttons.addWidget(self.btn_qps_concluidas)
        self.layout_buttons.addWidget(self.btn_abrir_compras)
        self.layout_buttons.addWidget(self.btn_abrir_engenharia)
        self.layout_buttons.addWidget(self.btn_fechar)
        self.layout_buttons.addStretch()

        self.layout_footer_label.addStretch(1)
        self.layout_footer_label.addWidget(self.label_line_number)
        self.layout_footer_label.addStretch(1)

        layout.addLayout(layout_title)
        layout.addWidget(self.line)

        layout.addLayout(layout_campos_01)
        layout.addLayout(layout_campos_02)
        layout.addLayout(self.layout_buttons)
        layout.addWidget(self.tree)
        layout.addLayout(self.layout_footer_label)
        self.setLayout(layout)

    def validar_campos(self, codigo_produto, numero_qp, numero_op):

        if len(codigo_produto) != 13 and not codigo_produto == '':
            exibir_mensagem("ATENÇÃO!",
                            "Produto não encontrado!\n\nCorrija e tente "
                            f"novamente.\n\nツ\n\nSMARTPLIC®",
                            "info")
            return True

        if len(numero_op) != 6 and not numero_op == '':
            exibir_mensagem("ATENÇÃO!",
                            "Ordem de Produção não encontrada!\n\nCorrija e tente "
                            f"novamente.\n\nツ\n\nSMARTPLIC®",
                            "info")
            return True

        if len(numero_qp.zfill(6)) != 6 and not numero_qp == '':
            exibir_mensagem("ATENÇÃO!",
                            "QP não encontrada!\n\nCorrija e tente "
                            f"novamente.\n\nツ\n\nSMARTPLIC®",
                            "info")
            return True

    def numero_linhas_consulta(self, query_consulta):

        order_by_a_remover = "ORDER BY op.R_E_C_N_O_ DESC;"
        query_sem_order_by = query_consulta.replace(order_by_a_remover, "")

        query = f"""
                    SELECT 
                        COUNT(*) AS total_records
                    FROM ({query_sem_order_by}) AS combined_results;
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
                    self.guias_abertas_saldo.remove(codigo_guia_fechada)

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

            context_menu_abrir_desenho = QAction('Abrir desenho', self)
            context_menu_abrir_desenho.triggered.connect(lambda: abrir_desenho(self, table))

            context_menu_consultar_estrutura = QAction('Consultar estrutura', self)
            context_menu_consultar_estrutura.triggered.connect(lambda: executar_consulta_estrutura(self, table))

            context_menu_consultar_onde_usado = QAction('Onde é usado?', self)
            context_menu_consultar_onde_usado.triggered.connect(lambda: executar_consulta_onde_usado(self, table))

            context_menu_saldo_estoque = QAction('Saldo em estoque', self)
            context_menu_saldo_estoque.triggered.connect(lambda: executar_saldo_em_estoque(self, table))

            context_menu_nova_janela = QAction('Nova janela', self)
            context_menu_nova_janela.triggered.connect(lambda: abrir_nova_janela(self, PcpApp()))

            menu.addAction(context_menu_abrir_desenho)
            menu.addAction(context_menu_consultar_estrutura)
            menu.addAction(context_menu_consultar_onde_usado)
            menu.addAction(context_menu_saldo_estoque)
            menu.addAction(context_menu_nova_janela)

            menu.exec_(table.viewport().mapToGlobal(position))

    def clean_screen(self):
        self.campo_codigo.clear()
        self.campo_qp.clear()
        self.campo_OP.clear()
        self.campo_descricao_prod.clear()
        self.campo_contem_descricao_prod.clear()
        self.campo_observacao.clear()
        self.tree.setColumnCount(0)
        self.tree.setRowCount(0)
        self.label_line_number.hide()

        self.btn_abrir_desenho.hide()
        self.btn_consultar_estrutura.hide()
        self.btn_exportar_excel.hide()
        self.btn_onde_e_usado.hide()
        self.btn_saldo_estoque.hide()

        self.guias_abertas.clear()
        self.guias_abertas_onde_usado.clear()
        self.guias_abertas_saldo.clear()

        while self.tabWidget.count():
            self.tabWidget.removeTab(0)
        self.tabWidget.setVisible(False)
        self.guia_fechada.emit()

    def button_visible_control(self, visible):
        if visible == "False":
            self.btn_abrir_desenho.hide()
            self.btn_consultar_estrutura.hide()
            self.btn_exportar_excel.hide()
            self.btn_onde_e_usado.hide()
            self.btn_saldo_estoque.hide()
        else:
            self.btn_abrir_desenho.show()
            self.btn_consultar_estrutura.show()
            self.btn_exportar_excel.show()
            self.btn_onde_e_usado.show()
            self.btn_saldo_estoque.show()

    def abrir_modulo_engenharia(self):
        process = QProcess()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, 'engenharia_model.pyw')
        process.startDetached("python", [script_path])

    def abrir_modulo_compras(self):
        process = QProcess()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, 'compras_model.pyw')
        process.startDetached("python", [script_path])

    def abrir_modulo_qps_concluidas(self):
        process = QProcess()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, 'qps_model.pyw')
        process.startDetached("python", [script_path])

    def add_today_button(self, date_edit):
        calendar = date_edit.calendarWidget()
        calendar.setGeometry(10, 10, 600, 400)
        btn_today = QPushButton("Hoje", calendar)
        largura = 50
        altura = 20
        btn_today.setGeometry(20, 5, largura, altura)
        btn_today.clicked.connect(lambda: date_edit.setDate(QDate.currentDate()))

    def add_clear_button(self, line_edit):
        clear_icon = self.style().standardIcon(QStyle.SP_LineEditClearButton)
        pixmap = clear_icon.pixmap(40, 40)  # Redimensionar o ícone para 20x20 pixels
        larger_clear_icon = QIcon(pixmap)
        clear_action = QAction(larger_clear_icon, "Clear", line_edit)
        clear_action.triggered.connect(line_edit.clear)
        line_edit.addAction(clear_action, QLineEdit.TrailingPosition)

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
        self.tree.horizontalHeader().setStretchLastSection(False)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(lambda pos: self.show_context_menu(pos, self.tree))

    def ordenar_tabela(self, logical_index):
        # Obter o índice real da coluna (considerando a ordem de classificação)
        index = self.tree.horizontalHeader().sortIndicatorOrder()

        # Definir a ordem de classificação
        order = Qt.AscendingOrder if index == 0 else Qt.DescendingOrder

        # Ordenar a tabela pela coluna clicada
        self.tree.sortItems(logical_index, order)

    def controle_campos_formulario(self, status):
        self.campo_codigo.setEnabled(status)
        self.campo_qp.setEnabled(status)
        self.campo_OP.setEnabled(status)
        self.campo_observacao.setEnabled(status)
        self.campo_data_inicio.setEnabled(status)
        self.campo_data_fim.setEnabled(status)
        self.btn_consultar.setEnabled(status)
        self.btn_exportar_excel.setEnabled(status)
        self.btn_abrir_desenho.setEnabled(status)
        self.btn_onde_e_usado.setEnabled(status)
        self.btn_saldo_estoque.setEnabled(status)
        self.btn_consultar_estrutura.setEnabled(status)

    def query_consulta_ordem_producao(self):

        numero_qp = self.campo_qp.text().upper().strip()
        numero_op = self.campo_OP.text().upper().strip()
        codigo_produto = self.campo_codigo.text().upper().strip()
        descricao_produto = self.campo_descricao_prod.text().upper().strip()
        contem_descricao = self.campo_contem_descricao_prod.text().upper().strip()
        observacao = self.campo_observacao.text().upper().strip()

        if self.validar_campos(codigo_produto, numero_qp, numero_op):
            self.btn_consultar.setEnabled(True)
            return

        numero_qp = numero_qp.zfill(6) if numero_qp != '' else numero_qp

        palavras_contem_descricao = contem_descricao.split('*')
        clausulas_contem_descricao = " AND ".join(
            [f"prod.B1_DESC LIKE '%{palavra}%'" for palavra in palavras_contem_descricao])
        data_inicio_formatada = self.campo_data_inicio.date().toString("yyyyMMdd")
        data_fim_formatada = self.campo_data_fim.date().toString("yyyyMMdd")

        filtro_data = f"AND C2_EMISSAO >= '{data_inicio_formatada}' AND C2_EMISSAO <= '{data_fim_formatada}'" if data_fim_formatada != '' and data_fim_formatada != '' else ''

        query = f"""
            SELECT 
                C2_ZZNUMQP AS "QP", 
                C2_NUM AS "OP", 
                C2_ITEM AS "Item", 
                C2_SEQUEN AS "Seq.",
                C2_PRODUTO AS "Código", 
                B1_DESC AS "Descrição", 
                C2_QUANT AS "Quant.", 
                C2_UM AS "UM", 
                C2_EMISSAO AS "Emissão", 
                C2_DATPRF AS "Prev. Entrega",
                C2_DATRF AS "Fechamento", 
                C2_OBS AS "Observação",
                C2_QUJE AS "Quant. Produzida", 
                C2_AGLUT AS "Aglutinada?",
                users.USR_NOME AS "Aberto por:" 
            FROM 
                {self.database}.dbo.SC2010 op
            LEFT JOIN 
                SB1010 prod ON C2_PRODUTO = B1_COD
            LEFT JOIN 
                {self.database}.dbo.SYS_USR users
            ON 
                users.USR_CNLOGON = op.C2_XMAQUIN 
                AND users.D_E_L_E_T_ <> '*'
                AND users.USR_ID = (
                    SELECT MAX(users.USR_ID) 
                    FROM {self.database}.dbo.SYS_USR users
                    WHERE users.USR_CNLOGON = op.C2_XMAQUIN 
                AND users.D_E_L_E_T_ <> '*')
            WHERE 
                C2_ZZNUMQP LIKE '%{numero_qp}'
                AND C2_PRODUTO LIKE '{codigo_produto}%'
                AND prod.B1_DESC LIKE '{descricao_produto}%'
                AND {clausulas_contem_descricao}
                AND C2_OBS LIKE '%{observacao}%'
                AND C2_NUM LIKE '{numero_op}%' {filtro_data}
                AND op.D_E_L_E_T_ <> '*'
            ORDER BY op.R_E_C_N_O_ DESC;
        """
        return query

    def configurar_tabela_tooltips(self, dataframe):
        # Mapa de tooltips correspondentes às colunas da consulta SQL
        tooltip_map = {
            "Status OP": "VERMELHO -> OP ABERTA\nVERDE -> OP FINALIZADA"
        }

        # Obtenha os cabeçalhos das colunas do dataframe
        headers = dataframe.columns

        # Adicione os cabeçalhos e os tooltips
        for i, header in enumerate(headers):
            item = QTableWidgetItem(header)
            tooltip = tooltip_map.get(header)
            item.setToolTip(tooltip)
            self.tree.setHorizontalHeaderItem(i, item)

    def executar_consulta(self):
        query_consulta_op = self.query_consulta_ordem_producao()
        if query_consulta_op is None:
            return
        query_contagem_linhas = self.numero_linhas_consulta(query_consulta_op)

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
                    message = f"Foram encontrados {line_number} resultados"
                else:
                    message = f"Foi encontrado {line_number} resultado"

                self.label_line_number.setText(f"{message}")
                self.label_line_number.show()

            else:
                exibir_mensagem("EUREKA® PCP", 'Nada encontrado!', "info")
                self.controle_campos_formulario(True)
                self.button_visible_control(False)
                return

            dialog = loading_dialog(self, "Eureka® Processando...", "Carregando dados do TOTVS...\n\nPor favor, aguarde")

            dataframe = pd.read_sql(query_consulta_op, self.engine)
            dataframe.insert(0, 'Status OP', '')

            self.configurar_tabela(dataframe)
            self.configurar_tabela_tooltips(dataframe)

            self.tree.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
            self.tree.setRowCount(0)

            # Construir caminhos relativos
            script_dir = os.path.dirname(os.path.abspath(__file__))
            open_icon_path = os.path.join(script_dir, '..', 'resources', 'images', 'red.png')
            closed_icon_path = os.path.join(script_dir, '..', 'resources', 'images', 'green.png')

            open_icon = QIcon(open_icon_path)
            closed_icon = QIcon(closed_icon_path)

            for i, row in dataframe.iterrows():
                if self.interromper_consulta_sql:
                    break

                self.tree.setSortingEnabled(False)
                self.tree.insertRow(i)
                for j, value in enumerate(row):
                    if value is not None:
                        if j == 0:
                            item = QTableWidgetItem()
                            if row['Fechamento'].strip() == '':
                                item.setIcon(open_icon)
                            else:
                                item.setIcon(closed_icon)
                            item.setTextAlignment(Qt.AlignCenter)
                        else:
                            if j == 14 and value == 'S':
                                value = 'Sim'
                            elif j == 14 and value != 'S':
                                value = 'Não'
                            if 9 <= j <= 11 and not value.isspace():
                                data_obj = datetime.strptime(value, "%Y%m%d")
                                value = data_obj.strftime("%d/%m/%Y")

                            item = QTableWidgetItem(str(value).strip())

                            if j not in (6, 12, 15):
                                item.setTextAlignment(Qt.AlignCenter)

                    else:
                        item = QTableWidgetItem('')

                    self.tree.setItem(i, j, item)

                # QCoreApplication.processEvents()

            self.tree.setSortingEnabled(True)
            self.controle_campos_formulario(True)
            self.button_visible_control(True)
            dialog.close()

        except Exception as ex:
            exibir_mensagem('Erro ao consultar tabela', f'Erro: {str(ex)}', 'error')

        finally:
            # Fecha a conexão com o banco de dados se estiver aberta
            if hasattr(self, 'engine'):
                self.engine.dispose()
                self.engine = None
            self.interromper_consulta_sql = False

    def fechar_janela(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PcpApp()
    username, password, database, server = setup_mssql()
    driver = '{SQL Server}'
    window.showMaximized()
    sys.exit(app.exec_())
