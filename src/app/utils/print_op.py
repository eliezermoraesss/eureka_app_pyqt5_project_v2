import os
from datetime import datetime

import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (QVBoxLayout, QMessageBox, QProgressBar)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from src.app.utils.generate_barcode import generate_barcode


class PDFGeneratorThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, df: pd.DataFrame, output_path: str):
        super().__init__()
        self.df = df
        self.output_path = output_path

    def run(self):
        try:
            generate_production_order_pdf(self.df, self.output_path, self.progress)
            self.finished.emit(self.output_path)
        except Exception as e:
            self.error.emit(str(e))

def get_company_logo_path():
    """Retorna o caminho do logo da empresa"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, '..', '..', 'resources', 'images', 'logo_enaplic.jpg')

def generate_production_order_pdf(df: pd.DataFrame, output_path: str, progress_callback):
    """Gera PDF da Ordem de Produção"""
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Margens reduzidas
    margin = 15 * mm

    # Cabeçalho
    logo_path = get_company_logo_path()
    c.drawImage(logo_path, margin, height - margin * 2, width=50, preserveAspectRatio=True)

    # Código de Barras
    barcode_path = generate_barcode('teste_op')
    c.drawImage(barcode_path, width - margin * 4, height - margin * 2, width=50, preserveAspectRatio=True)

    # Informações da Ordem de Produção
    styles = getSampleStyleSheet()
    op_info = [
        f"OP: {df.iloc[0]['OP']}",
        f"Produto: {df.iloc[0]['Código']} - {df.iloc[0]['Descrição']}",
        f"Quantidade: {df.iloc[0]['Quantidade']}",
        f"Data Abertura: {df.iloc[0]['Data Abertura']}",
        f"Previsão Entrega: {df.iloc[0]['Prev. Entrega']}"
    ]

    y_position = height - margin * 4
    for line in op_info:
        p = Paragraph(line, styles['Normal'])
        p.wrapOn(c, width - 2*margin, 20)
        p.drawOn(c, margin, y_position)
        y_position -= 15

    # Limpar recursos temporários
    if os.path.exists(barcode_path):
        os.remove(barcode_path)

    c.showPage()
    c.save()

    # Emit progress
    progress_callback.emit(100)


class PrintProductionOrderDialog(QtWidgets.QDialog):
    def __init__(self, df: pd.DataFrame, parent=None):
        super().__init__(parent)
        self.progress_bar = None
        self.layout = None
        self.pdf_thread = None
        self.df = df
        self.init_ui()
        self.print_production_order()

    def init_ui(self):
        self.setWindowTitle("Publicando Ordem de Produção")
        self.setGeometry(100, 100, 400, 200)

        self.layout = QVBoxLayout(self)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.layout.addWidget(self.progress_bar)

        self.setLayout(self.layout)

    def print_production_order(self):
        # Definir caminho de saída
        output_dir = r"\\192.175.175.4\dados\EMPRESA\PRODUCAO\ORDEM_DE_PRODUCAO"
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, f"OP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

        # Iniciar thread de geração de PDF
        self.pdf_thread = PDFGeneratorThread(self.df, output_path)
        self.pdf_thread.finished.connect(self.on_pdf_generation_complete)
        self.pdf_thread.error.connect(self.on_pdf_generation_error)
        self.pdf_thread.progress.connect(self.update_progress)
        self.pdf_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_pdf_generation_complete(self, path):
        # Lógica após geração do PDF (abrir, mostrar mensagem)
        QMessageBox.information(self, "PDF Gerado", f"PDF gerado em: {path}")
        self.close()

    def on_pdf_generation_error(self, error):
        # Tratar erros na geração do PDF
        QMessageBox.critical(self, "Erro na Geração do PDF", f"Erro na geração do PDF: {error}")
        self.close()
