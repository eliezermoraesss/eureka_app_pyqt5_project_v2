import locale
import os
import sys

# Caminho absoluto para o diretório onde o módulo src está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from datetime import datetime

import pandas as pd
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QTableWidget, QTableWidgetItem, QHeaderView, QStyle, QAction, QDateEdit, QLabel, QSizePolicy, QTabWidget, QMenu, \
    QComboBox, QMessageBox
from sqlalchemy import create_engine

from src.app.utils.consultar_estrutura import ConsultaEstrutura
from src.app.utils.consultar_onde_usado import executar_consulta_onde_usado
from src.app.utils.consultar_saldo_estoque import executar_saldo_em_estoque
from src.app.utils.db_mssql import setup_mssql
from src.app.utils.load_session import load_session
from src.app.utils.utils import exibir_mensagem, abrir_desenho, exportar_excel, copiar_linha, abrir_tabela_pesos, \
    obter_codigo_item_selecionado
from src.app.utils.open_search_dialog import open_search_dialog
from src.dialog.loading_dialog import loading_dialog
from src.app.utils.run_image_comparator import run_image_comparator_exe, run_image_comparator_model
from src.app.utils.autocomplete_feature import AutoCompleteManager
from src.app.utils.search_history_manager import SearchHistoryManager
from src.resources.styles.qss_pcp import pcp_qss
from src.app.utils.abrir_hierarquia_estrutura import abrir_hierarquia_estrutura
from src.dialog.confirmation_dialog import show_confirmation_dialog
from src.app.utils.print_op_v2 import PrintProductionOrderDialogV2


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

def validar_campos(codigo_produto, numero_qp, numero_op):
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


class PcpApp(QWidget):
    guia_fechada = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.dataframe = None
        self.dataframe_original = None
        self.main_window = main_window
        user_data = load_session()
        username = user_data["username"]
        role = user_data["role"]

        self.username, self.password, self.database, self.server = setup_mssql()
        self.driver = '{SQL Server}'

        self.setWindowTitle(f"Eureka® PCP . {username} ({role})")
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

        self.engine = None

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
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

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

        self.setStyleSheet(pcp_qss())

        self.label_title = QLabel("Gestão de Ordens de Produção", self)
        self.label_title.setObjectName('label-title')

        self.label_line_number = QLabel("", self)
        self.label_line_number.setObjectName("label-line-number")
        self.label_line_number.setVisible(False)

        self.label_indicators = QLabel("", self)
        self.label_indicators.setObjectName("label-indicators")
        self.label_indicators.setVisible(False)
        self.label_indicators.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_enaplic_path = os.path.join(script_dir, '..', 'resources', 'images', 'LOGO.jpeg')
        self.logo_label = QLabel(self)
        self.logo_label.setObjectName('logo-enaplic')
        pixmap_logo = QPixmap(logo_enaplic_path).scaledToWidth(50)
        self.logo_label.setPixmap(pixmap_logo)
        self.logo_label.setAlignment(Qt.AlignRight)

        self.label_codigo = QLabel("Código", self)
        self.label_descricao_prod = QLabel("Descrição", self)
        self.label_contem_descricao_prod = QLabel("Contém na descrição", self)
        self.label_contem_descricao_prod.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_OP = QLabel("OP", self)
        self.label_qp = QLabel("QP", self)
        self.label_data_inicio = QLabel("Data inicial", self)
        self.label_data_inicio.setObjectName("data-inicio")
        self.label_data_fim = QLabel("Data final", self)
        self.label_data_fim.setObjectName("data-fim")
        self.label_campo_observacao = QLabel("Observação", self)

        self.campo_codigo = QLineEdit(self)
        self.campo_codigo.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_codigo.setMaxLength(13)
        self.campo_codigo.setFixedWidth(170)
        self.add_clear_button(self.campo_codigo)

        self.campo_descricao = QLineEdit(self)
        self.campo_descricao.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_descricao.setMaxLength(60)
        self.campo_descricao.setFixedWidth(280)
        self.add_clear_button(self.campo_descricao)

        self.campo_contem_descricao = QLineEdit(self)
        self.campo_contem_descricao.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_contem_descricao.setMaxLength(60)
        self.campo_contem_descricao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_clear_button(self.campo_contem_descricao)

        self.campo_qp = CustomLineEdit('QPS', 'qps', 'Código', self)
        self.campo_qp.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_qp.setMaxLength(6)
        self.campo_qp.setFixedWidth(110)
        self.add_clear_button(self.campo_qp)

        self.campo_OP = QLineEdit(self)
        self.campo_OP.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_OP.setMaxLength(11)
        self.campo_OP.setFixedWidth(220)
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
        self.btn_consultar.clicked.connect(self.btn_pesquisar)
        self.btn_consultar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        estrutura = ConsultaEstrutura()
        self.btn_consultar_estrutura = QPushButton("Consultar Estrutura", self)
        self.btn_consultar_estrutura.clicked.connect(lambda: estrutura.executar_consulta_estrutura(self, self.tree))
        self.btn_consultar_estrutura.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_consultar_estrutura.hide()

        self.btn_home = QPushButton("HOME", self)
        self.btn_home.setObjectName("btn_home")
        self.btn_home.clicked.connect(self.return_to_main)
        self.btn_home.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

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

        self.btn_image_comparator = QPushButton("Image Comparator", self)
        self.btn_image_comparator.clicked.connect(lambda: run_image_comparator_model(self))
        self.btn_image_comparator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_image_comparator.hide()

        self.btn_toggle_footer = QPushButton("Ocultar Status", self)
        self.btn_toggle_footer.clicked.connect(self.toggle_footer)
        self.btn_toggle_footer.hide()

        self.btn_imprimir_op = QPushButton("Imprimir OP", self)
        self.btn_imprimir_op.clicked.connect(self.imprimir_op)
        self.btn_imprimir_op.hide()

        self.combobox_status_op = QComboBox(self)
        self.combobox_status_op.setEditable(False)
        self.combobox_status_op.setObjectName('combobox-status-op')
        self.combobox_status_op.addItem('')
        self.combobox_status_op.addItem('Aberta')
        self.combobox_status_op.addItem('Fechada')

        self.combobox_aglutinado = QComboBox(self)
        self.combobox_aglutinado.setEditable(False)
        self.combobox_aglutinado.setObjectName('combobox-aglutinado')
        self.combobox_aglutinado.addItem('')
        self.combobox_aglutinado.addItem('Sim')
        self.combobox_aglutinado.addItem('Não')

        self.field_name_list = [
            "codigo",
            "descricao",
            "contem_descricao",
            "qp",
            "op",
            "observacao"
        ]

        object_fields = {
            "codigo": self.campo_codigo,
            "descricao": self.campo_descricao,
            "contem_descricao": self.campo_contem_descricao,
            "qp": self.campo_qp,
            "op": self.campo_OP,
            "observacao": self.campo_observacao
        }

        layout = QVBoxLayout()
        layout_title = QHBoxLayout()
        layout_campos_01 = QHBoxLayout()
        layout_campos_02 = QHBoxLayout()
        self.layout_buttons = QHBoxLayout()
        self.layout_footer_label = QHBoxLayout()

        layout_title.addStretch(1)
        layout_title.addWidget(self.label_title)
        layout_title.addStretch(1)

        container_codigo = QVBoxLayout()
        container_codigo.addWidget(self.label_codigo)
        container_codigo.addWidget(self.campo_codigo)

        container_descricao_prod = QVBoxLayout()
        container_descricao_prod.addWidget(self.label_descricao_prod)
        container_descricao_prod.addWidget(self.campo_descricao)

        container_contem_descricao_prod = QVBoxLayout()
        container_contem_descricao_prod.addWidget(self.label_contem_descricao_prod)
        container_contem_descricao_prod.addWidget(self.campo_contem_descricao)

        container_observacao = QVBoxLayout()
        container_observacao.addWidget(self.label_campo_observacao)
        container_observacao.addWidget(self.campo_observacao)

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

        container_combobox_status_op = QVBoxLayout()
        container_combobox_status_op.addWidget(QLabel("SITUAÇÃO OP"))
        container_combobox_status_op.addWidget(self.combobox_status_op)

        container_combobox_aglutinado = QVBoxLayout()
        container_combobox_aglutinado.addWidget(QLabel("AGLUTINADA?"))
        container_combobox_aglutinado.addWidget(self.combobox_aglutinado)

        layout_campos_01.addStretch()
        layout_campos_02.addStretch()
        layout_campos_01.addLayout(container_qp)
        layout_campos_01.addLayout(container_op)
        layout_campos_01.addLayout(container_codigo)
        layout_campos_01.addLayout(container_descricao_prod)
        layout_campos_01.addLayout(container_contem_descricao_prod)
        layout_campos_01.addLayout(container_observacao)
        layout_campos_02.addLayout(container_data_ini)
        layout_campos_02.addLayout(container_data_fim)
        layout_campos_02.addLayout(container_combobox_status_op)
        layout_campos_02.addLayout(container_combobox_aglutinado)
        layout_campos_01.addStretch()
        layout_campos_02.addStretch()

        self.layout_buttons.addStretch()
        self.layout_buttons.addWidget(self.btn_consultar)
        self.layout_buttons.addWidget(self.btn_consultar_estrutura)
        self.layout_buttons.addWidget(self.btn_onde_e_usado)
        self.layout_buttons.addWidget(self.btn_saldo_estoque)
        self.layout_buttons.addWidget(self.btn_nova_janela)
        self.layout_buttons.addWidget(self.btn_limpar)
        self.layout_buttons.addWidget(self.btn_abrir_desenho)
        self.layout_buttons.addWidget(self.btn_exportar_excel)
        self.layout_buttons.addWidget(self.btn_image_comparator)
        self.layout_buttons.addWidget(self.btn_fechar)
        self.layout_buttons.addWidget(self.btn_home)
        self.layout_buttons.addStretch()

        self.layout_footer_label.addStretch(1)
        self.layout_footer_label.addWidget(self.label_line_number)
        self.layout_footer_label.addWidget(self.label_indicators)
        self.layout_footer_label.addWidget(self.btn_toggle_footer)
        self.layout_footer_label.addWidget(self.btn_imprimir_op)
        self.layout_footer_label.addStretch(1)
        self.layout_footer_label.addWidget(self.logo_label)

        layout.addLayout(layout_title)

        layout.addLayout(layout_campos_01)
        layout.addLayout(layout_campos_02)
        layout.addLayout(self.layout_buttons)
        layout.addWidget(self.table_area)
        layout.addWidget(self.tree)
        layout.addLayout(self.layout_footer_label)
        self.setLayout(layout)

        history_manager = SearchHistoryManager('pcp')
        self.autocomplete_settings = AutoCompleteManager(history_manager)
        self.autocomplete_settings.setup_autocomplete(self.field_name_list, object_fields)

        self.campo_codigo.returnPressed.connect(self.btn_pesquisar)
        self.campo_qp.returnPressed.connect(self.btn_pesquisar)
        self.campo_OP.returnPressed.connect(self.btn_pesquisar)
        self.campo_descricao.returnPressed.connect(self.btn_pesquisar)
        self.campo_contem_descricao.returnPressed.connect(self.btn_pesquisar)
        self.campo_observacao.returnPressed.connect(self.btn_pesquisar)

    def imprimir_op(self):
        df_op_aberta = self.filter_table(situacao_op='ABERTA')
        line_number = df_op_aberta.shape[0]
        title = "Imprimir OP"
        message = f"Foram encontradas {line_number} OPs.\n\nDeseja prosseguir com a impressão?"
        response = show_confirmation_dialog(title, message)

        if response == QMessageBox.Yes:
            print_dialog = PrintProductionOrderDialogV2(df_op_aberta, self.dataframe_original, self)
            print_dialog.show()
        else:
            return

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

    def return_to_main(self):
        self.close()  # Fecha a janela atual
        self.main_window.reopen()  # Reabre ou traz a janela principal ao foco

    def abrir_nova_janela(self):
        eng_window = PcpApp(self.main_window)
        eng_window.showMaximized()
        self.main_window.sub_windows.append(eng_window)

    def fechar_guia(self, index):
        if index >= 0:
            try:
                codigo_guia_fechada = self.tabWidget.tabText(index).split(' - ')[1]
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
            # A lib Qt garante que o objeto do menu será destruído após uso
            menu.setAttribute(Qt.WA_DeleteOnClose)

            abrir_desenho_menu = QAction('Abrir desenho', self)
            abrir_desenho_menu.triggered.connect(lambda: abrir_desenho(self, table))

            image_comparator = QAction('Abrir ImageComparator®', self)
            image_comparator.triggered.connect(lambda: run_image_comparator_exe())

            estrutura = ConsultaEstrutura()
            consultar_estrutura = QAction('Consultar estrutura', self)
            consultar_estrutura.triggered.connect(lambda: estrutura.executar_consulta_estrutura(self, table))

            codigo_pai = obter_codigo_item_selecionado(table)
            hierarquia_estrutura = QAction('Consultar estrutura explodida...', self)
            hierarquia_estrutura.triggered.connect(lambda: abrir_hierarquia_estrutura(self, codigo_pai))

            onde_usado = QAction('Onde é usado?', self)
            onde_usado.triggered.connect(lambda: executar_consulta_onde_usado(self, table))

            saldo_estoque = QAction('Saldo em estoque', self)
            saldo_estoque.triggered.connect(lambda: executar_saldo_em_estoque(self, table))

            nova_janela = QAction('Nova janela', self)
            nova_janela.triggered.connect(self.abrir_nova_janela)

            tabela_pesos = QAction('Abrir Tabela de Pesos', self)
            tabela_pesos.triggered.connect(lambda: abrir_tabela_pesos())

            menu.addAction(nova_janela)
            menu.addSeparator()
            menu.addAction(abrir_desenho_menu)
            menu.addAction(image_comparator)
            menu.addAction(tabela_pesos)
            menu.addSeparator()
            menu.addAction(consultar_estrutura)
            menu.addAction(hierarquia_estrutura)
            menu.addAction(onde_usado)
            menu.addAction(saldo_estoque)

            menu.exec_(table.viewport().mapToGlobal(position))

    def clean_screen(self):
        self.table_area.show()
        self.tree.hide()
        self.campo_codigo.clear()
        self.campo_qp.clear()
        self.campo_OP.clear()
        self.campo_descricao.clear()
        self.campo_contem_descricao.clear()
        self.campo_observacao.clear()
        self.tree.setColumnCount(0)
        self.tree.setRowCount(0)
        self.label_line_number.hide()
        self.label_indicators.hide()

        self.btn_abrir_desenho.hide()
        self.btn_consultar_estrutura.hide()
        self.btn_exportar_excel.hide()
        self.btn_onde_e_usado.hide()
        self.btn_saldo_estoque.hide()
        self.btn_image_comparator.hide()
        self.btn_toggle_footer.hide()
        self.btn_imprimir_op.hide()

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
            self.btn_image_comparator.hide()
            self.btn_onde_e_usado.hide()
            self.btn_saldo_estoque.hide()
            self.btn_toggle_footer.hide()
            self.btn_imprimir_op.hide()
        else:
            self.btn_abrir_desenho.show()
            self.btn_consultar_estrutura.show()
            self.btn_exportar_excel.show()
            self.btn_image_comparator.show()
            self.btn_onde_e_usado.show()
            self.btn_saldo_estoque.show()
            self.btn_toggle_footer.show()
            self.btn_imprimir_op.show()

    def add_today_button(self, date_edit):
        calendar = date_edit.calendarWidget()
        calendar.setGeometry(10, 10, 600, 400)
        btn_today = QPushButton("Hoje", calendar)
        largura = 50
        altura = 20
        btn_today.setGeometry(20, 5, largura, altura)
        btn_today.clicked.connect(lambda: date_edit.setDate(QDate.currentDate()))

    def clear_and_filter(self, line_edit):
        line_edit.clear()
        self.btn_pesquisar()

    def add_clear_button(self, line_edit):
        clear_icon = self.style().standardIcon(QStyle.SP_LineEditClearButton)
        pixmap = clear_icon.pixmap(40, 40)  # Redimensionar o ícone para 20x20 pixels
        larger_clear_icon = QIcon(pixmap)
        clear_action = QAction(larger_clear_icon, "Clear", line_edit)
        clear_action.triggered.connect(lambda: self.clear_and_filter(line_edit))
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
        self.table_area.hide()
        self.tree.show()
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
        self.tree.setAlternatingRowColors(True)

        # Evita múltiplas conexões para o menu de contexto
        try:
            self.tree.customContextMenuRequested.disconnect()
        except TypeError:
            pass  # Ignora erros caso não haja conexão existente

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
        self.btn_image_comparator.setEnabled(status)
        self.btn_abrir_desenho.setEnabled(status)
        self.btn_onde_e_usado.setEnabled(status)
        self.btn_saldo_estoque.setEnabled(status)
        self.btn_consultar_estrutura.setEnabled(status)
        self.btn_toggle_footer.setEnabled(status)
        self.btn_imprimir_op.setEnabled(status)

    def query_consulta_ordem_producao(self):
        data_inicio_formatada = self.campo_data_inicio.date().toString("yyyyMMdd")
        data_fim_formatada = self.campo_data_fim.date().toString("yyyyMMdd")

        filtro_data = f"C2_EMISSAO >= '{data_inicio_formatada}' AND C2_EMISSAO <= '{data_fim_formatada}'" \
            if data_fim_formatada != '' and data_fim_formatada != '' else ''

        query = f"""
            SELECT 
                C2_ZZNUMQP AS "QP",
                qps.des_qp AS "PROJETO",
                CONCAT(C2_NUM, C2_ITEM, C2_SEQUEN) AS "OP",
                C2_PRODUTO AS "Código", 
                B1_DESC AS "Descrição", 
                C2_QUANT AS "Quantidade",
                C2_QUJE AS "Qtd. Disponível",
                C2_UM AS "Unid.", 
                C2_EMISSAO AS "Data Abertura", 
                C2_DATPRF AS "Prev. Entrega",
                C2_DATRF AS "Fechamento", 
                C2_OBS AS "Observação",
                C2_CC AS "Código CC",
                cc.CTT_DESC01 AS "Centro de Custo",
                C2_AGLUT AS "Aglutinada?",
                C2_NUM AS "OP GERAL", 
                C2_ITEM AS "Item", 
                C2_SEQUEN AS "Seq.",
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
            LEFT JOIN
                {self.database}.dbo.CTT010 cc 
            ON 
                C2_CC = CTT_CUSTO
            LEFT JOIN
                enaplic_management.dbo.tb_qps qps
            ON 
                cod_qp COLLATE Latin1_General_CI_AI = C2_ZZNUMQP COLLATE Latin1_General_CI_AI
            WHERE 
                {filtro_data}
                AND op.D_E_L_E_T_ <> '*'
            ORDER BY CONCAT(C2_NUM, C2_ITEM, C2_SEQUEN) DESC;
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

    def not_found_message(self, df):
        if not self.table_line_number(df.shape[0]):
            self.clean_screen()
            exibir_mensagem("Eureka!® PCP", 'Nenhum resultado encontrado nesta pesquisa.', "info")
            return False
        else:
            return True

    def btn_pesquisar(self):
        message = "🔄 Processando dados...\n\n⏱️ Por favor aguarde..."
        for field_name in self.field_name_list:
            self.autocomplete_settings.save_search_history(field_name)
        if self.dataframe_original is None:
            dialog = loading_dialog(self, "Eureka® PCP", message)
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
            dialog = loading_dialog(self, "Eureka® PCP", message)
            filtered_df = self.filter_table()
            if not self.not_found_message(filtered_df):
                self.dataframe_original = None
                dialog.close()
                return
            self.atualizar_tabela(filtered_df)
            self.dataframe = filtered_df.copy()
            dialog.close()

    def executar_consulta(self):
        conn_str = (f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};'
                    f'PWD={self.password}')
        self.engine = create_engine(f'mssql+pyodbc:///?odbc_connect={conn_str}')
        try:
            query_consulta_op = self.query_consulta_ordem_producao()

            self.label_line_number.hide()
            self.label_indicators.hide()
            self.controle_campos_formulario(False)
            self.button_visible_control(False)

            self.dataframe = pd.read_sql(query_consulta_op, self.engine)
            self.dataframe.insert(0, 'Status OP', '')

        except Exception as ex:
            print(ex)
            exibir_mensagem('Erro ao consultar tabela', f'Erro: {str(ex)}', 'error')

        finally:
            # Fecha a conexão com o banco de dados se estiver aberta
            if hasattr(self, 'engine'):
                self.engine.dispose()
                self.engine = None

    def filter_table(self, situacao_op=None):
        filter_qp = self.campo_qp.text().strip()
        filter_op = self.campo_OP.text().strip()
        filter_codigo = self.campo_codigo.text().strip().upper()
        filter_descricao = self.campo_descricao.text().strip().upper()
        filter_contem_descricao = self.campo_contem_descricao.text().strip().upper()
        filter_observacao = self.campo_observacao.text().strip().upper()
        if situacao_op is None:
            filter_status_op = self.combobox_status_op.currentText().upper()
        else:
            filter_status_op = situacao_op
        filter_aglutinado = self.combobox_aglutinado.currentText().upper()

        filtered_df = self.dataframe_original.copy()

        if filter_qp:
            filtered_df = filtered_df[filtered_df['QP'].str.endswith(filter_qp, na=False)]
        if filter_op:
            filtered_df = filtered_df[filtered_df['OP'].str.startswith(filter_op, na=False)]
        if filter_codigo:
            filtered_df = filtered_df[filtered_df['Código'].str.startswith(filter_codigo, na=False)]
        if filter_descricao:
            filtered_df = filtered_df[filtered_df['Descrição'].str.startswith(filter_descricao, na=False)]
        if filter_contem_descricao:
            filtered_df = filtered_df[filtered_df['Descrição'].str.contains(filter_contem_descricao, na=False)]
        if filter_observacao:
            filtered_df = filtered_df[filtered_df['Observação'].str.contains(filter_observacao, na=False)]
        if filter_status_op:
            if filter_status_op == 'FECHADA':
                filtered_df = filtered_df[filtered_df['Fechamento'].str.strip() != '']
            elif filter_status_op == 'ABERTA':
                filtered_df = filtered_df[filtered_df['Fechamento'].str.contains('        ', na=False)]
        if filter_aglutinado:
            if filter_aglutinado == 'SIM':
                filtered_df = filtered_df[filtered_df['Aglutinada?'].str.contains('S', na=False)]
            elif filter_aglutinado == 'NÃO':
                filtered_df = filtered_df[filtered_df['Aglutinada?'].str.contains(' ', na=False)]
        return filtered_df

    def atualizar_tabela(self, dataframe):
        self.tree.setRowCount(len(dataframe.index))
        self.tree.clearContents()
        self.tree.setRowCount(0)
        self.tree.setColumnCount(0)
        self.configurar_tabela(dataframe)
        self.configurar_tabela_tooltips(dataframe)

        # Construir caminhos relativos
        script_dir = os.path.dirname(os.path.abspath(__file__))
        open_icon_path = os.path.join(script_dir, '..', 'resources', 'images', 'red.png')
        closed_icon_path = os.path.join(script_dir, '..', 'resources', 'images', 'green.png')

        open_icon = QIcon(open_icon_path)
        closed_icon = QIcon(closed_icon_path)

        for i, (index, row) in enumerate(dataframe.iterrows()):
            self.tree.setSortingEnabled(False)
            self.tree.insertRow(i)
            for column_name, value in row.items():
                if value is not None:
                    if column_name == 'Status OP':
                        item = QTableWidgetItem()
                        if row['Fechamento'].strip() == '':
                            item.setIcon(open_icon)
                            item.setText('ABERTA')
                        else:
                            item.setIcon(closed_icon)
                            item.setText('FECHADA')
                        item.setTextAlignment(Qt.AlignCenter)
                    else:
                        item = process_table_item(column_name, value)

                        if column_name == 'Descrição':
                            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                        else:
                            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                else:
                    item = QTableWidgetItem('')
                self.tree.setItem(i, list(row.index).index(column_name), item)

        self.table_line_number(dataframe.shape[0])
        self.exibir_indicadores(dataframe)
        self.tree.viewport().update()
        self.tree.setSortingEnabled(True)
        self.controle_campos_formulario(True)
        self.button_visible_control(True)

    def exibir_indicadores(self, dataframe):
        quantidade_op_aberta = dataframe['Fechamento'].apply(
            lambda x: x.strip() == '' if isinstance(x, str) else True).sum()
        quantidade_op_fechada = dataframe['Fechamento'].apply(
            lambda x: x.strip() != '' if isinstance(x, str) else True).sum()
        indicadores_table = f"""
                <table border="1" cellspacing="2" cellpadding="4" style="border-collapse: collapse; text-align: left; width: 100%;">
                    <tr>
                        <th style="text-align: middle; vertical-align: middle;">STATUS</th>
                        <th style="text-align: right; vertical-align: middle;">QUANTIDADE</th>
                    </tr>
                    <tr>
                        <td style="vertical-align: middle;">OP ABERTA</td>
                        <td style="text-align: right; vertical-align: middle;">{quantidade_op_aberta}</td>
                    </tr>
                    <tr>
                        <td style="vertical-align: middle;">OP FECHADA</td>
                        <td style="text-align: right; vertical-align: middle;">{quantidade_op_fechada}</td>
                    </tr>
                </table>
            """
        self.label_indicators.setText(indicadores_table)
        self.label_indicators.show()


def format_date(value):
    try:
        if value and not value.isspace():
            data_obj = datetime.strptime(value.strip(), "%Y%m%d")
            return data_obj.strftime("%d/%m/%Y")
    except ValueError:
        return value
    return ''


def process_table_item(column_name, value):
    if value is None or (isinstance(value, str) and value.strip() == ''):
        return QTableWidgetItem('')

    if column_name == 'QP':
        return QTableWidgetItem(value.lstrip('0'))

    if column_name in ['Data Abertura', 'Prev. Entrega', 'Fechamento']:
        return QTableWidgetItem(format_date(value))

    if column_name == 'Aglutinada?':
        if value == 'S':
            return QTableWidgetItem('Sim')
        elif value == ' ':
            return QTableWidgetItem('Não')

    if column_name in ['Quantidade', 'Qtd. Disponível']:
        return QTableWidgetItem(format_quantity(value))

    return QTableWidgetItem(str(value).strip())


def format_quantity(value):
    """Formata a quantidade: inteiro sem casas decimais, decimal com duas casas"""
    if value.is_integer():
        return f"{int(value)}"
    return locale.format_string("%.2f", value, grouping=True)
