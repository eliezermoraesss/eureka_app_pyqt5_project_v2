import locale
import os
import sys
import time

# Caminho absoluto para o diretório onde o módulo src está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pyodbc
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QTableWidget, \
    QTableWidgetItem, QSizePolicy, QSpacerItem, QTabWidget, \
    QMenu, QAction, QComboBox, QStyle
from sqlalchemy import create_engine

from src.app.views.new_product_window import NewProductWindow
from src.app.views.edit_product_window import EditarProdutoItemWindow
from src.app.utils.consultar_estrutura import ConsultaEstrutura
from src.app.utils.consultar_onde_usado import executar_consulta_onde_usado
from src.app.utils.consultar_saldo_estoque import executar_saldo_em_estoque
from src.app.utils.consultar_ultimos_fornec import executar_ultimos_fornecedores
from src.app.utils.consultar_ultimas_nfe import consultar_ultimas_nfe
from src.app.utils.db_mssql import setup_mssql
from src.app.utils.load_session import load_session
from src.app.utils.open_search_dialog import open_search_dialog
from src.app.utils.abrir_hierarquia_estrutura import abrir_hierarquia_estrutura
from src.app.utils.utils import *
from src.app.views.copy_product_window import CopyProdutoItemWindow
from src.app.utils.run_image_comparator import *
from src.app.utils.autocomplete_feature import AutoCompleteManager
from src.app.utils.search_history_manager import SearchHistoryManager
from src.resources.styles.qss_engenharia import engenharia_qss


class CustomLineEdit(QLineEdit):
    def __init__(self, entity_name, entity, nome_coluna, parent=None):
        super(CustomLineEdit, self).__init__(parent)
        self.entity_name = entity_name
        self.entity = entity
        self.nome_coluna = nome_coluna

    def mousePressEvent(self, event):
        # Chama a função open_search_dialog quando o QLineEdit for clicado
        open_search_dialog(self.entity_name, self, self.entity, self.nome_coluna, self.parentWidget())
        # Continue com o comportamento padrão
        super(CustomLineEdit, self).mousePressEvent(event)


def numero_linhas_consulta(query_consulta):
    order_by_a_remover = "ORDER BY B1_COD ASC"
    query_sem_order_by = query_consulta.replace(order_by_a_remover, "")

    query = f"""
                SELECT 
                    COUNT(*) AS total_records
                FROM ({query_sem_order_by}) AS combined_results;
            """
    return query


def abrir_janela_novo_produto():
    new_product_window = NewProductWindow()
    new_product_window.exec_()


def abrir_janela_copiar_produto(selected_row_table):
    copy_window = CopyProdutoItemWindow(selected_row_table)
    copy_window.exec_()


class EngenhariaApp(QWidget):
    guia_fechada = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        user_data = load_session()
        username = user_data["username"]
        role = user_data["role"]
        self.engine = None
        self.dialog_open = False
        self.setWindowTitle(f"Eureka® Engenharia . {username} ({role})")
        self.username, self.password, self.database, self.server = setup_mssql()
        self.driver = '{SQL Server}'
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        self.nova_janela = None  # Adicione esta linha
        self.guias_abertas = []
        self.guias_abertas_onde_usado = []
        self.guias_abertas_saldo = []
        self.guias_abertas_ultimos_fornecedores = []
        self.guias_abertas_ultimas_nfe = []
        self.guias_abertas_visualizar_nfe = []
        fonte = "Segoe UI"
        tamanho_fonte = 12

        self.altura_linha = 30
        self.tamanho_fonte_tabela = 10
        self.fonte_tabela = 'Segoe UI'

        self.interromper_consulta_sql = False
        self.tree = QTableWidget(self)
        self.tree.setColumnCount(0)
        self.tree.setRowCount(0)

        self.tabWidget = QTabWidget(self)  # Adicione um QTabWidget ao layout principal
        self.tabWidget.setTabsClosable(True)  # Adicione essa linha para permitir o fechamento de guias
        self.tabWidget.tabCloseRequested.connect(self.fechar_guia)
        self.tabWidget.setVisible(False)  # Inicialmente, a guia está invisível

        self.label_line_number = QLabel("", self)
        self.label_line_number.setObjectName("label-line-number")
        self.label_line_number.setVisible(False)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_enaplic_path = os.path.join(script_dir, '..', 'resources', 'images', 'LOGO.jpeg')
        self.logo_label = QLabel(self)
        self.logo_label.setObjectName('logo-enaplic')
        pixmap_logo = QPixmap(logo_enaplic_path).scaledToWidth(60)
        self.logo_label.setPixmap(pixmap_logo)
        self.logo_label.setAlignment(Qt.AlignRight)

        self.campo_codigo = QLineEdit(self)
        self.campo_codigo.setMaxLength(13)
        self.campo_codigo.setFont(QFont(fonte, tamanho_fonte))
        self.add_clear_button(self.campo_codigo)

        self.campo_descricao = QLineEdit(self)
        self.campo_descricao.setMaxLength(100)
        self.campo_descricao.setFont(QFont(fonte, tamanho_fonte))
        self.add_clear_button(self.campo_descricao)

        self.campo_contem_descricao = QLineEdit(self)
        self.campo_contem_descricao.setMaxLength(60)
        self.campo_contem_descricao.setFont(QFont(fonte, tamanho_fonte))
        self.add_clear_button(self.campo_contem_descricao)

        self.campo_tipo = CustomLineEdit('Tipo', 'tipo', 'Código', self)
        self.campo_tipo.setMaxLength(2)
        self.campo_tipo.setFont(QFont(fonte, tamanho_fonte))
        self.add_clear_button(self.campo_tipo)

        self.campo_um = CustomLineEdit('Unidade de medida', 'unidade_medida', 'Código', self)
        self.campo_um.setMaxLength(2)
        self.campo_um.setFont(QFont(fonte, tamanho_fonte))
        self.add_clear_button(self.campo_um)

        self.campo_armazem = CustomLineEdit('Armazém', 'armazem', 'Código', self)
        self.campo_armazem.setMaxLength(2)
        self.campo_armazem.setFont(QFont(fonte, tamanho_fonte))
        self.add_clear_button(self.campo_armazem)

        self.campo_grupo = CustomLineEdit('Grupo', 'grupo', 'Código', self)
        self.campo_grupo.setMaxLength(4)
        self.campo_grupo.setFont(QFont(fonte, tamanho_fonte))
        self.add_clear_button(self.campo_grupo)

        self.campo_cc = CustomLineEdit('Centro de custo', 'centro_custo', 'Código', self)
        self.campo_cc.setMaxLength(9)
        self.campo_cc.setFont(QFont(fonte, tamanho_fonte))
        self.add_clear_button(self.campo_cc)

        self.combobox_bloqueio = QComboBox(self)
        self.combobox_bloqueio.setEditable(False)
        self.combobox_bloqueio.setObjectName("combobox_bloqueio")
        self.combobox_bloqueio.addItem("-", "")
        self.combobox_bloqueio.addItem("Sim", '1')
        self.combobox_bloqueio.addItem("Não", '2')

        self.btn_consultar = QPushButton("Pesquisar", self)
        self.btn_consultar.clicked.connect(self.btn_consultar_actions)
        self.btn_consultar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_new_product = QPushButton("Cadastrar novo produto", self)
        self.btn_new_product.clicked.connect(abrir_janela_novo_produto)
        self.btn_new_product.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_home = QPushButton("HOME", self)
        self.btn_home.setObjectName("btn_home")
        self.btn_home.clicked.connect(self.return_to_main)
        self.btn_home.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        estrutura = ConsultaEstrutura()
        self.btn_consultar_estrutura = QPushButton("Consultar Estrutura", self)
        self.btn_consultar_estrutura.clicked.connect(
            lambda: estrutura.executar_consulta_estrutura(self, table=self.tree))
        self.btn_consultar_estrutura.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_consultar_estrutura.hide()

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

        self.btn_calculo_peso = QPushButton("Tabela de pesos", self)
        self.btn_calculo_peso.clicked.connect(lambda: abrir_tabela_pesos())
        self.btn_calculo_peso.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_image_comparator = QPushButton("Image Comparator", self)
        self.btn_image_comparator.clicked.connect(lambda: run_image_comparator_model(self))
        self.btn_image_comparator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_fechar = QPushButton("Fechar", self)
        self.btn_fechar.clicked.connect(self.fechar_janela)
        self.btn_fechar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.field_name_list = [
            "codigo",
            "descricao",
            "contem_descricao",
            "tipo",
            "unid_medida",
            "armazem",
            "grupo",
            "centro_custo"
        ]

        object_fields = {
            "codigo": self.campo_codigo,
            "descricao": self.campo_descricao,
            "contem_descricao": self.campo_contem_descricao,
            "tipo": self.campo_tipo,
            "unid_medida": self.campo_um,
            "armazem": self.campo_armazem,
            "grupo": self.campo_grupo,
            "centro_custo": self.campo_cc
        }

        layout = QVBoxLayout()
        layout_campos_01 = QHBoxLayout()
        layout_campos_02 = QHBoxLayout()
        layout_button_03 = QHBoxLayout()
        layout_button_04 = QHBoxLayout()
        self.layout_footer_label = QHBoxLayout()

        layout_campos_01.addWidget(QLabel("Código:"))
        layout_campos_01.addWidget(self.campo_codigo)
        layout_campos_01.addWidget(QLabel("Descrição:"))
        layout_campos_01.addWidget(self.campo_descricao)
        layout_campos_01.addWidget(QLabel("Contém na Descrição:"))
        layout_campos_01.addWidget(self.campo_contem_descricao)

        layout_campos_02.addWidget(QLabel("Tipo:"))
        layout_campos_02.addWidget(self.campo_tipo)
        layout_campos_02.addWidget(QLabel("Unid. Medida:"))
        layout_campos_02.addWidget(self.campo_um)
        layout_campos_02.addWidget(QLabel("Armazém:"))
        layout_campos_02.addWidget(self.campo_armazem)
        layout_campos_02.addWidget(QLabel("Grupo:"))
        layout_campos_02.addWidget(self.campo_grupo)
        layout_campos_02.addWidget(QLabel("Centro Custo:"))
        layout_campos_02.addWidget(self.campo_cc)
        layout_campos_02.addWidget(QLabel("Bloqueio:"))
        layout_campos_02.addWidget(self.combobox_bloqueio)

        layout_button_03.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout_button_03.addWidget(self.btn_consultar)
        layout_button_03.addWidget(self.btn_new_product)
        layout_button_03.addWidget(self.btn_limpar)
        layout_button_04.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout_button_04.addWidget(self.btn_consultar_estrutura)
        layout_button_04.addWidget(self.btn_onde_e_usado)
        layout_button_04.addWidget(self.btn_saldo_estoque)
        layout_button_04.addWidget(self.btn_ultimos_fornecedores)
        layout_button_04.addWidget(self.btn_ultimas_nfe)
        layout_button_03.addWidget(self.btn_nova_janela)
        layout_button_04.addWidget(self.btn_abrir_desenho)
        layout_button_04.addWidget(self.btn_exportar_excel)
        layout_button_04.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout_button_03.addWidget(self.btn_calculo_peso)
        layout_button_03.addWidget(self.btn_image_comparator)
        layout_button_03.addWidget(self.btn_fechar)
        layout_button_03.addWidget(self.btn_home)
        layout_button_03.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.layout_footer_label.addStretch(1)
        self.layout_footer_label.addWidget(self.label_line_number)
        self.layout_footer_label.addStretch(1)
        self.layout_footer_label.addWidget(self.logo_label)

        layout.addLayout(layout_campos_01)
        layout.addLayout(layout_campos_02)
        layout.addLayout(layout_button_03)
        layout.addLayout(layout_button_04)
        layout.addWidget(self.tree)
        layout.addLayout(self.layout_footer_label)
        self.setLayout(layout)

        history_manager = SearchHistoryManager('engenharia')
        self.autocomplete_settings = AutoCompleteManager(history_manager)
        self.autocomplete_settings.setup_autocomplete(self.field_name_list, object_fields)

        self.campo_codigo.returnPressed.connect(self.executar_consulta)
        self.campo_descricao.returnPressed.connect(self.executar_consulta)
        self.campo_contem_descricao.returnPressed.connect(self.executar_consulta)
        self.campo_tipo.returnPressed.connect(self.executar_consulta)
        self.campo_um.returnPressed.connect(self.executar_consulta)
        self.campo_armazem.returnPressed.connect(self.executar_consulta)
        self.campo_grupo.returnPressed.connect(self.executar_consulta)
        self.campo_cc.returnPressed.connect(self.executar_consulta)

        self.setStyleSheet(engenharia_qss())

    def btn_consultar_actions(self):
        for field_name in self.field_name_list:
            self.autocomplete_settings.save_search_history(field_name)
        self.executar_consulta()

    def return_to_main(self):
        self.close()  # Fecha a janela atual
        self.main_window.reopen()  # Reabre ou traz a janela principal ao foco

    def abrir_nova_janela(self):
        eng_window = EngenhariaApp(self.main_window)
        eng_window.showMaximized()
        self.main_window.sub_windows.append(eng_window)

    def add_clear_button(self, line_edit):
        clear_icon = self.style().standardIcon(QStyle.SP_LineEditClearButton)

        line_edit_height = line_edit.height()
        pixmap = clear_icon.pixmap(line_edit_height - 4, line_edit_height - 4)
        larger_clear_icon = QIcon(pixmap)

        clear_action = QAction(larger_clear_icon, "Limpar", line_edit)
        clear_action.triggered.connect(line_edit.clear)
        line_edit.addAction(clear_action, QLineEdit.TrailingPosition)

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

            nova_janela = QAction('Nova janela', self)
            nova_janela.triggered.connect(self.abrir_nova_janela)

            new_product = QAction('Cadastrar novo produto...', self)
            new_product.triggered.connect(abrir_janela_novo_produto)

            cadastro_copia_produto = QAction('Cadastro semelhante...', self)
            cadastro_copia_produto.triggered.connect(self.copiar_item_selecionado)

            editar_action = QAction('Editar cadastro...', self)
            editar_action.triggered.connect(self.editar_item_selecionado)

            abrir_desenho_menu = QAction('Abrir desenho', self)
            abrir_desenho_menu.triggered.connect(lambda: abrir_desenho(self, table))

            estrutura = ConsultaEstrutura()
            consultar_estrutura = QAction('Consultar estrutura', self)
            consultar_estrutura.triggered.connect(lambda: estrutura.executar_consulta_estrutura(self, table=table))

            codigo_pai = obter_codigo_item_selecionado(table)
            hierarquia_estrutura = QAction('Consultar estrutura explodida...', self)
            hierarquia_estrutura.triggered.connect(lambda: abrir_hierarquia_estrutura(self, codigo_pai))

            consultar_onde_usado = QAction('Onde é usado?', self)
            consultar_onde_usado.triggered.connect(lambda: executar_consulta_onde_usado(self, table))

            saldo_estoque = QAction('Saldo em estoque', self)
            saldo_estoque.triggered.connect(lambda: executar_saldo_em_estoque(self, table))

            ultimo_fornecedor = QAction('Últimos Fornecedores', self)
            ultimo_fornecedor.triggered.connect(lambda: executar_ultimos_fornecedores(self, table))

            ultimas_nfe = QAction('Últimas Notas Fiscais', self)
            ultimas_nfe.triggered.connect(lambda: consultar_ultimas_nfe(self, table))

            image_comparator = QAction('Abrir ImageComparator®', self)
            image_comparator.triggered.connect(lambda: run_image_comparator_model(self))

            tabela_pesos = QAction('Abrir Tabela de Pesos', self)
            tabela_pesos.triggered.connect(lambda: abrir_tabela_pesos())

            menu.addAction(nova_janela)
            menu.addSeparator()
            menu.addAction(new_product)
            menu.addAction(cadastro_copia_produto)
            menu.addAction(editar_action)
            menu.addSeparator()
            menu.addAction(abrir_desenho_menu)
            menu.addAction(image_comparator)
            menu.addAction(tabela_pesos)
            menu.addSeparator()
            menu.addAction(consultar_estrutura)
            menu.addAction(hierarquia_estrutura)
            menu.addAction(consultar_onde_usado)
            menu.addAction(saldo_estoque)
            menu.addAction(ultimo_fornecedor)
            menu.addAction(ultimas_nfe)

            menu.exec_(table.viewport().mapToGlobal(position))

    def linha_selecionada(self):
        selected_row = self.tree.currentRow()
        if selected_row != -1:
            selected_row_table = []
            for column in range(self.tree.columnCount()):
                item = self.tree.item(selected_row, column)
                selected_row_table.append(item.text() if item else "")
            return selected_row_table

    def copiar_item_selecionado(self):
        selected_row_table = self.linha_selecionada()
        if selected_row_table:
            abrir_janela_copiar_produto(selected_row_table)

    def editar_item_selecionado(self):
        selected_row_table = self.linha_selecionada()
        if selected_row_table:
            self.abrir_janela_edicao(selected_row_table)

    def abrir_janela_edicao(self, selected_row_table):
        edit_window = EditarProdutoItemWindow(selected_row_table)
        if edit_window.exec_():
            selected_row = self.tree.currentRow()
            for column, value in enumerate(selected_row_table):
                item = QTableWidgetItem(value)
                self.tree.setItem(selected_row, column, item)

    def configurar_tabela_tooltips(self, dataframe):
        tooltips = {
            "B1_COD": "Código do produto",
            "B1_DESC": "Descrição do produto",
            "B1_XDESC2": "Descrição completa do produto",
            "B1_TIPO": "Tipo de produto\n\nMC - Material de consumo\nMP - Matéria-prima\nPA - Produto Acabado\nPI - "
                       "Produto Intermediário\nSV - Serviço",
            "B1_UM": "Unidade de medida",
            "B1_LOCPAD": "Armazém padrão\n\n01 - Matéria-prima\n02 - Produto Intermediário\n03 - Produto "
                         "Comercial\n04 - Produto Acabado",
            "B1_GRUPO": "Grupo do produto",
            "B1_ZZNOGRP": "Descrição do grupo do produto",
            "B1_CC": "Centro de custo",
            "B1_MSBLQL": "Indica se o produto está bloqueado",
            "B1_REVATU": "Revisão atual do produto",
            "B1_DATREF": "Data de referência",
            "B1_UREV": "Unidade de revisão",
            "B1_ZZLOCAL": "Localização do produto"
        }

        headers = dataframe.columns

        # Adicione os cabeçalhos e os tooltips
        for i, header in enumerate(headers):
            item = QTableWidgetItem(header)
            tooltip = tooltips.get(header)
            item.setToolTip(tooltip)
            self.tree.setHorizontalHeaderItem(i, item)

    def clean_screen(self):
        # Limpar os dados dos campos
        self.campo_codigo.clear()
        self.campo_descricao.clear()
        self.campo_contem_descricao.clear()
        self.campo_tipo.clear()
        self.campo_um.clear()
        self.campo_armazem.clear()
        self.campo_grupo.clear()
        self.campo_cc.clear()
        self.combobox_bloqueio.setCurrentText('-')
        self.tree.setColumnCount(0)
        self.tree.setRowCount(0)
        self.label_line_number.hide()

        self.btn_abrir_desenho.hide()
        self.btn_consultar_estrutura.hide()
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
        self.guias_abertas_visualizar_nfe.clear()

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
            self.btn_ultimos_fornecedores.hide()
            self.btn_ultimas_nfe.hide()
        else:
            self.btn_abrir_desenho.show()
            self.btn_consultar_estrutura.show()
            self.btn_exportar_excel.show()
            self.btn_onde_e_usado.show()
            self.btn_saldo_estoque.show()
            self.btn_ultimos_fornecedores.show()
            self.btn_ultimas_nfe.show()

    def controle_campos_formulario(self, status):
        self.campo_codigo.setEnabled(status)
        self.campo_descricao.setEnabled(status)
        self.campo_contem_descricao.setEnabled(status)
        self.campo_tipo.setEnabled(status)
        self.campo_um.setEnabled(status)
        self.campo_armazem.setEnabled(status)
        self.campo_grupo.setEnabled(status)
        self.campo_cc.setEnabled(status)
        self.btn_consultar.setEnabled(status)
        self.combobox_bloqueio.setEnabled(status)

    def query_consulta_tabela_produtos(self):
        codigo = self.campo_codigo.text().upper().strip()
        descricao = self.campo_descricao.text().upper().strip()
        descricao2 = self.campo_contem_descricao.text().upper().strip()
        tipo = self.campo_tipo.text().upper().strip()
        um = self.campo_um.text().upper().strip()
        armazem = self.campo_armazem.text().upper().strip()
        grupo = self.campo_grupo.text().upper().strip()
        centro_custo = self.campo_cc.text().upper().strip()
        status_bloqueio = self.combobox_bloqueio.currentData()

        status_bloqueio = status_bloqueio if status_bloqueio is not None else ''

        lista_campos = [codigo, descricao, descricao2, tipo, um, armazem, grupo, centro_custo]

        if all(valor == '' for valor in lista_campos):
            self.btn_consultar.setEnabled(False)
            exibir_mensagem("ATENÇÃO!",
                            "Os campos de pesquisa estão vazios.\nPreencha algum campo e tente "
                            "novamente.\n\nツ\n\nSMARTPLIC®",
                            "info")
            return True

        # Dividir descricao2 em partes usando o delimitador *
        descricao2_parts = descricao2.split('*')
        # Construir cláusulas LIKE dinamicamente para descricao2
        descricao2_clauses = " AND ".join([f"B1_DESC LIKE '%{part}%'" for part in descricao2_parts])

        filtro_bloqueio = f"AND B1_MSBLQL = '{status_bloqueio}'" if status_bloqueio != '' else ''

        query = f"""
        SELECT B1_COD AS "Código", 
            B1_DESC AS "Descrição", 
            B1_XDESC2 AS "Desc. Compl.", 
            B1_TIPO AS "Tipo", 
            B1_UM AS "Unid. Med", 
            B1_LOCPAD AS "Armazém", 
            B1_GRUPO AS "Grupo", 
            B1_ZZNOGRP AS "Desc. Grupo", 
            B1_CC AS "Centro Custo", 
            B1_MSBLQL AS "Bloqueado?", 
            B1_REVATU AS "Últ. Rev.", 
            B1_DATREF AS "Cadastrado em:", 
            B1_UREV AS "Data Últ. Rev.", 
            B1_ZZLOCAL AS "Endereço"
        FROM 
            {self.database}.dbo.SB1010
        WHERE 
            B1_COD LIKE '{codigo}%' 
            AND B1_DESC LIKE '{descricao}%' 
            AND {descricao2_clauses}
            AND B1_TIPO LIKE '{tipo}%' 
            AND B1_UM LIKE '{um}%' 
            AND B1_LOCPAD LIKE '{armazem}%' 
            AND B1_GRUPO LIKE '{grupo}%'
            AND B1_CC LIKE '{centro_custo}%'
            {filtro_bloqueio}
            AND D_E_L_E_T_ <> '*'
            ORDER BY B1_COD ASC
        """
        return query

    def executar_consulta(self):
        query_consulta = self.query_consulta_tabela_produtos()

        if isinstance(query_consulta, bool) and query_consulta:
            self.btn_consultar.setEnabled(True)
            return

        query_contagem_linhas = numero_linhas_consulta(query_consulta)

        self.label_line_number.hide()
        self.controle_campos_formulario(False)
        self.button_visible_control(False)

        conn_str = (f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};'
                    f'PWD={self.password}')
        self.engine = create_engine(f'mssql+pyodbc:///?odbc_connect={conn_str}')

        try:
            dataframe_line_number = pd.read_sql(query_contagem_linhas, self.engine)
            line_number = dataframe_line_number.iloc[0, 0]
            dataframe = pd.read_sql(query_consulta, self.engine)
            dataframe.insert(5, 'Desenho PDF', '')

            if not dataframe.empty:

                if line_number > 1:
                    message = f"Foram encontrados {line_number} itens"
                else:
                    message = f"Foi encontrado {line_number} item"

                self.label_line_number.setText(f"{message}")
                self.label_line_number.show()

                self.configurar_tabela(dataframe)
                self.configurar_tabela_tooltips(dataframe)

                # Limpar a ordenação
                self.tree.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)

                # Limpar a tabela
                self.tree.setRowCount(0)

                time.sleep(0.1)
            else:
                self.controle_campos_formulario(True)
                self.clean_screen()
                exibir_mensagem("EUREKA® Engenharia", 'Nada encontrado!', "info")
                return

            COLOR_FILE_EXISTS = QColor(51, 211, 145)  # green
            COLOR_FILE_MISSING = QColor(201, 92, 118)  # light red

            # Preencher a tabela com os resultados
            for i, (index, row) in enumerate(dataframe.iterrows()):
                self.tree.setSortingEnabled(False)  # Permitir ordenação
                # Inserir os valores formatados na tabela
                self.tree.insertRow(i)
                for column_name, value in row.items():
                    if column_name == 'Bloqueado?':  # Verifica se o valor é da coluna B1_MSBLQL
                        # Converte o valor 1 para 'Sim' e 2 para 'Não'
                        if value == '1':
                            value = 'Sim'
                        else:
                            value = 'Não'
                    elif column_name == 'Cadastrado em:' or column_name == 'Data Últ. Rev.':
                        if not value.isspace():
                            data_obj = datetime.strptime(value, "%Y%m%d")
                            value = data_obj.strftime("%d/%m/%Y")

                    item = QTableWidgetItem(str(value).strip())

                    if column_name not in ['Código', 'Descrição']:
                        item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    else:
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

                    # Special handling for Desenho PDF column
                    if column_name == 'Desenho PDF':
                        codigo_desenho = row['Código'].strip()  # Assuming 'Código' is the column with drawing codes
                        pdf_path = os.path.join(r"\\192.175.175.4\dados\EMPRESA\PROJETOS\PDF-OFICIAL",
                                                f"{codigo_desenho}.PDF")

                        # Check if file exists and set background color accordingly
                        if os.path.exists(pdf_path):
                            item.setBackground(COLOR_FILE_EXISTS)
                            item.setText('Sim')
                            item.setToolTip("Desenho encontrado")
                        else:
                            item.setBackground(COLOR_FILE_MISSING)
                            item.setText('Não')
                            item.setToolTip("Desenho não encontrado")

                    self.tree.setItem(i, list(row.index).index(column_name), item)

            self.tree.setSortingEnabled(True)  # Permitir ordenação

            self.controle_campos_formulario(True)
            self.button_visible_control(True)

        except pyodbc.Error as ex:
            exibir_mensagem("EUREKA® Engenharia", f'Falha ao consultar banco de dados - {ex}\n\n'
                                                  f'executar_consulta(self)', "error")
            print(f"Falha na consulta. Erro: {str(ex)}")

        finally:
            if hasattr(self, 'engine'):
                self.engine.dispose()
                self.engine = None
            self.interromper_consulta_sql = False

    def fechar_janela(self):
        self.close()

    def fechar_guia(self, index):
        if index >= 0:
            try:
                codigo_guia_fechada = self.tabWidget.tabText(index).split(' - ')[1]
                self.guias_abertas.remove(codigo_guia_fechada)

            # Por ter duas listas de controle de abas abertas, 'guias_abertas = []' e 'guias_abertas_onde_usado = []',
            # ao fechar uma guia ocorre uma exceção (ValueError) se o código não for encontrado em uma das listas.
            # Utilizei try/except para contornar esse problema.
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
