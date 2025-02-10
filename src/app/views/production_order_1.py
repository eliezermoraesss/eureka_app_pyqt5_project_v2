import os
import locale
import sys
from datetime import datetime
from typing import List, Dict

import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QTableWidget,
                             QTableWidgetItem, QLabel, QPushButton, QFileDialog,
                             QProgressDialog, QHeaderView, QCheckBox)
from PyQt5.QtCore import Qt, QThread, QObject, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.graphics.barcode import code128
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

import qrcode
from PIL import Image

class PDFGeneratorThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, data: List[Dict], output_path: str):
        super().__init__()
        self.data = data
        self.output_path = output_path

    def run(self):
        try:
            generate_production_order_pdf(self.data, self.output_path)
            self.finished.emit(self.output_path)
        except Exception as e:
            self.error.emit(str(e))

def generate_qr_code(data: str, size: int = 10) -> str:
    """Gera um código QR e retorna o caminho para a imagem"""
    qr = qrcode.QRCode(version=1, box_size=size, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    temp_qr_path = os.path.join(script_dir, '..', 'resources', 'images', 'barcode.png')
    return temp_qr_path

def get_company_logo_path():
    """Retorna o caminho do logo da empresa"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, '..', 'resources', 'images', 'logo_enaplic.jpg')

def generate_production_order_pdf(data: List[Dict], output_path: str):
    """Gera PDF da Ordem de Produção"""
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Margens reduzidas
    margin = 15 * mm

    # Cabeçalho
    logo_path = get_company_logo_path()
    c.drawImage(logo_path, margin, height - margin * 2, width=50, preserveAspectRatio=True)

    # QR Code / Código de Barras
    qr_path = generate_qr_code(str(data[0]['OP']))
    c.drawImage(qr_path, width - margin * 4, height - margin * 2, width=50, preserveAspectRatio=True)

    # Informações da Ordem de Produção
    styles = getSampleStyleSheet()
    op_info = [
        f"OP: {data[0]['OP']}",
        f"Produto: {data[0]['Código']} - {data[0]['Descrição']}",
        f"Quantidade: {data[0]['Quantidade']}",
        f"Data Abertura: {data[0]['Data Abertura']}",
        f"Previsão Entrega: {data[0]['Prev. Entrega']}"
    ]

    y_position = height - margin * 4
    for line in op_info:
        p = Paragraph(line, styles['Normal'])
        p.wrapOn(c, width - 2*margin, 20)
        p.drawOn(c, margin, y_position)
        y_position -= 15

    # Limpar recursos temporários
    if os.path.exists(qr_path):
        os.remove(qr_path)

    c.showPage()
    c.save()

class PrintProductionOrderDialog(QtWidgets.QDialog):
    def __init__(self, dataframe: pd.DataFrame, parent=None):
        super().__init__(parent)
        self.dataframe = dataframe

        # Layout
        main_layout = QHBoxLayout()

        # Tabela de resultados (esquerda)
        self.results_table = QTableWidget()
        self.setup_results_table()

        # Área de configuração (direita)
        config_layout = QVBoxLayout()

        # Opções de seleção
        self.manual_selection_radio = QCheckBox("Seleção Manual")
        self.op_range_radio = QCheckBox("Intervalo de OP")
        self.date_range_radio = QCheckBox("Intervalo de Data")

        config_layout.addWidget(self.manual_selection_radio)
        config_layout.addWidget(self.op_range_radio)
        config_layout.addWidget(self.date_range_radio)

        # Botões
        buttons_layout = QHBoxLayout()
        self.close_btn = QPushButton("Fechar")
        self.print_btn = QPushButton("Imprimir")

        buttons_layout.addWidget(self.close_btn)
        buttons_layout.addWidget(self.print_btn)

        config_layout.addStretch()
        config_layout.addLayout(buttons_layout)

        # Layout principal
        main_layout.addWidget(self.results_table, 2)
        main_layout.addLayout(config_layout, 1)

        self.setLayout(main_layout)

        # Conectar sinais
        self.close_btn.clicked.connect(self.close)
        self.print_btn.clicked.connect(self.print_production_order)

    def setup_results_table(self):
        self.results_table.setColumnCount(len(self.dataframe.columns))
        self.results_table.setHorizontalHeaderLabels(self.dataframe.columns)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setSelectionMode(QTableWidget.MultiSelection)

        for i, (index, row) in enumerate(self.dataframe.iterrows()):
            self.results_table.insertRow(i)
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.results_table.setItem(i, j, item)

    def print_production_order(self):
        # Lógica de impressão da ordem de produção
        selected_rows = set(index.row() for index in self.results_table.selectedIndexes())

        if not selected_rows:
            # Lógica para lidar com nenhuma seleção
            return

        # Preparar dados para impressão
        selected_data = self.dataframe.iloc[list(selected_rows)].to_dict('records')

        # Definir caminho de saída
        output_dir = r"\\192.175.175.4\dados\EMPRESA\PRODUCAO\ORDEM_DE_PRODUCAO"
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, f"OP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

        # Iniciar thread de geração de PDF
        self.pdf_thread = PDFGeneratorThread(selected_data, output_path)
        self.pdf_thread.finished.connect(self.on_pdf_generation_complete)
        self.pdf_thread.error.connect(self.on_pdf_generation_error)
        self.pdf_thread.start()

    def on_pdf_generation_complete(self, path):
        # Lógica após geração do PDF (abrir, mostrar mensagem)
        print(f"PDF gerado em: {path}")

    def on_pdf_generation_error(self, error):
        # Tratar erros na geração do PDF
        print(f"Erro na geração do PDF: {error}")
