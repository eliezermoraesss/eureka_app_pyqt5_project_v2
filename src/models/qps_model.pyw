import locale
import os
import sys

# Caminho absoluto para o diretório onde o módulo src está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pandas as pd
import requests
from PyQt5.QtCore import Qt, QProcess, pyqtSignal, QEvent, QThread
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QTableWidget, QTableWidgetItem, QHeaderView, QStyle, QAction, QLabel, QSizePolicy, QMenu, QFrame, \
    QCalendarWidget
from sqlalchemy import create_engine, text

from src.app.utils.db_mssql import setup_mssql
from src.app.utils.utils import exibir_mensagem, copiar_linha, exportar_excel
from src.app.utils.load_session import load_session


class UpdateTableThread(QThread):
    update_complete = pyqtSignal(bool, str)

    def __init__(self, url, method='POST', parent=None):
        super().__init__(parent)
        self.url = url
        self.method = method

    def run(self):
        try:
            if self.method.upper() == 'POST':
                response = requests.post(self.url)
            else:
                raise ValueError(f"Método HTTP não suportado: {self.method}")

            if response.status_code == 201:
                self.update_complete.emit(True, "A tabela foi atualizada com sucesso!")
            else:
                self.update_complete.emit(False,
                                          f"Erro ao atualizar a tabela. Código de status: {response.status_code}")
        except Exception as e:
            self.update_complete.emit(False, f"Erro ao enviar a requisição: {str(e)}")


class QpClosedApp(QWidget):
    guia_fechada = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        user_data = load_session()
        username = user_data["username"]
        role = user_data["role"]
        self.username, self.password, self.database, self.server = setup_mssql()
        self.driver = '{SQL Server}'

        self.setWindowTitle(f"Eureka® QPS . {username} ({role})")
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

        self.update_thread = None
        self.engine = None
        self.status_atualizacao = False
        self.tree = QTableWidget(self)
        self.tree.setColumnCount(0)
        self.tree.setRowCount(0)
        self.process = QProcess(self)
        self.nova_janela = None

        self.altura_linha = 30
        self.tamanho_fonte_tabela = 10

        self.fonte_tabela = 'Segoe UI'
        fonte_campos = "Segoe UI"
        tamanho_fonte_campos = 16

        self.setStyleSheet("""
            * {
                background-color: #222831;
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

            QLineEdit {
                background-color: #EEEEEE;
                border: 1px solid #262626;
                padding: 5px 10px;
                border-radius: 10px;
                height: 24px;
                font-size: 16px;
            }

            QPushButton {
                background-color: #00ADB5;
                color: #EEEEEE;
                padding: 5px 10px;
                border: 2px;
                border-radius: 8px;
                font-size: 11px;
                height: 20px;
                font-weight: bold;
                margin: 10px 5px;
            }
            
            QPushButton#btn_home {
                background-color: #c1121f;
            }
            
            QPushButton#btn_qps_finalizadas {
                background-color: #C5EBAA;
                color: #294B29;
            }
            
            QPushButton#btn_qps_abertas {
                background-color: #FFC94A;
                color: #3E3232;
            }
            
            QPushButton#btn_qps {
                background-color: #6EACDA;
                color: #021526;
            }
            
            QPushButton#btn_atualizar_qp {
                background-color: #3F72AF;
            }

            QPushButton:hover, QPushButton:hover#btn_qps_finalizadas, QPushButton:hover#btn_qps_abertas, 
            QPushButton:hover#btn_qps, QPushButton:hover#btn_atualizar_qp, QPushButton:hover#btn_home { background-color: #E84545; color: #fff }
    
            QPushButton:pressed, QPushButton:pressed#btn_qps_finalizadas, QPushButton:pressed#btn_qps_abertas, 
            QPushButton:pressed#btn_qps, QPushButton:pressed#btn_atualizar_qp, QPushButton:pressed#btn_home { background-color: #6703c5; color: #fff; }

            QTableWidget {
                border: 1px solid #000000;
                background-color: #393E46;
                padding-left: 10px;
                margin: 5px 0;
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
                background-color: #393E46;
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

        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_enaplic_path = os.path.join(script_dir, '..', 'resources', 'images', 'LOGO.jpeg')
        self.logo_label = QLabel(self)
        self.logo_label.setObjectName('logo-enaplic')
        pixmap_logo = QPixmap(logo_enaplic_path).scaledToWidth(50)
        self.logo_label.setPixmap(pixmap_logo)
        self.logo_label.setAlignment(Qt.AlignRight)

        self.label_title = QLabel("GESTÃO DE QPS", self)
        self.label_title.setObjectName('label-title')

        self.line = QFrame(self)
        self.line.setObjectName('line')
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.label_descricao_prod = QLabel("Descrição:", self)
        self.label_contem_descricao_prod = QLabel("Contém na descrição:", self)
        self.label_contem_descricao_prod.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_qp = QLabel("QP:", self)
        self.label_line_number = QLabel("", self)
        self.label_line_number.setVisible(False)

        self.campo_descricao_prod = QLineEdit(self)
        self.campo_descricao_prod.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_descricao_prod.setMaxLength(60)
        self.campo_descricao_prod.setFixedWidth(400)
        self.add_clear_button(self.campo_descricao_prod)
        self.campo_descricao_prod.returnPressed.connect(lambda: self.consultar_qps('T'))

        self.campo_contem_descricao_prod = QLineEdit(self)
        self.campo_contem_descricao_prod.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_contem_descricao_prod.setMaxLength(60)
        self.campo_contem_descricao_prod.setFixedWidth(400)
        self.add_clear_button(self.campo_contem_descricao_prod)
        self.campo_contem_descricao_prod.returnPressed.connect(lambda: self.consultar_qps('T'))

        self.campo_qp = QLineEdit(self)
        self.campo_qp.setFont(QFont(fonte_campos, tamanho_fonte_campos))
        self.campo_qp.setMaxLength(6)
        self.campo_qp.setFixedWidth(110)
        self.add_clear_button(self.campo_qp)
        self.campo_qp.returnPressed.connect(lambda: self.consultar_qps('T'))

        self.btn_qps = QPushButton("Pesquisar", self)
        self.btn_qps.clicked.connect(lambda: self.consultar_qps('T'))
        self.btn_qps.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.btn_qps.setObjectName("btn_qps")

        self.btn_qps_finalizadas = QPushButton("Concluídas", self)
        self.btn_qps_finalizadas.clicked.connect(lambda: self.consultar_qps('F'))
        self.btn_qps_finalizadas.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.btn_qps_finalizadas.setObjectName("btn_qps_finalizadas")

        self.btn_qps_abertas = QPushButton("Em aberto", self)
        self.btn_qps_abertas.clicked.connect(lambda: self.consultar_qps('A'))
        self.btn_qps_abertas.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.btn_qps_abertas.setObjectName("btn_qps_abertas")

        self.btn_atualizar_qp = QPushButton("Atualizar", self)
        self.btn_atualizar_qp.clicked.connect(lambda: self.atualizar_tabela('open'))
        self.btn_atualizar_qp.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.btn_atualizar_qp.hide()
        self.btn_atualizar_qp.setObjectName("btn_atualizar_qp")

        self.btn_exportar_excel = QPushButton("Exportar Excel", self)
        self.btn_exportar_excel.clicked.connect(lambda: exportar_excel(self, self.tree))
        self.btn_exportar_excel.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.btn_exportar_excel.setEnabled(False)

        self.btn_limpar = QPushButton("Limpar", self)
        self.btn_limpar.clicked.connect(self.limpar_campos)
        self.btn_limpar.setFixedWidth(110)

        self.btn_fechar = QPushButton("Fechar", self)
        self.btn_fechar.clicked.connect(self.fechar_janela)
        self.btn_fechar.setFixedWidth(110)

        self.btn_home = QPushButton("HOME", self)
        self.btn_home.setObjectName("btn_home")
        self.btn_home.clicked.connect(self.return_to_main)
        self.btn_home.setFixedWidth(110)

        self.calendar = QCalendarWidget(self)
        self.calendar.setFixedSize(350, 200)
        self.calendar.setGridVisible(True)
        self.calendar.hide()
        self.calendar.clicked.connect(self.date_selected)

        self.tree.cellDoubleClicked.connect(self.cell_clicked_open_calendar)
        self.selected_row = None
        self.selected_column = None
        self.tree.installEventFilter(self)
        self.installEventFilter(self)

        layout = QVBoxLayout()
        layout_title = QHBoxLayout()
        layout_campos_01 = QHBoxLayout()
        self.layout_buttons = QHBoxLayout()
        self.layout_footer_label = QHBoxLayout()

        layout_title.addStretch(1)
        layout_title.addWidget(self.logo_label)
        layout_title.addWidget(self.label_title)
        layout_title.addStretch(1)

        container_descricao_prod = QVBoxLayout()
        container_descricao_prod.addWidget(self.label_descricao_prod)
        container_descricao_prod.addWidget(self.campo_descricao_prod)

        container_contem_descricao_prod = QVBoxLayout()
        container_contem_descricao_prod.addWidget(self.label_contem_descricao_prod)
        container_contem_descricao_prod.addWidget(self.campo_contem_descricao_prod)

        container_qp = QVBoxLayout()
        container_qp.addWidget(self.label_qp)
        container_qp.addWidget(self.campo_qp)

        layout_campos_01.addLayout(container_qp)
        layout_campos_01.addLayout(container_descricao_prod)
        layout_campos_01.addLayout(container_contem_descricao_prod)
        layout_campos_01.addStretch()

        self.layout_buttons.addWidget(self.btn_qps)
        self.layout_buttons.addWidget(self.btn_qps_finalizadas)
        self.layout_buttons.addWidget(self.btn_qps_abertas)
        self.layout_buttons.addWidget(self.btn_atualizar_qp)
        self.layout_buttons.addWidget(self.btn_exportar_excel)
        self.layout_buttons.addWidget(self.btn_limpar)
        self.layout_buttons.addWidget(self.btn_fechar)
        self.layout_buttons.addWidget(self.btn_home)
        self.layout_buttons.addStretch()

        self.layout_footer_label.addStretch(1)
        self.layout_footer_label.addWidget(self.label_line_number)
        self.layout_footer_label.addStretch(1)

        layout.addLayout(layout_title)
        layout.addWidget(self.line)
        layout.addLayout(layout_campos_01)
        layout.addLayout(self.layout_buttons)
        layout.addWidget(self.tree)
        layout.addLayout(self.layout_footer_label)
        self.setLayout(layout)

        self.consultar_qps('T')

    def return_to_main(self):
        self.close()  # Fecha a janela atual
        self.main_window.reopen()  # Reabre ou traz a janela principal ao foco

    def abrir_nova_janela(self):
        eng_window = QpClosedApp(self.main_window)
        eng_window.showMaximized()
        self.main_window.sub_windows.append(eng_window)

    def atualizar_tabela(self, tipo_qp):
        exibir_mensagem("Atualização em andamento",
                        "A atualização está em andamento e demorará cerca de 5 minutos.",
                        "info")
        self.btn_atualizar_qp.hide()

        if tipo_qp == 'closed':
            url = "http://192.175.175.41:5000/indicators/save?qp=closed"
        elif tipo_qp == 'open':
            url = "http://192.175.175.41:5000/indicators/save?qp=open"
        else:
            exibir_mensagem("Erro", "Status de QP não suportado!", "error")
            self.btn_atualizar_qp.show()
            return

        self.status_atualizacao = True
        self.update_thread = UpdateTableThread(url)
        self.update_thread.update_complete.connect(self.on_update_complete)
        self.update_thread.start()

    def on_update_complete(self, success, message):
        self.status_atualizacao = False
        self.btn_atualizar_qp.show()
        if success:
            exibir_mensagem("Atualização concluída", message, "info")
        else:
            exibir_mensagem("Erro na atualização", message, "error")

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
            context_menu_nova_janela = QAction('Nova janela', self)
            context_menu_nova_janela.triggered.connect(self.abrir_nova_janela)
            menu.addAction(context_menu_nova_janela)
            menu.exec_(table.viewport().mapToGlobal(position))

    def limpar_campos(self):
        self.campo_qp.clear()
        self.campo_descricao_prod.clear()
        self.campo_contem_descricao_prod.clear()
        self.tree.setColumnCount(0)
        self.tree.setRowCount(0)
        self.label_line_number.hide()
        self.btn_atualizar_qp.hide()

    def add_clear_button(self, line_edit):
        clear_icon = self.style().standardIcon(QStyle.SP_LineEditClearButton)
        pixmap = clear_icon.pixmap(40, 40)  # Redimensionar o ícone para 20x20 pixels
        larger_clear_icon = QIcon(pixmap)
        clear_action = QAction(larger_clear_icon, "Clear", line_edit)
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
        self.tree.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
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

    def controle_ativacao_de_objetos(self, status):
        self.campo_qp.setEnabled(status)
        self.btn_exportar_excel.setEnabled(status)

    def fechar_janela(self):
        self.close()
        
    def configurar_tabela_tooltips(self, dataframe, status_qp):
        # Mapa de tooltips correspondentes às colunas da consulta SQL
        tooltip_map = {
            "STATUS QP": "FINALIZADO\nQP localizada na pasta QP CONCLUÍDA no Sharepoint\n\nABERTO\nQP localizada na pasta QP ABERTA no Sharepoint",
            "SALDO (EM DIAS)": "1. Se a data de entrega estiver vazia:\nSALDO (EM DIAS) = (PRAZO DE ENTREGA) - (DATA DE HOJE)\n\n2. Se a data de entrega NÃO estiver vazia:\nSALDO (EM DIAS) = (PRAZO DE ENTREGA) - (DATA DE ENTREGA)",
            "DATA DE EMISSÃO": "Data de abertura da QP\nrealizada pela ENGENHARIA",
            "PRAZO DE ENTREGA": "Data do prazo de entrega\nindicada na OFERTA enviada pelo COMERCIAL",
            "DATA DE ENTREGA": "Data do envio do último produto manufaturado\npertencente a QP que indica sua conclusão.\nDeve ser preenchida pelo PCP"
        }
        
        if status_qp == 'A':
            tooltip_map['SALDO (EM DIAS)'] = 'SALDO (EM DIAS) = (PRAZO DE ENTREGA) - (DATA DE HOJE))'
            tooltip_map['STATUS QP'] = 'ABERTO\nQP localizada na pasta QP ABERTA no Sharepoint'
            del tooltip_map['DATA DE ENTREGA']
        elif status_qp == 'F':
            tooltip_map['STATUS QP'] = 'FINALIZADO\nQP localizada na pasta QP CONCLUÍDA no Sharepoint'

        # Obtenha os cabeçalhos das colunas do dataframe
        headers = dataframe.columns

        # Adicione os cabeçalhos e os tooltips
        for i, header in enumerate(headers):
            item = QTableWidgetItem(header)
            tooltip = tooltip_map.get(header)
            item.setToolTip(tooltip)
            self.tree.setHorizontalHeaderItem(i, item)

    def query_consulta_qps(self, status_qp):
        numero_qp = self.campo_qp.text().upper().strip()
        descricao = self.campo_descricao_prod.text().upper().strip()
        contem_descricao = self.campo_contem_descricao_prod.text().upper().strip()

        palavras_contem_descricao = contem_descricao.split('*')
        clausulas_contem_descricao = " AND ".join(
            [f"des_qp LIKE '%{palavra}%'" for palavra in palavras_contem_descricao])

        query = f"""
            SELECT
                cod_qp AS "QP",
                des_qp AS "NOME DO PROJETO",
                status_qp AS "STATUS QP",
                dt_open_qp AS "DATA DE EMISSÃO",
                dt_end_qp AS "PRAZO DE ENTREGA",
                dt_completed_qp AS "DATA DE ENTREGA",
                vl_delay AS "SALDO (EM DIAS)",
                status_delivery AS "STATUS ENTREGA"
            FROM 
                enaplic_management.dbo.tb_qps
            WHERE
                cod_qp LIKE '%{numero_qp}%'
                AND des_qp LIKE '{descricao}%'
                AND {clausulas_contem_descricao}
                AND status_qp = '{status_qp}'
                ORDER BY cod_qp DESC
            """

        return query if status_qp in ('F', 'A') else query.replace("AND status_qp = 'T'", '')

    def consultar_qps(self, status_qp):
        query = self.query_consulta_qps(status_qp)
        line_number = f"""
            SELECT
                COUNT(*) AS count
            FROM ({query.replace("ORDER BY cod_qp DESC", "")}) AS results
        """

        conn_str = f'DRIVER={self.driver};SERVER={self.server};UID={self.username};PWD={self.password}'
        self.engine = create_engine(f'mssql+pyodbc:///?odbc_connect={conn_str}')

        try:
            dataframe_line_number = pd.read_sql(line_number, self.engine)
            line_number = dataframe_line_number.iloc[0, 0]

            if line_number >= 1:
                if line_number > 1:
                    message = f"Foram encontrados {line_number} resultados"
                else:
                    message = f"Foi encontrado {line_number} resultado"

                self.label_line_number.setText(f"{message}")
                self.label_line_number.show()

            else:
                exibir_mensagem("EUREKA® PCP", 'Nenhuma QP encontrada!', "info")
                self.controle_ativacao_de_objetos(True)
                return

            dataframe = pd.read_sql(query, self.engine)
            dataframe.insert(0, '', '')
            dataframe = dataframe.drop('DATA DE ENTREGA', axis=1) if status_qp == 'A' else dataframe
            dataframe[''] = ''

            self.configurar_tabela(dataframe)
            self.configurar_tabela_tooltips(dataframe, status_qp)
            self.tree.setRowCount(0)

            # Construir caminhos relativos
            script_dir = os.path.dirname(os.path.abspath(__file__))
            open_icon_path = os.path.join(script_dir, '..', 'resources', 'images', 'red.png')
            closed_icon_path = os.path.join(script_dir, '..', 'resources', 'images', 'green.png')

            open_icon = QIcon(open_icon_path)
            closed_icon = QIcon(closed_icon_path)

            for i, row in dataframe.iterrows():

                self.tree.setSortingEnabled(False)
                self.tree.insertRow(i)
                for j, value in enumerate(row):
                    if value is not None:
                        if j == 0:
                            item = QTableWidgetItem()
                            if row['STATUS QP'] == 'A':
                                item.setIcon(open_icon)
                            elif row['STATUS QP'] == 'F':
                                item.setIcon(closed_icon)
                            item.setTextAlignment(Qt.AlignCenter)
                        else:
                            if j == 1:
                                value = str(value).lstrip('0')
                            if j == 3:
                                value = 'FINALIZADO' if value == 'F' else 'ABERTO'
                            item = QTableWidgetItem(str(value).strip())
                            if j != 2:
                                item.setTextAlignment(Qt.AlignCenter)
                    else:
                        item = QTableWidgetItem('')

                    self.tree.setItem(i, j, item)

            self.tree.setSortingEnabled(True)
            self.controle_ativacao_de_objetos(True)
            if not self.status_atualizacao:
                self.btn_atualizar_qp.show()
            else:
                self.btn_atualizar_qp.hide()

        except Exception as ex:
            exibir_mensagem('Erro ao consultar tabela', f'Erro: {str(ex)}', 'error')

        finally:
            # Fecha a conexão com o banco de dados se estiver aberta
            if hasattr(self, 'engine'):
                self.engine.dispose()
                self.engine = None

    def cell_clicked_open_calendar(self, row, column):
        if self.tree.horizontalHeaderItem(column).text() == "DATA DE ENTREGA":
            self.selected_row = row
            self.selected_column = column
            status_qp = self.tree.item(self.selected_row, 3).text()
            if status_qp == "FINALIZADO":
                self.calendar.setGeometry(self.tree.visualItemRect(self.tree.item(row, column)))
                self.calendar.show()
        else:
            self.calendar.hide()

    def date_selected(self, date):
        if self.selected_row is not None:
            date_str = date.toString("dd/MM/yyyy")
            cod_qp = self.tree.item(self.selected_row, 1).text().zfill(6)  # Assuming QP is in the second column

            update_query = text("""
                UPDATE enaplic_management.dbo.tb_qps
                SET dt_completed_qp = :selected_date
                WHERE cod_qp = :cod_qp
            """)

            try:
                conn_str = f'DRIVER={self.driver};SERVER={self.server};UID={self.username};PWD={self.password}'
                self.engine = create_engine(f'mssql+pyodbc:///?odbc_connect={conn_str}')

                with self.engine.begin() as connection:
                    connection.execute(update_query, {'selected_date': date_str, 'cod_qp': cod_qp})

                item = QTableWidgetItem(date_str)
                item.setTextAlignment(Qt.AlignCenter)
                self.tree.setItem(self.selected_row, self.selected_column, item)
                self.calendar.hide()
            except Exception as ex:
                exibir_mensagem('Erro ao atualizar tabela', f'Erro: {str(ex)}', 'error')

    def eventFilter(self, obj, event):
        if obj == self.tree:
            if event.type() == QEvent.MouseButtonRelease or event.type() == QEvent.KeyPress:
                if self.calendar.isVisible():
                    self.calendar.hide()
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.calendar.isVisible():
            self.calendar.hide()
        elif event.key() == Qt.Key_Delete:
            current_item = self.tree.currentItem()
            if current_item is not None or current_item != '':
                current_row = self.tree.currentRow()
                current_column = self.tree.currentColumn()
                if self.tree.horizontalHeaderItem(current_column).text() == "DATA DE ENTREGA":
                    cell_value = current_item.text()
                    status_qp = self.tree.item(current_row, 3).text()
                    if cell_value and status_qp == 'FINALIZADO':
                        cod_qp = self.tree.item(current_row, 1).text().zfill(6)

                        update_query = text("""
                            UPDATE enaplic_management.dbo.tb_qps
                            SET dt_completed_qp = ''
                            WHERE cod_qp = :cod_qp
                        """)

                        try:
                            conn_str = f'DRIVER={self.driver};SERVER={self.server};UID={self.username};PWD={self.password}'
                            self.engine = create_engine(f'mssql+pyodbc:///?odbc_connect={conn_str}')

                            with self.engine.begin() as connection:
                                connection.execute(update_query, {'cod_qp': cod_qp})
                            self.tree.setItem(current_row, current_column, QTableWidgetItem(''))
                        except Exception as ex:
                            exibir_mensagem('Erro ao remover data da tabela', f'Erro: {str(ex)}', 'error')
