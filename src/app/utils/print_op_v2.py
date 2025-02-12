import os
from datetime import datetime

import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (QVBoxLayout, QMessageBox, QProgressBar, QLabel)
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from sqlalchemy import create_engine

from src.app.utils.db_mssql import setup_mssql
from src.app.utils.utils import exibir_mensagem


class PDFGeneratorThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, df: pd.DataFrame, df_op_table, output_dir: str):
        super().__init__()
        self.output_path = None
        self.df = df
        self.output_dir = output_dir
        self.df_op_table = df_op_table

    def run(self):
        try:
            total_rows = len(self.df)
            for index, row in self.df.iterrows():
                progress = int((index + 1) / total_rows * 100)
                self.output_path = os.path.join(self.output_dir,
                                           f"OP_{row['OP'].strip()}_{row['Código'].strip()}.pdf")
                generate_production_order_pdf(row, self.output_path, self.progress, self.df_op_table)
                self.progress.emit(progress)
            self.finished.emit(self.output_path)
        except Exception as e:
            self.error.emit(str(e))

def get_resource_path(resource_type: str, filename: str) -> str:
    """Returns the path for various resource types"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, '..', '..', 'resources', resource_type, filename)

def create_header_style():
    """Creates and returns custom header style"""
    return ParagraphStyle(
        'CustomHeader',
        parent=getSampleStyleSheet()['Heading3'],
        fontSize=10,
        spaceAfter=30,
        alignment=TA_LEFT,
        fontName='Courier-New'
    )

def generate_hierarchical_table(df: pd.DataFrame, canvas_obj, y_position: float):
    """Generates the hierarchical table for the production order"""
    # Define column widths and headers
    col_widths = [60, 70, 200, 60, 160]  # Adjusted widths
    headers = ['OP Pai', 'Código Pai', 'Descrição', 'Quantidade', 'Centro de Custo']

    # Prepare data for table
    table_data = [headers]
    for _, row in df.iterrows():
        descricao = str(row['Descrição']).strip()
        if len(descricao) > 35:
            descricao = descricao[:35] + '...'
        table_data.append([
            str(row['OP']),
            str(row['Código Pai']).strip(),
            descricao,
            str(row['Quantidade']),
            str(row['Centro de Custo'].strip())
        ])

    # Create and style table
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.transparent),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Courier-New-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Courier-New'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.transparent),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    # Draw table
    table.wrapOn(canvas_obj, 530, 400)
    table.drawOn(canvas_obj, 30, y_position)

def consultar_hierarquia_tabela(codigo):
    username, password, database, server = setup_mssql()
    driver = '{SQL Server}'
    conn_str = (f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};'
                f'PWD={password}')
    engine = create_engine(f'mssql+pyodbc:///?odbc_connect={conn_str}')

    query_onde_usado = f"""
                    SELECT
                        STRUT.G1_COD AS "Código",
                        PROD.B1_DESC "Descrição",
                        STRUT.G1_QUANT AS "Quantidade",
                        STRUT.G1_XUM AS "Unid"
                    FROM
                        {database}.dbo.SG1010 STRUT
                    INNER JOIN
                        {database}.dbo.SB1010 PROD
                    ON
                        STRUT.G1_COD = PROD.B1_COD
                    WHERE G1_COMP = '{codigo}'
                        AND STRUT.G1_REVFIM = (
                            SELECT MAX(G1_REVFIM)
                            FROM PROTHEUS12_R27.dbo.SG1010
                            WHERE G1_COD = STRUT.G1_COD
                            AND G1_REVFIM <> 'ZZZ'
                            AND D_E_L_E_T_ <> '*')
                        AND STRUT.G1_REVFIM <> 'ZZZ'
                        AND STRUT.D_E_L_E_T_ <> '*'
                        AND PROD.D_E_L_E_T_ <> '*'
                    ORDER BY B1_DESC ASC;
                """
    try:
        with engine.connect() as connection:
            dataframe = pd.read_sql(query_onde_usado, connection)
        return dataframe if not dataframe.empty else pd.DataFrame()

    except Exception as ex:
        print(f"Erro ao consultar a hierarquia: {ex}")
        exibir_mensagem('Erro ao consultar itens pais da OP', f'Erro: {str(ex)}', 'error')
        return pd.DataFrame()

    finally:
        # Fecha a conexão com o banco de dados se estiver aberta
        engine.dispose()

def generate_production_order_pdf(row: pd.Series, output_path: str, progress_callback, dataframe_geral):
    data_hora_impressao = datetime.now().strftime('%d/%m/%Y   %H:%M:%S')
    codigo = row['Código'].strip()
    num_qp = row['QP'].strip()
    num_op = row['OP'].strip()
    """Generates PDF for a single Production Order"""
    # Create PDF
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    margin = 10 * mm

    # Logo
    logo_path = get_resource_path('images', 'logo_enaplic.jpg')
    logo_width = 80
    logo_x = margin
    logo_y = height - margin * 3
    c.drawImage(logo_path, logo_x, logo_y, width=logo_width, preserveAspectRatio=True)
    progress_callback.emit(20)

    # Title
    title_text = f"ORDEM DE PRODUÇÃO - {num_op}"
    title_font_size = 12
    c.setFont("Courier-New-Bold", title_font_size)
    title_width = c.stringWidth(title_text, "Courier-New-Bold", title_font_size)
    title_x = (width - title_width) / 2
    title_y = 810  # Adjust this value as needed to position the title vertically
    c.drawString(title_x, title_y, title_text)
    progress_callback.emit(30)

    title_text = f"QP: {num_qp} {row['PROJETO']}"
    title_font_size = 12
    c.setFont("Courier-New-Bold", title_font_size)
    title_width = c.stringWidth(title_text, "Courier-New-Bold", title_font_size)
    title_x = (width - title_width) / 2
    title_y = title_y - 20  # Adjust this value as needed to position the title vertically
    c.drawString(title_x, title_y, title_text)
    progress_callback.emit(35)

    # Add line below the title
    line_y = title_y - 10
    c.line(margin, line_y, width - margin, line_y)

    # Barcode
    barcode_path = get_resource_path('images', 'barcode.png')
    barcode_width = 100
    barcode_x = 475
    barcode_y = 565  # Adjust this value as needed to position the barcode vertically
    c.drawImage(barcode_path, barcode_x, barcode_y, width=barcode_width, preserveAspectRatio=True)
    progress_callback.emit(40)

    # Informações da Ordem de Produção
    header_style = create_header_style()

    data_emissao = datetime.strptime(row['Data Abertura'].strip(), "%Y%m%d").strftime("%d/%m/%Y")
    data_entrega = datetime.strptime(row['Prev. Entrega'].strip(), "%Y%m%d").strftime("%d/%m/%Y")

    op_info = [
        f"Produto: {row['Código'].strip()}  {row['Descrição'].strip()}",
        f"Quantidade: {row['Quantidade']}   {row['Unid.']}",
        f"Centro de Custo: {row['Código CC']}   {row['Centro de Custo']}",
        f"Dt. Abertura da OP: {data_emissao}",
        f"Previsão de Entrega: {data_entrega}",
        f"Dt. Impressão da OP: {data_hora_impressao}",
        f"Observação: {row['Observação'].strip()}"
    ]

    y_position = 750  # Adjust this value as needed to position the information vertically
    for line in op_info:
        p = Paragraph(line, header_style)
        p.wrapOn(c, width - 2*margin, 20)
        p.drawOn(c, margin, y_position)
        y_position -= 15

    progress_callback.emit(60)

    # Tabela hierárquica
    dataframe_onde_usado = consultar_hierarquia_tabela(codigo)

    if not dataframe_onde_usado.empty:
        # Get the list of códigos from dataframe_onde_usado
        codigos_onde_usado = dataframe_onde_usado['Código'].unique()
        codigos_onde_usado = [item.strip() for item in codigos_onde_usado]

        # Filter dataframe_op to only include rows where 'Código' is in codigos_onde_usado and 'QP' matches num_qp
        dataframe_filtrado = dataframe_geral[
            dataframe_geral['Código'].str.strip().isin(codigos_onde_usado) &
            (dataframe_geral['QP'].str.strip() == num_qp)
        ]

        # Add the OP column to the filtered dataframe if it doesn't exist
        if 'OP' not in dataframe_filtrado.columns:
            dataframe_filtrado['OP'] = row['OP']

        # Merge the filtered dataframe with onde_usado to get additional information
        dataframe_final = pd.merge(
            dataframe_filtrado,
            dataframe_onde_usado,
            on='Código',
            suffixes=('', '_onde_usado')
        )

        # Select and rename columns as needed
        dataframe_final = dataframe_final[[
            'OP',
            'Código',
            'Descrição',
            'Quantidade_onde_usado',
            'Centro de Custo'
        ]].copy()

        # Rename columns to match the expected format
        dataframe_final = dataframe_final.rename(columns={
            'Código': 'Código Pai',
            'Quantidade_onde_usado': 'Quantidade'
        })

        # Sort the dataframe if needed
        dataframe_final = dataframe_final.sort_values('OP')

        # Generate the table
        table_y_position = y_position - 60
        generate_hierarchical_table(dataframe_final, c, table_y_position)
        progress_callback.emit(80)
    else:
        print(f"No hierarchical data found for código: {row['Código']}")

    # Roteiro
    workflow_path = get_resource_path('images', 'roteiro_v3.png')
    workflow_y_position = table_y_position - 700  # Adjust this value as needed to position the workflow vertically
    c.drawImage(workflow_path, margin, workflow_y_position, width=width-2*margin, preserveAspectRatio=True)

    # Save first page
    c.save()
    progress_callback.emit(90)

    # Handle technical drawing (Page 2)
    codigo_desenho = row['Código'].strip()
    drawing_path = os.path.normpath(os.path.join(
        r"\\192.175.175.4\dados\EMPRESA\PROJETOS\PDF-OFICIAL",
        f"{codigo_desenho}.PDF"
    ))

    from PyPDF2 import PdfMerger

    if os.path.exists(drawing_path):
        merger = PdfMerger()
        progress_callback.emit(94)
        merger.append(output_path)  # First append the production order page
        merger.append(drawing_path)  # Then append the technical drawing

        # Create a temporary file for the merged result
        temp_output = output_path + '.temp'
        merger.write(temp_output)
        progress_callback.emit(98)
        merger.close()

        # Replace the original file with the merged result
        os.replace(temp_output, output_path)
        progress_callback.emit(100)
    else:
        # Create a new page with the "Drawing not found" message
        c = canvas.Canvas(output_path + '.temp', pagesize=A4)
        width, height = A4

        c.showPage()
        c.setFont("Courier-New-Italic", 24)
        c.drawCentredString(width/2, height/2, "DESENHO NÃO ENCONTRADO")
        c.save()

        # Merge the original page with the "Drawing not found" page
        merger = PdfMerger()
        progress_callback.emit(94)
        merger.append(output_path)
        merger.append(output_path + '.temp')

        temp_output = output_path + '.merged'
        merger.write(temp_output)
        progress_callback.emit(98)
        merger.close()

        # Clean up temporary files and replace the original
        os.remove(output_path + '.temp')
        os.replace(temp_output, output_path)
        progress_callback.emit(100)


def registrar_fonte_personalizada():
    # Registra todas as variações da fonte Courier
    pdfmetrics.registerFont(TTFont('Courier-New', r'C:\WINDOWS\FONTS\COUR.TTF'))
    pdfmetrics.registerFont(TTFont('Courier-New-Bold', r'C:\WINDOWS\FONTS\COURBD.TTF'))
    pdfmetrics.registerFont(TTFont('Courier-New-Italic', r'C:\WINDOWS\FONTS\COURI.TTF'))
    pdfmetrics.registerFont(TTFont('Courier-New-BoldItalic', r'C:\WINDOWS\FONTS\COURBI.TTF'))

    # Mapeia as variações da fonte
    addMapping('Courier-New', 0, 0, 'Courier-New')              # normal
    addMapping('Courier-New', 1, 0, 'Courier-New-Bold')         # bold
    addMapping('Courier-New', 0, 1, 'Courier-New-Italic')       # italic
    addMapping('Courier-New', 1, 1, 'Courier-New-BoldItalic')   # bold & italic


class PrintProductionOrderDialogV2(QtWidgets.QDialog):
    def __init__(self, df: pd.DataFrame, df_op_table, parent=None):
        super().__init__(parent)
        self.label_status = None
        self.pdf_thread = None
        self.progress_bar = None
        self.layout = None
        self.df = df
        self.df_op_table = df_op_table
        self.init_ui()
        registrar_fonte_personalizada()
        self.print_production_order()

    def init_ui(self):
        self.setWindowTitle("Impressão de OP")
        self.setGeometry(100, 100, 400, 100)

        self.layout = QVBoxLayout(self)

        self.label_status = QLabel("Publicando Ordem de Produção...", self)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)

        self.layout.addWidget(self.label_status)
        self.layout.addWidget(self.progress_bar)

        self.setLayout(self.layout)

    def print_production_order(self):
        output_dir = r"\\192.175.175.4\dados\EMPRESA\PRODUCAO\ORDEM_DE_PRODUCAO"
        os.makedirs(output_dir, exist_ok=True)

        self.pdf_thread = PDFGeneratorThread(self.df, self.df_op_table, output_dir)
        self.pdf_thread.finished.connect(self.on_pdf_generation_complete)
        self.pdf_thread.error.connect(self.on_pdf_generation_error)
        self.pdf_thread.progress.connect(self.update_progress)
        self.pdf_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_pdf_generation_complete(self, path):
        QMessageBox.information(self, "", f"PDF gerado com sucesso!")
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        self.close()

    def on_pdf_generation_error(self, error):
        QMessageBox.critical(self, "Erro", f"Erro ao gerar PDF: {error}")
        self.close()
