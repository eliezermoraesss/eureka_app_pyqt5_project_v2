import os
from datetime import datetime

import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (QVBoxLayout, QMessageBox, QProgressBar)
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from sqlalchemy import create_engine

from src.app.utils.db_mssql import setup_mssql
from src.app.utils.utils import exibir_mensagem


class PDFGeneratorThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, df: pd.DataFrame, df_op_table, output_path: str):
        super().__init__()
        self.df = df
        self.output_path = output_path
        self.df_op_table = df_op_table

    def run(self):
        try:
            total_rows = len(self.df)
            for index, row in self.df.iterrows():
                progress = int((index + 1) / total_rows * 100)
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
        parent=getSampleStyleSheet()['Heading1'],
        fontSize=12,
        spaceAfter=30,
        alignment=TA_LEFT
    )

def generate_hierarchical_table(df: pd.DataFrame, canvas_obj, y_position: float):
    """Generates the hierarchical table for the production order"""
    # Define column widths and headers
    col_widths = [60, 100, 250, 60, 40]  # Adjusted widths
    headers = ['OP', 'Código Pai', 'Descrição', 'Qtde', 'Un.']

    # Prepare data for table
    table_data = [headers]
    for _, row in df.iterrows():
        table_data.append([
            str(row['OP']),
            str(row['Código Pai']),
            str(row['Descrição']),
            str(row['Quantidade']),
            str(row['Unid'])
        ])

    # Create and style table
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
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
        print(f"Executing query: {query_onde_usado}")

        with engine.connect() as connection:
            dataframe = pd.read_sql(query_onde_usado, connection)
        print(f"Query returned {len(dataframe)} rows")

        return dataframe if not dataframe.empty else pd.DataFrame()

    except Exception as ex:
        print(f"Erro ao consultar a hierarquia: {ex}")
        exibir_mensagem('Erro ao consultar itens pais da OP', f'Erro: {str(ex)}', 'error')
        return pd.DataFrame()

    finally:
        # Fecha a conexão com o banco de dados se estiver aberta
        engine.dispose()

def generate_production_order_pdf(row: pd.Series, output_path: str, progress_callback, dataframe_geral):
    codigo = row['Código'].strip()
    """Generates PDF for a single Production Order"""
    # Create PDF
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    margin = 15 * mm

    # Header
    logo_path = get_resource_path('images', 'logo_enaplic.jpg')
    c.drawImage(logo_path, margin, height - margin * 2, width=100, preserveAspectRatio=True)
    progress_callback.emit(20)

    # Barcode
    barcode_path = get_resource_path('images', 'barcode.png')
    c.drawImage(barcode_path, width - margin * 8, height - margin * 2, width=100, preserveAspectRatio=True)
    progress_callback.emit(40)

    # Production Order Information
    header_style = create_header_style()

    op_info = [
        f"OP: {row['OP']}",
        f"Produto: {row['Código']} - {row['Descrição']}",
        f"Quantidade: {row['Quantidade']}",
        f"Data Abertura: {row['Data Abertura']}",
        f"Previsão Entrega: {row['Prev. Entrega']}"
    ]

    y_position = height - margin * 4
    for line in op_info:
        p = Paragraph(line, header_style)
        p.wrapOn(c, width - 2*margin, 20)
        p.drawOn(c, margin, y_position)
        y_position -= 15

    progress_callback.emit(60)

    # Hierarchical Table
    dataframe_onde_usado = consultar_hierarquia_tabela(codigo)

    if not dataframe_onde_usado.empty:
        # Get the list of códigos from dataframe_onde_usado
        codigos_onde_usado = dataframe_onde_usado['Código'].unique()
        codigos_onde_usado = [item.strip() for item in codigos_onde_usado]

        # Filter dataframe_op to only include rows where 'Código' is in codigos_onde_usado
        dataframe_filtrado = dataframe_geral[dataframe_geral['Código'].str.strip().isin(codigos_onde_usado)]

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
            'Unid'
        ]].copy()

        # Rename columns to match the expected format
        dataframe_final = dataframe_final.rename(columns={
            'Código': 'Código Pai',
            'Quantidade_onde_usado': 'Quantidade'
        })

        # Sort the dataframe if needed
        dataframe_final = dataframe_final.sort_values('OP')

        # Generate the table
        table_y_position = y_position - 30
        generate_hierarchical_table(dataframe_final, c, table_y_position)
        progress_callback.emit(80)
    else:
        print(f"No hierarchical data found for código: {row['Código']}")

    # Workflow Image
    workflow_path = get_resource_path('images', 'roteiro.png')
    workflow_y_position = table_y_position - 250
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
        merger.append(output_path)  # First append the production order page
        merger.append(drawing_path)  # Then append the technical drawing

        # Create a temporary file for the merged result
        temp_output = output_path + '.temp'
        merger.write(temp_output)
        merger.close()

        # Replace the original file with the merged result
        os.replace(temp_output, output_path)
        progress_callback.emit(100)
    else:
        # Create a new page with the "Drawing not found" message
        c = canvas.Canvas(output_path + '.temp', pagesize=A4)
        width, height = A4

        c.showPage()
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width/2, height/2, "DESENHO NÃO ENCONTRADO")
        c.save()

        # Merge the original page with the "Drawing not found" page
        merger = PdfMerger()
        merger.append(output_path)
        merger.append(output_path + '.temp')

        temp_output = output_path + '.merged'
        merger.write(temp_output)
        merger.close()

        # Clean up temporary files and replace the original
        os.remove(output_path + '.temp')
        os.replace(temp_output, output_path)
        progress_callback.emit(100)

class PrintProductionOrderDialogV2(QtWidgets.QDialog):
    def __init__(self, df: pd.DataFrame, df_op_table, parent=None):
        super().__init__(parent)
        self.pdf_thread = None
        self.progress_bar = None
        self.layout = None
        self.df = df
        self.df_op_table = df_op_table
        self.init_ui()
        self.print_production_order()

    def init_ui(self):
        self.setWindowTitle("Publicando Ordem de Produção")
        self.setGeometry(100, 100, 400, 100)

        self.layout = QVBoxLayout(self)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.layout.addWidget(self.progress_bar)

        self.setLayout(self.layout)

    def print_production_order(self):
        output_dir = r"\\192.175.175.4\dados\EMPRESA\PRODUCAO\ORDEM_DE_PRODUCAO"
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(output_dir, f"OP_{timestamp}.pdf")

        self.pdf_thread = PDFGeneratorThread(self.df, self.df_op_table, output_path)
        self.pdf_thread.finished.connect(self.on_pdf_generation_complete)
        self.pdf_thread.error.connect(self.on_pdf_generation_error)
        self.pdf_thread.progress.connect(self.update_progress)
        self.pdf_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_pdf_generation_complete(self, path):
        QMessageBox.information(self, "PDF Gerado", f"PDF gerado com sucesso!")
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        self.close()

    def on_pdf_generation_error(self, error):
        QMessageBox.critical(self, "Erro", f"Erro ao gerar PDF: {error}")
        self.close()