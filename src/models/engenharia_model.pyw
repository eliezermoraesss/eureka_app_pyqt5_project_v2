import locale
import sys
import time

import pyodbc
from PyQt5.QtCore import Qt, pyqtSignal, QProcess
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QTableWidget, \
    QTableWidgetItem, QSizePolicy, QSpacerItem, QTabWidget, \
    QCheckBox, QMenu, QAction, QComboBox, QStyle
from sqlalchemy import create_engine

from src.app.utils.consultar_estrutura import executar_consulta_estrutura
from src.app.utils.consultar_onde_usado import executar_consulta_onde_usado
from src.app.utils.consultar_saldo_estoque import executar_saldo_em_estoque
from src.app.utils.db_mssql import setup_mssql
from src.app.utils.utils import *


def abrir_tabela_pesos():
    os.startfile(r'\\192.175.175.4\f\INTEGRANTES\ELIEZER\DOCUMENTOS_UTEIS\TABELA_PESO.xlsx')


def numero_linhas_consulta(query_consulta):
    order_by_a_remover = "ORDER BY B1_COD ASC"
    query_sem_order_by = query_consulta.replace(order_by_a_remover, "")

    query = f"""
                SELECT 
                    COUNT(*) AS total_records
                FROM ({query_sem_order_by}) AS combined_results;
            """
    return query


class EngenhariaApp(QWidget):
    # Adicione este sinal à classe
    guia_fechada = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.engine = None
        self.setWindowTitle("EUREKA® ENGENHARIA - v2.0")

        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

        self.nova_janela = None  # Adicione esta linha
        self.guias_abertas = []
        self.guias_abertas_onde_usado = []
        self.guias_abertas_saldo = []
        fonte = "Segoe UI"
        tamanho_fonte = 10

        self.altura_linha = 30
        self.tamanho_fonte_tabela = 10
        self.fonte_tabela = 'Segoe UI'

        self.interromper_consulta_sql = False
        self.tree = QTableWidget(self)
        self.tree.setColumnCount(0)
        self.tree.setRowCount(0)

        self.process = QProcess(self)

        self.tabWidget = QTabWidget(self)  # Adicione um QTabWidget ao layout principal
        self.tabWidget.setTabsClosable(True)  # Adicione essa linha para permitir o fechamento de guias
        self.tabWidget.tabCloseRequested.connect(self.fechar_guia)
        self.tabWidget.setVisible(False)  # Inicialmente, a guia está invisível

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
        self.campo_codigo.setFont(QFont(fonte, tamanho_fonte))
        self.add_clear_button(self.campo_codigo)

        self.campo_descricao = QLineEdit(self)
        self.campo_descricao.setFont(QFont(fonte, tamanho_fonte))
        self.add_clear_button(self.campo_descricao)

        self.campo_contem_descricao = QLineEdit(self)
        self.campo_contem_descricao.setFont(QFont(fonte, tamanho_fonte))
        self.add_clear_button(self.campo_contem_descricao)

        self.campo_tipo = QLineEdit(self)
        self.campo_tipo.setFont(QFont(fonte, tamanho_fonte))
        self.add_clear_button(self.campo_tipo)

        self.campo_um = QLineEdit(self)
        self.campo_um.setFont(QFont(fonte, tamanho_fonte))
        self.add_clear_button(self.campo_um)

        self.campo_grupo = QLineEdit(self)
        self.campo_grupo.setFont(QFont(fonte, tamanho_fonte))
        self.add_clear_button(self.campo_grupo)

        self.checkbox_bloqueado = QCheckBox("Bloqueado?", self)

        self.btn_consultar = QPushButton("Pesquisar", self)
        self.btn_consultar.clicked.connect(self.executar_consulta)
        self.btn_consultar.setMinimumWidth(100)

        self.btn_abrir_pcp = QPushButton("PCP", self)
        self.btn_abrir_pcp.setObjectName("PCP")
        self.btn_abrir_pcp.clicked.connect(self.abrir_modulo_pcp)
        self.btn_abrir_pcp.setMinimumWidth(100)

        self.btn_abrir_compras = QPushButton("Compras", self)
        self.btn_abrir_compras.setObjectName("compras")
        self.btn_abrir_compras.clicked.connect(self.abrir_modulo_compras)
        self.btn_abrir_compras.setMinimumWidth(100)

        self.btn_consultar_estrutura = QPushButton("Consultar Estrutura", self)
        self.btn_consultar_estrutura.clicked.connect(lambda: executar_consulta_estrutura(self, self.tree))
        self.btn_consultar_estrutura.setMinimumWidth(150)
        self.btn_consultar_estrutura.setEnabled(False)

        self.btn_onde_e_usado = QPushButton("Onde é usado?", self)
        self.btn_onde_e_usado.clicked.connect(lambda: executar_consulta_onde_usado(self, self.tree))
        self.btn_onde_e_usado.setMinimumWidth(150)
        self.btn_onde_e_usado.setEnabled(False)

        self.btn_saldo_estoque = QPushButton("Saldos em Estoque", self)
        self.btn_saldo_estoque.clicked.connect(lambda: executar_saldo_em_estoque(self, self.tree))
        self.btn_saldo_estoque.setMinimumWidth(150)
        self.btn_saldo_estoque.setEnabled(False)

        self.btn_limpar = QPushButton("Limpar", self)
        self.btn_limpar.clicked.connect(self.limpar_campos)
        self.btn_limpar.setMinimumWidth(100)

        self.btn_nova_janela = QPushButton("Nova Janela", self)
        self.btn_nova_janela.clicked.connect(lambda: abrir_nova_janela(self, EngenhariaApp()))
        self.btn_nova_janela.setMinimumWidth(100)

        self.btn_abrir_desenho = QPushButton("Abrir Desenho", self)
        self.btn_abrir_desenho.clicked.connect(lambda: abrir_desenho(self, self.tree))
        self.btn_abrir_desenho.setMinimumWidth(100)

        self.btn_exportar_excel = QPushButton("Exportar Excel", self)
        self.btn_exportar_excel.clicked.connect(lambda: exportar_excel(self, self.tree))
        self.btn_exportar_excel.setMinimumWidth(100)
        self.btn_exportar_excel.setEnabled(False)  # Desativar inicialmente

        self.btn_calculo_peso = QPushButton("Tabela de pesos", self)
        self.btn_calculo_peso.clicked.connect(abrir_tabela_pesos)
        self.btn_calculo_peso.setMinimumWidth(100)

        self.btn_fechar = QPushButton("Fechar", self)
        self.btn_fechar.clicked.connect(self.fechar_janela)
        self.btn_fechar.setMinimumWidth(100)

        layout = QVBoxLayout()
        layout_campos_01 = QHBoxLayout()
        layout_campos_02 = QHBoxLayout()
        layout_button_03 = QHBoxLayout()
        layout_button_04 = QHBoxLayout()
        self.layout_footer_label = QHBoxLayout()
        layout_footer_logo = QHBoxLayout()

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
        layout_campos_02.addWidget(self.combobox_armazem)
        layout_campos_02.addWidget(QLabel("Grupo:"))
        layout_campos_02.addWidget(self.campo_grupo)
        layout_campos_02.addWidget(self.checkbox_bloqueado)

        layout_button_03.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout_button_03.addWidget(self.btn_consultar)
        layout_button_03.addWidget(self.btn_consultar_estrutura)
        layout_button_03.addWidget(self.btn_onde_e_usado)
        layout_button_03.addWidget(self.btn_saldo_estoque)
        layout_button_03.addWidget(self.btn_limpar)
        layout_button_03.addWidget(self.btn_nova_janela)
        layout_button_03.addWidget(self.btn_abrir_desenho)
        layout_button_03.addWidget(self.btn_exportar_excel)
        layout_button_03.addWidget(self.btn_calculo_peso)
        layout_button_03.addWidget(self.btn_abrir_pcp)
        layout_button_03.addWidget(self.btn_abrir_compras)
        layout_button_03.addWidget(self.btn_fechar)
        layout_button_03.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.layout_footer_label.addStretch(1)
        self.layout_footer_label.addWidget(self.label_line_number)
        self.layout_footer_label.addStretch(1)

        layout_footer_logo.addWidget(self.logo_label)

        layout.addLayout(layout_campos_01)
        layout.addLayout(layout_campos_02)
        layout.addLayout(layout_button_03)
        layout.addLayout(layout_button_04)
        layout.addWidget(self.tree)
        layout.addLayout(self.layout_footer_label)
        layout.addLayout(layout_footer_logo)
        self.setLayout(layout)

        self.campo_codigo.returnPressed.connect(self.executar_consulta)
        self.campo_descricao.returnPressed.connect(self.executar_consulta)
        self.campo_contem_descricao.returnPressed.connect(self.executar_consulta)
        self.campo_tipo.returnPressed.connect(self.executar_consulta)
        self.campo_um.returnPressed.connect(self.executar_consulta)
        self.campo_grupo.returnPressed.connect(self.executar_consulta)

        self.setStyleSheet("""
            * {
                background-color: #363636;
            }

            QLabel, QCheckBox {
                color: #EEEEEE;
                font-size: 11px;
                font-weight: bold;
            }
            
            QLabel#logo-enaplic {
                margin: 5px 0;
            }
            
            QLabel#label-line-number {
                font-size: 16px;
                font-weight: normal;
            }

            QLineEdit {
                background-color: #DFE0E2;
                border: 1px solid #262626;
                padding: 5px;
                border-radius: 8px;
            }
            
            QDateEdit, QComboBox {
                background-color: #DFE0E2;
                border: 1px solid #262626;
                padding: 5px 10px;
                border-radius: 10px;
                height: 20px;
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

            QPushButton {
                background-color: #0a79f8;
                color: #fff;
                padding: 5px 15px;
                border: 2px;
                border-radius: 8px;
                font-size: 11px;
                height: 20px;
                font-weight: bold;
                margin: 10px 5px;
            }

            QPushButton#PCP, QPushButton#compras {
                background-color: #DC5F00;
            }

            QPushButton#compras {
                background-color: #836FFF;
            }

            QPushButton:hover, QPushButton#PCP:hover, QPushButton#compras:hover {
                background-color: #fff;
                color: #0a79f8
            }

            QPushButton:pressed, QPushButton#PCP:pressed, QPushButton#compras:pressed {
                background-color: #6703c5;
                color: #fff;
            }

            QTableWidget {
                border: 1px solid #000000;
                background-color: #686D76;
                padding-left: 10px;
                margin-bottom: 15px;
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
                """)

    def abrir_modulo_pcp(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, 'pcp_model.pyw')
        self.process.start("python", [script_path])

    def abrir_modulo_compras(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, 'compras_model.pyw')
        self.process.start("python", [script_path])

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
        self.tree.horizontalHeader().setStretchLastSection(True)
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

            context_menu_abrir_desenho = QAction('Abrir desenho', self)
            context_menu_abrir_desenho.triggered.connect(lambda: abrir_desenho(self, table))

            context_menu_consultar_estrutura = QAction('Consultar estrutura', self)
            context_menu_consultar_estrutura.triggered.connect(lambda: executar_consulta_estrutura(self, table))

            context_menu_consultar_onde_usado = QAction('Onde é usado?', self)
            context_menu_consultar_onde_usado.triggered.connect(lambda: executar_consulta_onde_usado(self, table))

            context_menu_saldo_estoque = QAction('Saldo em estoque', self)
            context_menu_saldo_estoque.triggered.connect(lambda: executar_saldo_em_estoque(self, table))

            context_menu_nova_janela = QAction('Nova janela', self)
            context_menu_nova_janela.triggered.connect(lambda: abrir_nova_janela(self, EngenhariaApp()))

            menu.addAction(context_menu_abrir_desenho)
            menu.addAction(context_menu_consultar_estrutura)
            menu.addAction(context_menu_consultar_onde_usado)
            menu.addAction(context_menu_saldo_estoque)
            menu.addAction(context_menu_nova_janela)

            menu.exec_(table.viewport().mapToGlobal(position))

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

    def limpar_campos(self):
        # Limpar os dados dos campos
        self.campo_codigo.clear()
        self.campo_descricao.clear()
        self.campo_contem_descricao.clear()
        self.campo_tipo.clear()
        self.campo_um.clear()
        self.combobox_armazem.clear()
        self.campo_grupo.clear()
        self.checkbox_bloqueado.setChecked(False)
        self.tree.setColumnCount(0)
        self.tree.setRowCount(0)
        self.label_line_number.hide()

    def controle_campos_formulario(self, status):
        self.campo_codigo.setEnabled(status)
        self.campo_descricao.setEnabled(status)
        self.campo_contem_descricao.setEnabled(status)
        self.campo_tipo.setEnabled(status)
        self.campo_um.setEnabled(status)
        self.combobox_armazem.setEnabled(status)
        self.campo_grupo.setEnabled(status)
        self.btn_consultar.setEnabled(status)
        self.btn_exportar_excel.setEnabled(status)
        self.btn_consultar_estrutura.setEnabled(status)
        self.btn_onde_e_usado.setEnabled(status)
        self.btn_saldo_estoque.setEnabled(status)

    def query_consulta_tabela_produtos(self):

        codigo = self.campo_codigo.text().upper().strip()
        descricao = self.campo_descricao.text().upper().strip()
        descricao2 = self.campo_contem_descricao.text().upper().strip()
        tipo = self.campo_tipo.text().upper().strip()
        um = self.campo_um.text().upper().strip()
        armazem = self.combobox_armazem.currentData()
        grupo = self.campo_grupo.text().upper().strip()
        status_checkbox = self.checkbox_bloqueado.isChecked()

        armazem = armazem if armazem is not None else ''

        lista_campos = [codigo, descricao, descricao2, tipo, um, armazem, grupo]

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

        # Montar a query com base no status do checkbox
        status_bloqueado = '1' if status_checkbox else ''
        status_clause = f"AND B1_MSBLQL = '{status_bloqueado}'" if status_checkbox else ''

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
            {database}.dbo.SB1010
        WHERE 
            B1_COD LIKE '{codigo}%' 
            AND B1_DESC LIKE '{descricao}%' 
            AND {descricao2_clauses}
            AND B1_TIPO LIKE '{tipo}%' 
            AND B1_UM LIKE '{um}%' 
            AND B1_LOCPAD LIKE '{armazem}%' 
            AND B1_GRUPO LIKE '{grupo}%' {status_clause}
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

        conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        self.engine = create_engine(f'mssql+pyodbc:///?odbc_connect={conn_str}')

        try:
            dataframe_line_number = pd.read_sql(query_contagem_linhas, self.engine)
            line_number = dataframe_line_number.iloc[0, 0]
            dataframe = pd.read_sql(query_consulta, self.engine)
            dataframe[''] = ''

            if not dataframe.empty:

                if line_number > 1:
                    message = f"Foram encontrados {line_number} resultados"
                else:
                    message = f"Foi encontrado {line_number} resultado"

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
                exibir_mensagem("EUREKA® engenharia", 'Nada encontrado!', "info")
                self.controle_campos_formulario(True)
                return

            # Preencher a tabela com os resultados
            for i, row in dataframe.iterrows():

                self.tree.setSortingEnabled(False)  # Permitir ordenação
                # Inserir os valores formatados na tabela
                self.tree.insertRow(i)
                for j, value in enumerate(row):
                    if j == 9:  # Verifica se o valor é da coluna B1_MSBLQL
                        # Converte o valor 1 para 'Sim' e 2 para 'Não'
                        if value == '1':
                            value = 'Sim'
                        else:
                            value = 'Não'
                    elif j == 11 or j == 12:
                        if not value.isspace():
                            data_obj = datetime.strptime(value, "%Y%m%d")
                            value = data_obj.strftime("%d/%m/%Y")

                    item = QTableWidgetItem(str(value).strip())

                    if j != 0 and j != 1:
                        item.setTextAlignment(Qt.AlignCenter)

                    self.tree.setItem(i, j, item)

                # Permitir que a interface gráfica seja atualizada
                # QCoreApplication.processEvents()

            self.tree.setSortingEnabled(True)  # Permitir ordenação

            self.controle_campos_formulario(True)

        except pyodbc.Error as ex:
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EngenhariaApp()
    username, password, database, server = setup_mssql()
    driver = '{SQL Server}'

    window.showMaximized()
    sys.exit(app.exec_())
