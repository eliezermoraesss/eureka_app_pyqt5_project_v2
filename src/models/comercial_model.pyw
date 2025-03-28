import io
import locale
import os
import sys

# Caminho absoluto para o diretório onde o módulo src está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from datetime import datetime

import pandas as pd
import pyodbc
import xlwings as xw
from PyPDF2 import PdfReader
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QStyle, QAction, QSizePolicy
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from sqlalchemy import create_engine

from src.app.utils.db_mssql import setup_mssql
from src.app.utils.utils import exibir_mensagem, copiar_linha, obter_dados_tabela, abrir_desenho
from src.app.utils.load_session import load_session
from src.dialog.loading_dialog import loading_dialog
from src.app.utils.autocomplete_feature import AutoCompleteManager
from src.app.utils.search_history_manager import SearchHistoryManager
from src.resources.styles.qss_comercial import comercial_qss


def query_consulta(codigo):

    query = f"""
    DECLARE @CodigoPai VARCHAR(50) = '{codigo}';

    -- CTE para selecionar as revisões máximas
    WITH MaxRevisoes AS (
        SELECT
            G1_COD,
            MAX(G1_REVFIM) AS MaxRevisao
        FROM
            SG1010
        WHERE
            G1_REVFIM <> 'ZZZ'
            AND D_E_L_E_T_ <> '*'
        GROUP BY
            G1_COD
    ),
    -- CTE para selecionar os itens pai e seus subitens recursivamente
    ListMP AS (
        -- Selecionar o item pai inicialmente
        SELECT
            G1.G1_COD AS "CÓDIGO",
            G1.G1_COMP AS "COMPONENTE",
            G1.G1_QUANT AS "QUANTIDADE",
            0 AS Nivel,
            G1.G1_REVFIM AS "REVISAO"
        FROM
            SG1010 G1
        INNER JOIN MaxRevisoes MR ON G1.G1_COD = MR.G1_COD AND G1.G1_REVFIM = MR.MaxRevisao
        WHERE
            G1.G1_COD = @CodigoPai
            AND G1.G1_REVFIM <> 'ZZZ'
            AND G1.D_E_L_E_T_ <> '*'
        UNION ALL
        -- Selecione os subitens de cada item pai e multiplique as quantidades
        SELECT
            filho.G1_COD,
            filho.G1_COMP,
            filho.G1_QUANT * pai.QUANTIDADE,
            pai.Nivel + 1,
            filho.G1_REVFIM
        FROM
            SG1010 AS filho
        INNER JOIN ListMP AS pai ON
            filho.G1_COD = pai."COMPONENTE"
        INNER JOIN MaxRevisoes MR ON filho.G1_COD = MR.G1_COD AND filho.G1_REVFIM = MR.MaxRevisao
        WHERE
            pai.Nivel < 100
            -- Defina o limite máximo de recursão aqui
            AND filho.G1_REVFIM <> 'ZZZ'
            AND filho.D_E_L_E_T_ <> '*'
    )
    -- Selecionar os componentes, somar as quantidades e evitar componentes duplicados
    SELECT 
        "COMPONENTE" AS "CÓDIGO",
        prod.B1_DESC AS "DESCRIÇÃO",
        SUM("QUANTIDADE") AS "QUANT.",
        prod.B1_UM AS "UNID. MED.", 
        prod.B1_UCOM AS "ULT. ATUALIZ.",
        prod.B1_TIPO AS "TIPO", 
        prod.B1_LOCPAD AS "ARMAZÉM", 
        prod.B1_UPRC AS "VALOR UNIT. (R$)",
        SUM("QUANTIDADE" * prod.B1_UPRC) AS "SUB-TOTAL (R$)"
    FROM 
        ListMP AS listMP
    INNER JOIN 
        SB1010 AS prod ON listMP."COMPONENTE" = prod.B1_COD
    WHERE 
        prod.B1_TIPO = 'MP'
        AND prod.B1_LOCPAD IN ('01', '03', '11', '12', '97')
        AND prod.D_E_L_E_T_ <> '*'
    GROUP BY 
        "COMPONENTE",
        prod.B1_DESC,
        prod.B1_UM,
        prod.B1_UCOM,
        prod.B1_TIPO,
        prod.B1_LOCPAD,
        prod.B1_UPRC
    ORDER BY 
        "COMPONENTE" ASC;
    """
    return query

def query_pesquisa_fiscal(codigo):

    query = f"""
    DECLARE @CodigoPai VARCHAR(50) = '{codigo}';
    -- CTE para selecionar as revisões máximas
    WITH MaxRevisoes AS (
        SELECT G1_COD, MAX(G1_REVFIM) AS MaxRevisao
        FROM SG1010
        WHERE G1_REVFIM <> 'ZZZ' AND D_E_L_E_T_ <> '*'
        GROUP BY G1_COD
    ),
    -- CTE para selecionar os itens pai e seus subitens recursivamente
    ListMP AS (
        SELECT G1.G1_COD AS "CÓDIGO", G1.G1_COMP AS "COMPONENTE", G1.G1_QUANT AS "QUANTIDADE", 0 AS Nivel, G1.G1_REVFIM AS "REVISAO"
        FROM SG1010 G1
        INNER JOIN MaxRevisoes MR ON G1.G1_COD = MR.G1_COD AND G1.G1_REVFIM = MR.MaxRevisao
        WHERE G1.G1_COD = @CodigoPai AND G1.G1_REVFIM <> 'ZZZ' AND G1.D_E_L_E_T_ <> '*'
        UNION ALL
        SELECT filho.G1_COD, filho.G1_COMP, filho.G1_QUANT * pai.QUANTIDADE, pai.Nivel + 1, filho.G1_REVFIM
        FROM SG1010 AS filho
        INNER JOIN ListMP AS pai ON filho.G1_COD = pai."COMPONENTE"
        INNER JOIN MaxRevisoes MR ON filho.G1_COD = MR.G1_COD AND filho.G1_REVFIM = MR.MaxRevisao
        WHERE pai.Nivel < 100 AND filho.G1_REVFIM <> 'ZZZ' AND filho.D_E_L_E_T_ <> '*'
    ),
    -- CTE com os dados da Nota Fiscal (simplificada para último registro apenas)
    UltimaNF AS (
        SELECT
            NFE.D1_COD,
            NFE.D1_DOC AS "DOCUMENTO NF",
            NFE.D1_DTDIGIT AS "ANO ENTRADA NF",
            NFE.D1_FORNECE AS "FORNECEDOR",
            livroFiscalFiltrado.F3_CHVNFE AS "CHAVE DE ACESSO",
            ROW_NUMBER() OVER (PARTITION BY NFE.D1_COD ORDER BY NFE.R_E_C_N_O_ DESC) AS rn
        FROM PROTHEUS12_R27.dbo.SD1010 NFE
        LEFT JOIN (
            SELECT 
                F3_NFISCAL, 
                F3_CLIEFOR, 
                F3_CHVNFE,
                ROW_NUMBER() OVER (PARTITION BY F3_NFISCAL, F3_CLIEFOR ORDER BY F3_CHVNFE DESC) AS row_num
            FROM PROTHEUS12_R27.dbo.SF3010
            WHERE F3_ESPECIE = 'SPED'
        ) AS livroFiscalFiltrado
            ON livroFiscalFiltrado.F3_NFISCAL = NFE.D1_DOC AND livroFiscalFiltrado.F3_CLIEFOR = NFE.D1_FORNECE
        WHERE NFE.D1_COD IN (SELECT DISTINCT "COMPONENTE" FROM ListMP)
            AND NFE.D_E_L_E_T_ <> '*'
            AND livroFiscalFiltrado.row_num = 1
    )
    -- Consulta Final
    SELECT 
        listMP."COMPONENTE" AS "CÓDIGO",
        prod.B1_DESC AS "DESCRIÇÃO",
        SUM(listMP."QUANTIDADE") AS "QUANT.",
        prod.B1_UM AS "UNID. MED.", 
        prod.B1_UCOM AS "ULT. ATUALIZ.",
        prod.B1_TIPO AS "TIPO", 
        prod.B1_LOCPAD AS "ARMAZÉM", 
        prod.B1_UPRC AS "VALOR UNIT. (R$)",
        SUM(listMP."QUANTIDADE" * prod.B1_UPRC) AS "SUB-TOTAL (R$)",
        prod.B1_PESO AS "PESO LÍQ",
        CASE
            WHEN fornProd.A5_CODPRF IS NULL THEN ''
            ELSE fornProd.A5_CODPRF
        END AS "CÓD. FORNECEDOR",
        NF.[DOCUMENTO NF],
        NF.[ANO ENTRADA NF],
        NF.[CHAVE DE ACESSO] 
    FROM 
        ListMP listMP
    INNER JOIN SB1010 prod 
        ON listMP."COMPONENTE" = prod.B1_COD
    LEFT JOIN UltimaNF NF 
        ON listMP."COMPONENTE" = NF.D1_COD 
        AND NF.rn = 1
    LEFT JOIN SA5010 fornProd 
        ON NF.D1_COD = fornProd.A5_PRODUTO 
        AND NF."FORNECEDOR" = fornProd.A5_FORNECE
    WHERE 
        prod.B1_TIPO = 'MP'
        AND prod.B1_LOCPAD IN ('01', '03', '11', '12', '97')
        AND prod.D_E_L_E_T_ <> '*'
    GROUP BY 
        listMP."COMPONENTE",
        prod.B1_DESC,
        prod.B1_UM,
        prod.B1_UCOM,
        prod.B1_TIPO,
        prod.B1_LOCPAD,
        prod.B1_UPRC,
        prod.B1_PESO,
        NF.[DOCUMENTO NF],
        NF.[ANO ENTRADA NF],
        NF.[CHAVE DE ACESSO],
        fornProd.A5_CODPRF
    ORDER BY 
        listMP."COMPONENTE" ASC;
    """
    return query


def recalculate_excel_formulas(file_path):
    app_excel = xw.App(visible=False)
    wb = xw.Book(file_path)
    wb.app.calculate()  # Recalcular todas as fórmulas
    wb.save()
    wb.close()
    app_excel.quit()


def format_decimal(value):
    return f'{value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


class ComercialApp(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.tipo_consulta = None
        self.main_window = main_window
        user_data = load_session()
        username = user_data["username"]
        role = user_data["role"]
        self.codigo = None
        self.descricao = None
        self.file_path = None
        self.nova_janela = None
        self.titulo_relatorio = "Relatório de Custos de Matéria-Prima e Itens Comerciais"
        self.username, self.password, self.database, self.server = setup_mssql()
        self.driver = '{SQL Server}'

        self.tree = QTableWidget(self)
        self.tree.setColumnCount(0)
        self.tree.setRowCount(0)

        self.setWindowTitle(f"Eureka® Comercial . {username} ({role})")
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_enaplic_path = os.path.join(script_dir, '..', 'resources', 'images', 'LOGO.jpeg')
        self.logo_label = QLabel(self)
        self.logo_label.setObjectName('logo-enaplic')
        pixmap_logo = QPixmap(logo_enaplic_path).scaledToWidth(60)
        self.logo_label.setPixmap(pixmap_logo)
        self.logo_label.setAlignment(Qt.AlignRight)

        self.label_codigo = QLabel("", self)

        self.label_product_name = QLabel("", self)
        self.label_product_name.setObjectName('product-name')
        self.label_product_name.setVisible(False)

        self.label_costs = QLabel("", self)
        self.label_costs.setObjectName('label-costs')
        self.label_costs.setVisible(False)
        self.label_costs.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

        self.campo_codigo = QLineEdit(self)
        self.campo_codigo.setPlaceholderText("Digite o código do produto...")
        self.campo_codigo.setFixedWidth(240)
        self.campo_codigo.setMaxLength(13)
        self.add_clear_button(self.campo_codigo)

        self.btn_consultar = QPushButton("Pesquisar", self)
        self.btn_consultar.clicked.connect(self.btn_consultar_actions)
        self.btn_consultar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_consulta_fiscal = QPushButton("Pesquisa Fiscal", self)
        self.btn_consulta_fiscal.clicked.connect(lambda: self.btn_consultar_actions('fiscal'))
        self.btn_consulta_fiscal.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_limpar = QPushButton("Limpar", self)
        self.btn_limpar.clicked.connect(self.limpar_campos)
        self.btn_limpar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_limpar.setEnabled(False)

        self.btn_nova_janela = QPushButton("Nova Janela", self)
        self.btn_nova_janela.clicked.connect(self.abrir_nova_janela)
        self.btn_nova_janela.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_exportar_pdf = QPushButton("Exportar PDF", self)
        self.btn_exportar_pdf.clicked.connect(self.exportar_pdf)
        self.btn_exportar_pdf.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_exportar_pdf.hide()

        self.btn_exportar_excel = QPushButton("Exportar Excel", self)
        self.btn_exportar_excel.clicked.connect(lambda: self.exportar_excel('excel'))
        self.btn_exportar_excel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_exportar_excel.hide()

        self.btn_fechar = QPushButton("Fechar", self)
        self.btn_fechar.clicked.connect(self.close)
        self.btn_fechar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_home = QPushButton("HOME", self)
        self.btn_home.setObjectName("btn_home")
        self.btn_home.clicked.connect(self.return_to_main)
        self.btn_home.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_abrir_desenho = QPushButton("Abrir Desenho", self)
        self.btn_abrir_desenho.clicked.connect(lambda: abrir_desenho(self, None, self.codigo))
        self.btn_abrir_desenho.hide()

        self.field_name_list = [
            "codigo"
        ]

        object_fields = {
            "codigo": self.campo_codigo
        }

        history_manager = SearchHistoryManager('comercial')
        self.autocomplete_settings = AutoCompleteManager(history_manager)
        self.autocomplete_settings.setup_autocomplete(self.field_name_list, object_fields)

        layout = QVBoxLayout()
        container_codigo = QVBoxLayout()
        container_codigo.addWidget(self.label_codigo)
        container_codigo.addWidget(self.campo_codigo)
        layout_header = QHBoxLayout()
        layout_table = QHBoxLayout()
        layout_sidebar = QVBoxLayout()
        layout_sidebar.addStretch(1)
        layout_sidebar.addWidget(self.label_costs)
        layout_sidebar.addWidget(self.btn_abrir_desenho)
        layout_sidebar.addStretch(1)
        layout_toolbar = QHBoxLayout()
        layout_footer = QHBoxLayout()

        layout_header.addStretch(1)
        layout_header.addWidget(self.label_product_name)
        layout_header.addStretch(1)
        layout_toolbar.addLayout(container_codigo)
        layout_toolbar.addWidget(self.btn_consultar)
        layout_toolbar.addWidget(self.btn_consulta_fiscal)
        layout_toolbar.addWidget(self.btn_limpar)
        layout_toolbar.addWidget(self.btn_nova_janela)
        layout_toolbar.addWidget(self.btn_exportar_excel)
        layout_toolbar.addWidget(self.btn_exportar_pdf)
        layout_toolbar.addWidget(self.btn_fechar)
        layout_toolbar.addWidget(self.btn_home)
        layout_toolbar.addStretch(1)

        layout_table.addWidget(self.tree)
        layout_table.addLayout(layout_sidebar)

        layout_footer.addStretch(1)
        layout_footer.addWidget(self.logo_label)

        layout.addLayout(layout_header)
        layout.addLayout(layout_toolbar)
        layout.addLayout(layout_table)
        layout.addLayout(layout_footer)

        self.setLayout(layout)

        self.setStyleSheet(comercial_qss())

    def btn_consultar_actions(self, tipo_consulta=None):
        for field_name in self.field_name_list:
            self.autocomplete_settings.save_search_history(field_name)
        self.executar_consulta(tipo_consulta)

    def return_to_main(self):
        self.close()  # Fecha a janela atual
        self.main_window.reopen()  # Reabre ou traz a janela principal ao foco

    def abrir_nova_janela(self):
        eng_window = ComercialApp(self.main_window)
        eng_window.showMaximized()
        self.main_window.sub_windows.append(eng_window)

    def get_product_name(self, codigo):
        query = f"""
            SELECT B1_DESC
                FROM 
                    {self.database}.dbo.SB1010
                WHERE 
                    B1_COD = N'{codigo}'
                    AND D_E_L_E_T_ <> '*';
            """
        try:
            with pyodbc.connect(
                    f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};'
                    f'PWD={self.password}') as conn:
                cursor = conn.cursor()
                cursor.execute(query)

                resultado = cursor.fetchone()
                codigo_produto = resultado[0]

                return codigo_produto

        except Exception as ex:
            exibir_mensagem('Erro banco de dados TOTVS', f'Erro ao consultar tabela de produtos SB1010: '
                                                         f'{str(ex)}', 'error')
            return None

    def add_clear_button(self, line_edit):
        clear_icon = self.style().standardIcon(QStyle.SP_LineEditClearButton)
        pixmap = clear_icon.pixmap(40, 40)  # Redimensionar o ícone para 20x20 pixels
        larger_clear_icon = QIcon(pixmap)
        clear_action = QAction(larger_clear_icon, "Clear", line_edit)
        clear_action.triggered.connect(line_edit.clear)
        line_edit.addAction(clear_action, QLineEdit.TrailingPosition)

    def exportar_excel(self, tipo_exportacao):

        now = datetime.now()
        default_filename = f'{self.codigo}_report_mp_{now.strftime("%Y-%m-%d_%H%M%S")}.xlsx'
        desktop_path = os.path.join(os.path.expanduser("~"), 'Desktop')

        if tipo_exportacao == 'excel':
            self.file_path, _ = QFileDialog.getSaveFileName(self, 'Salvar como', os.path.join(
                desktop_path, default_filename),
                                                            'Arquivos Excel (*.xlsx);;Todos os arquivos (*)')
        elif tipo_exportacao == 'pdf':
            self.file_path = os.path.join(desktop_path, default_filename)

        if self.file_path:
            data = obter_dados_tabela(self.tree)
            column_headers = [self.tree.horizontalHeaderItem(i).text() for i in range(self.tree.columnCount())]
            df = pd.DataFrame(data, columns=column_headers)
            df = df.fillna('')

            # Converter as colunas 'QUANT.', 'VALOR UNIT. (R$)' e 'SUB-TOTAL (R$)' para números
            numeric_columns = ['QUANT.', 'VALOR UNIT. (R$)', 'SUB-TOTAL (R$)']
            df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

            writer = pd.ExcelWriter(self.file_path, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Dados', index=False)

            workbook = writer.book
            worksheet_dados = writer.sheets['Dados']

            # Ajustar largura das colunas na planilha 'Dados'
            for i, col in enumerate(df.columns):
                max_len = df[col].astype(str).map(len).max()
                worksheet_dados.set_column(i, i, max_len + 2)

            # Calcular a última linha da planilha 'Dados'
            last_row = len(df) + 3  # +1 for header, +1 for the extra line we want to skip

            # Definindo um formato contábil
            accounting_format = workbook.add_format({'num_format': '[$R$-pt-BR] #,##0.00'})
            dolar_format = workbook.add_format({'num_format': '[$$-en-US] #,##0.00'})
            number_format = workbook.add_format({'num_format': '#,##0.00'})

            # Adicionar fórmulas na planilha 'Dados' na última linha + 1
            worksheet_dados.write(f'A{last_row}', 'COMERCIAL')
            worksheet_dados.write_formula(f'B{last_row}',
                                          f'=SUMIF(G2:G{last_row - 2}, "COMERCIAL", I2:I{last_row - 2})',
                                          accounting_format)

            worksheet_dados.write(f'A{last_row + 1}', 'MP')
            worksheet_dados.write_formula(f'B{last_row + 1}',
                                          f'=SUMIF(G2:G{last_row - 2}, "MATÉRIA-PRIMA", I2:I{last_row - 2})',
                                          accounting_format)

            worksheet_dados.write(f'A{last_row + 2}', 'PROD. COMER. IMPORT. DIR.')
            worksheet_dados.write_formula(f'B{last_row + 2}',
                                          f'=SUMIF(G2:G{last_row - 2}, "PROD. COMER. IMPORT. DIRETO", I2:I{last_row - 2})',
                                          accounting_format)

            worksheet_dados.write(f'A{last_row + 3}', 'MAT. PRIMA IMPORTADA')
            worksheet_dados.write_formula(f'B{last_row + 3}',
                                          f'=SUMIF(G2:G{last_row - 2}, "MAT. PRIMA IMPORT. DIRETO", I2:I{last_row - 2})',
                                          accounting_format)

            worksheet_dados.write(f'A{last_row + 4}', 'TRAT. SUPERF.')
            worksheet_dados.write_formula(f'B{last_row + 4}',
                                          f'=SUMIF(G2:G{last_row - 2}, "TRAT. SUPERFICIAL", I2:I{last_row - 2})',
                                          accounting_format)

            worksheet_dados.write_formula(f'C{last_row + 1}', f'=SUMIFS(C2:C{last_row - 2},D2:D{last_row - 2},'
                                                              f'"KG",G2:G{last_row - 2},"<>TRAT. SUPERFICIAL")')

            worksheet_dados.write(f'A{last_row + 6}', 'TOTAL GERAL')
            worksheet_dados.write_formula(f'B{last_row + 6}', f'=SUBTOTAL(9, B{last_row}:B{last_row + 4})',
                                          accounting_format)

            worksheet_dados.write(f'A{last_row + 8}', 'FATOR ENAPLIC')
            worksheet_dados.write_formula(f'B{last_row + 8}', f'3.75', number_format)
            worksheet_dados.write_formula(f'C{last_row + 8}', f'5.25', number_format)

            worksheet_dados.write(f'A{last_row + 9}', 'VENDA EM REAL (R$)')
            worksheet_dados.write_formula(f'B{last_row + 9}', f'=B{last_row + 6}*B{last_row + 8}', accounting_format)
            worksheet_dados.write_formula(f'C{last_row + 9}', f'=B{last_row + 6}*C{last_row + 8}', accounting_format)

            worksheet_dados.write(f'A{last_row + 10}', 'COTAÇÃO DO DÓLAR (US$)')
            worksheet_dados.write_formula(f'B{last_row + 10}', f'5.2', dolar_format)
            worksheet_dados.write_formula(f'C{last_row + 10}', f'5.2', dolar_format)

            worksheet_dados.write(f'A{last_row + 11}', 'VENDA EM DÓLAR (US$)')
            worksheet_dados.write_formula(f'B{last_row + 11}', f'=B{last_row + 9}/B{last_row + 10}', dolar_format)
            worksheet_dados.write_formula(f'C{last_row + 11}', f'=C{last_row + 9}/C{last_row + 10}', dolar_format)

            writer.close()

            recalculate_excel_formulas(self.file_path)

            if tipo_exportacao == 'excel':
                os.startfile(self.file_path)

    def exportar_pdf(self):
        self.exportar_excel('pdf')

        # Caminho para salvar o PDF
        pdf_path, _ = QFileDialog.getSaveFileName(self, 'Salvar como', self.file_path.replace('.xlsx', '.pdf'),
                                                  'Arquivos PDF (*.pdf);;Todos os arquivos (*)')
        if not pdf_path:
            return

        # Ler dados do Excel
        df_tabela = pd.read_excel(self.file_path, sheet_name='Dados')

        if os.path.exists(self.file_path):
            os.remove(self.file_path)

        if self.tipo_consulta == 'fiscal':
            df_tabela = df_tabela.drop(columns=['DOCUMENTO NF', 'ANO ENTRADA NF', 'CHAVE DE ACESSO', 'PESO LÍQ', 'CÓD. FORNECEDOR'])

        nan_row_index = df_tabela.isna().all(axis=1).idxmax()
        df_dados = df_tabela.iloc[:nan_row_index].dropna(how='all')
        df_dados = df_dados.fillna('')

        idx_total_geral = df_tabela[df_tabela['CÓDIGO'] == 'TOTAL GERAL'].index[0]
        idx_fator_enaplic = df_tabela[df_tabela['CÓDIGO'] == 'FATOR ENAPLIC'].index[0]

        df_total_armazem = df_tabela.iloc[nan_row_index + 1: idx_total_geral + 1].dropna(how='all')
        df_total_armazem = df_total_armazem.dropna(axis=1, how='all').fillna('')

        df_sugestao_vendas = df_tabela.iloc[idx_fator_enaplic:].dropna(axis=1, how='all').fillna('')

        table_valores_header = ['TOTAL POR ARMAZÉM', 'CUSTO\n(R$)', 'QUANTIDADE\n(kg)']
        table_valores = [table_valores_header] + df_total_armazem.values.tolist()

        table_sugestao_header = ['SUGESTÃO DE VENDA', 'QP', 'QR']
        table_sugestao_vendas = [table_sugestao_header] + df_sugestao_vendas.values.tolist()

        # Index das colunas que você deseja formatar
        idx_custo = table_valores_header.index('CUSTO\n(R$)')
        idx_quantidade = table_valores_header.index('QUANTIDADE\n(kg)')
        idx_custo_venda_qp = table_sugestao_header.index('QP')
        idx_custo_venda_qr = table_sugestao_header.index('QR')

        for row in table_valores[1:]:  # Começa do segundo item para pular o cabeçalho
            row[idx_custo] = format_decimal(row[idx_custo])
            if row[idx_quantidade] != '':
                row[idx_quantidade] = format_decimal(row[idx_quantidade])

        for row in table_sugestao_vendas[1:]:
            row[idx_custo_venda_qp] = format_decimal(row[idx_custo_venda_qp])
            row[idx_custo_venda_qr] = format_decimal(row[idx_custo_venda_qr])

        df_dados['DESCRIÇÃO'] = df_dados['DESCRIÇÃO'].apply(lambda value: value[:60])
        df_dados['QUANT.'] = df_dados['QUANT.'].apply(format_decimal)
        df_dados['VALOR UNIT. (R$)'] = df_dados['VALOR UNIT. (R$)'].apply(format_decimal)
        df_dados['SUB-TOTAL (R$)'] = df_dados['SUB-TOTAL (R$)'].apply(format_decimal)
        df_dados = df_dados.drop(columns='TIPO')
        df_dados = df_dados.rename(columns={'UNID. MED.': 'UNID.\nMED.'})
        df_dados['ARMAZÉM'] = df_dados['ARMAZÉM'].replace({
            'COMERCIAL': 'COM.',
            'MATÉRIA-PRIMA': 'MP',
            'TRAT. SUPERFICIAL': 'TRAT.',
            'PROD. COMER. IMPORT. DIRETO': 'COM. IMP.',
            'MAT. PRIMA IMPORT. DIRETO': 'MP IMP.'
        })
        df_dados = df_dados.rename(columns={'ULT. ATUALIZ.': 'ÚLT.\nATUALIZ.'})
        df_dados = df_dados.rename(columns={'VALOR UNIT. (R$)': 'VALOR\nUNIT. (R$)'})
        df_dados.rename(columns={'SUB-TOTAL (R$)': 'TOTAL (R$)'})

        def build_elements():
            elements_pdf = []

            # Adicionar logo
            script_dir = os.path.dirname(os.path.abspath(__file__))
            logo_enaplic_path = os.path.join(script_dir, '..', 'resources', 'images', 'logo_enaplic.jpg')

            if os.path.exists(logo_enaplic_path):
                logo = Image(logo_enaplic_path, 5 * inch, 0.5 * inch)
                elements_pdf.append(logo)

            # Adicionar título e data/hora
            title_style = ParagraphStyle(name='TitleStyle', fontSize=16, fontName='Helvetica-Bold', leading=24,
                                         alignment=TA_CENTER)
            normal_style = ParagraphStyle(name='NormalStyle', fontSize=10, leading=12, alignment=TA_CENTER)
            product_style = ParagraphStyle(name='ProductStyle', fontSize=12, leading=20, fontName='Helvetica-Bold',
                                           spaceAfter=12)

            title = Paragraph(f"{self.titulo_relatorio}", title_style)
            date_time = Paragraph(datetime.now().strftime("%d/%m/%Y %H:%M"), normal_style)
            elements_pdf.append(Paragraph("<br/><br/>", normal_style))
            product = Paragraph(f'{self.codigo} {self.descricao}', product_style)

            elements_pdf.append(title)
            elements_pdf.append(date_time)
            elements_pdf.append(Spacer(1, 12))
            elements_pdf.append(product)
            elements_pdf.append(Spacer(1, 8))  # Espaço entre título e tabela

            # Dados da tabela
            column_headers_dados = list(df_dados.columns)
            table_dados = [column_headers_dados] + df_dados.values.tolist()

            # Função para calcular a largura das colunas com base no conteúdo
            def calculate_col_widths(dataframe, col_width_multiplier=1.2, min_width=45):
                col_widths = []
                for col in dataframe.columns:
                    max_length = max(dataframe[col].astype(str).apply(len).max(), len(col))
                    col_width = max_length * col_width_multiplier
                    if col == 'DESCRIÇÃO':
                        col_width *= 3  # Aumentar a largura da coluna "descrição"
                    col_width = max(col_width, min_width)
                    col_widths.append(col_width)
                return col_widths

            col_widths_dados = calculate_col_widths(df_dados)

            col_idx_descricao = column_headers_dados.index('DESCRIÇÃO')

            # Estilo da tabela
            style_dados = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment for all cells
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (col_idx_descricao, 0), (col_idx_descricao, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),  # Adds a line below the first row
                ('LINEABOVE', (0, 1), (-1, -1), 0.5, colors.black)  # Removes lines above all other rows
            ])

            table_dados = Table(table_dados, colWidths=col_widths_dados)
            table_dados.setStyle(style_dados)
            elements_pdf.append(table_dados)

            style_valores = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Alinha a primeira coluna à esquerda
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),  # Alinha as demais colunas à direita
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment for all cells
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),  # Adds a line below the first row
                ('LINEABOVE', (0, 1), (-1, -1), 0.5, colors.black)  # Removes lines above all other rows
            ])

            summary_table = Table(table_valores)
            vendas_table = Table(table_sugestao_vendas)

            summary_table.setStyle(style_valores)
            vendas_table.setStyle(style_valores)

            elements_pdf.append(Spacer(1, 36))  # Espaço entre tabela e sumário
            elements_pdf.append(summary_table)
            elements_pdf.append(Spacer(1, 36))
            elements_pdf.append(vendas_table)

            return elements_pdf

        # Primeira passagem para contar as páginas
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20, bottomMargin=30)
        elements = build_elements()

        def add_page_number(canvas, doc):
            page_num = canvas.getPageNumber()
            text = f"Página {page_num}"
            canvas.drawRightString(200 * mm, 5 * mm, text)

        doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
        pdf = buffer.getvalue()
        buffer.close()

        # Contar o número total de páginas
        reader = PdfReader(io.BytesIO(pdf))
        num_pages = len(reader.pages)

        # Segunda passagem para adicionar paginação completa
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20, bottomMargin=30)
        elements = build_elements()

        def add_page_number_with_total(canvas, doc):
            page_num = canvas.getPageNumber()
            text = f"Página {page_num} de {num_pages}"
            canvas.drawRightString(200 * mm, 5 * mm, text)

        doc.build(elements, onFirstPage=add_page_number_with_total, onLaterPages=add_page_number_with_total)
        final_pdf = buffer.getvalue()
        buffer.close()

        # Salvar o PDF final
        with open(pdf_path, "wb") as f:
            f.write(final_pdf)
        os.startfile(pdf_path)

    def configurar_tabela(self, dataframe):
        self.tree.setColumnCount(len(dataframe.columns))
        self.tree.setHorizontalHeaderLabels(dataframe.columns)
        self.tree.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tree.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tree.setSelectionBehavior(QTableWidget.SelectRows)
        self.tree.setSelectionMode(QTableWidget.SingleSelection)
        self.tree.itemDoubleClicked.connect(copiar_linha)
        fonte_tabela = QFont("Segoe UI", 10)
        self.tree.setFont(fonte_tabela)
        altura_linha = 35
        self.tree.verticalHeader().setDefaultSectionSize(altura_linha)
        self.tree.horizontalHeader().sectionClicked.connect(self.ordenar_tabela)
        self.tree.horizontalHeader().setStretchLastSection(False)

    def ordenar_tabela(self, logical_index):
        # Obter o índice real da coluna (considerando a ordem de classificação)
        index = self.tree.horizontalHeader().sortIndicatorOrder()

        # Definir a ordem de classificação
        order = Qt.AscendingOrder if index == 0 else Qt.DescendingOrder

        # Ordenar a tabela pela coluna clicada
        self.tree.sortItems(logical_index, order)

    def limpar_campos(self):
        self.campo_codigo.clear()
        self.tree.setColumnCount(0)
        self.tree.setRowCount(0)
        self.label_product_name.hide()
        self.label_costs.hide()
        self.btn_exportar_excel.hide()
        self.btn_exportar_pdf.hide()
        self.btn_abrir_desenho.hide()

    def controle_campos_formulario(self, status):
        self.campo_codigo.setEnabled(status)
        self.btn_consultar.setEnabled(status)
        self.btn_exportar_excel.setEnabled(status)
        self.btn_exportar_pdf.setEnabled(status)
        self.btn_limpar.setEnabled(status)
        self.btn_abrir_desenho.setEnabled(status)
        self.btn_consulta_fiscal.setEnabled(status)

    def executar_consulta(self, tipo_consulta):
        codigo = self.campo_codigo.text().upper().strip()
        self.codigo = codigo

        if codigo == '':
            exibir_mensagem("ATENÇÃO!",
                            "O campo de pesquisa está vazio.\n\nDigite um código válido e tente "
                            "novamente!\n\nEUREKA® Comercial",
                            "info")
            self.controle_campos_formulario(True)
            return

        dialog = loading_dialog(self, "Carregando...", "🤖 Processando dados do TOTVS..."
                                                       "\n\n🤖 Por favor, aguarde.\n\nEureka®")

        query = query_consulta(codigo) if tipo_consulta != 'fiscal' else query_pesquisa_fiscal(codigo)
        self.label_product_name.hide()
        self.label_costs.hide()
        self.controle_campos_formulario(False)

        conn_str = f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}'
        engine = create_engine(f'mssql+pyodbc:///?odbc_connect={conn_str}')

        try:
            dataframe = pd.read_sql(query, engine)
            if not dataframe.empty:
                self.descricao = self.get_product_name(self.codigo)
                self.tipo_consulta = None

                common_columns = {
                    'DESCRIÇÃO': 'first',
                    'QUANT.': 'sum',
                    'UNID. MED.': 'first',
                    'ULT. ATUALIZ.': 'first',
                    'TIPO': 'first',
                    'ARMAZÉM': 'first',
                    'VALOR UNIT. (R$)': 'first',
                    'SUB-TOTAL (R$)': 'sum'
                }

                if tipo_consulta == 'fiscal':
                    self.tipo_consulta = tipo_consulta
                    fiscal_columns = {
                        'PESO LÍQ': 'first',
                        'CÓD. FORNECEDOR': 'first',
                        'DOCUMENTO NF': 'first',
                        'ANO ENTRADA NF': 'first',
                        'CHAVE DE ACESSO': 'first'
                    }
                    common_columns.update(fiscal_columns)

                df_consolidated = dataframe.groupby('CÓDIGO').agg(common_columns).reset_index()

                # Converter para float com duas casas decimais
                columns_to_convert = ['QUANT.', 'VALOR UNIT. (R$)', 'SUB-TOTAL (R$)']
                df_consolidated[columns_to_convert] = (df_consolidated[columns_to_convert]
                                                              .map(lambda x: round(float(x), 2)))

                if tipo_consulta == 'fiscal':
                    df_consolidated['PESO LÍQ'] = df_consolidated['PESO LÍQ'].apply(lambda x: format_decimal(x) if x is not None else x)
                    df_consolidated['DOCUMENTO NF'] = df_consolidated['DOCUMENTO NF'].apply(lambda x: x.lstrip('0') if x is not None else x)
                    df_consolidated['ANO ENTRADA NF'] = df_consolidated['ANO ENTRADA NF'].apply(
                        lambda x: x[:4] if x is not None else x)

                self.configurar_tabela(df_consolidated)
                self.tree.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
                self.tree.setRowCount(0)

                for i, row in df_consolidated.iterrows():
                    self.tree.setSortingEnabled(False)
                    self.tree.insertRow(i)
                    for column_name, value in row.items():
                        if column_name == 'ULT. ATUALIZ.' and not value.isspace():
                            data_obj = datetime.strptime(value, "%Y%m%d")
                            value = data_obj.strftime("%d/%m/%Y")
                        elif column_name == 'ARMAZÉM':
                            if value == '01':
                                value = 'MATÉRIA-PRIMA'
                            elif value == '03':
                                value = 'COMERCIAL'
                            elif value == '11':
                                value = 'PROD. COMER. IMPORT. DIRETO'
                            elif value == '12':
                                value = 'MAT. PRIMA IMPORT. DIRETO'
                            elif value == '97':
                                value = 'TRAT. SUPERFICIAL'

                        item = QTableWidgetItem(str(value).strip())

                        if column_name in ['QUANT.', 'ULT. ATUALIZ.', 'ARMAZÉM',
                                           'DOCUMENTO NF', 'ANO ENTRADA NF',
                                           'CHAVE DE ACESSO', 'CÓD. FORNECEDOR', 'PESO LÍQ']:
                            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        elif column_name in ['VALOR UNIT. (R$)', 'SUB-TOTAL (R$)']:
                            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                        self.tree.setItem(i, df_consolidated.columns.get_loc(column_name), item)
                self.tree.setSortingEnabled(True)
                self.controle_campos_formulario(True)
                self.label_product_name.setText(f"{self.codigo} - {self.descricao}")
                self.label_product_name.show()
                self.formatar_indicadores_custos(df_consolidated)
                self.btn_exportar_excel.show()
                self.btn_exportar_pdf.show()
                self.btn_abrir_desenho.show()
                dialog.close()
            else:
                self.controle_campos_formulario(True)
                dialog.close()
                exibir_mensagem("EUREKA® Comercial", 'Produto não encontrado!', "info")
                return

        except pyodbc.Error as ex:
            exibir_mensagem('Erro ao consultar tabela', f'Erro: {str(ex)}', 'error')

        finally:
            # Fecha a conexão com o banco de dados se estiver aberta
            if 'engine' in locals():
                engine.dispose()

    def formatar_indicadores_custos(self, dataframe):
        column_interval_kg = 'UNID. MED.'
        column_quantity_kg = 'QUANT.'
        column_interval = 'ARMAZÉM'
        column_subtotal = 'SUB-TOTAL (R$)'
        armazens = {
            'custo_comercial': '03',
            'custo_mp': '01',
            'custo_comer_importado': '11',
            'custo_mp_importado': '12',
            'custo_trat_superf': '97',
        }

        resultados = {key: dataframe[dataframe[column_interval] == value][column_subtotal].sum()
                      for key, value in armazens.items()}

        custos_formatados = {key: format_decimal(value) for key, value in resultados.items()}

        resultado_quantidade_kg = dataframe[
            (dataframe[column_interval_kg] == 'KG') &
            (dataframe[column_interval] != '97')
        ][column_quantity_kg].sum()

        total_geral = dataframe[column_subtotal].sum()

        costs_table = f"""
            <table border="1" cellspacing="2" cellpadding="4" style="border-collapse: collapse; text-align: left; width: 100%;">
                <tr>
                    <th style="text-align: middle; vertical-align: middle;">TOTAL POR ARMAZÉM</th>
                    <th style="text-align: right; vertical-align: middle;">CUSTO (R$)</th>
                    <th style="text-align: right; vertical-align: middle;">QUANTIDADE (kg)</th>
                </tr>
                <tr>
                    <td style="vertical-align: middle;">Comercial</td>
                    <td style="text-align: right; vertical-align: middle;">{custos_formatados['custo_comercial']}</td>
                    <td style="text-align: right; vertical-align: middle;"></td>
                </tr>
                <tr>
                    <td style="vertical-align: middle;">Matéria-prima</td>
                    <td style="text-align: right; vertical-align: middle;">{custos_formatados['custo_mp']}</td>
                    <td style="text-align: right; vertical-align: middle;">{format_decimal(resultado_quantidade_kg)}</td>
                </tr>
                <tr>
                    <td style="vertical-align: middle;">Produto comercial importado</td>
                    <td style="text-align: right; vertical-align: middle;">{custos_formatados['custo_comer_importado']}</td>
                    <td style="text-align: right; vertical-align: middle;"></td>
                </tr>
                <tr>
                    <td style="vertical-align: middle;">Matéria-prima importada</td>
                    <td style="text-align: right; vertical-align: middle;">{custos_formatados['custo_mp_importado']}</td>
                    <td style="text-align: right; vertical-align: middle;"></td>
                </tr>
                <tr>
                    <td style="vertical-align: middle;">Tratamento superficial</td>
                    <td style="text-align: right; vertical-align: middle;">{custos_formatados['custo_trat_superf']}</td>
                    <td style="text-align: right; vertical-align: middle;"></td>
                </tr>
                <tr>
                    <td style="text-align: middle; vertical-align: middle;"><b>TOTAL GERAL</b></td>
                    <td style="text-align: right; vertical-align: middle;"><b>{format_decimal(total_geral)}</b></td>
                    <td style="text-align: right; vertical-align: middle;"></td>
                </tr>
            </table>
        """

        self.label_costs.setText(costs_table)
        self.label_costs.show()
