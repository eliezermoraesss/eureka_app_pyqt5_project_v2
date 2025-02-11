import os

from PyPDF2 import PdfMerger
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from barcode import Code128
from barcode.writer import ImageWriter
import tempfile

from reportlab.platypus import TableStyle, Table


def generate_barcode(data):
    temp_barcode = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    Code128(data, writer=ImageWriter()).write(temp_barcode)
    temp_barcode.close()
    return temp_barcode.name


class PDFGenerator:
    def __init__(self, filename, op_dataframe, logo_path, roteiro_path):
        self.filename = filename
        self.op_dataframe = op_dataframe
        self.logo_path = logo_path
        self.roteiro_path = roteiro_path
        self.c = canvas.Canvas(filename, pagesize=A4)
        self.width, self.height = A4

    def create_header(self):
        # Logo
        self.c.drawImage(self.logo_path, self.width-5*cm, self.height-3*cm,
                         width=4*cm, height=2*cm, preserveAspectRatio=True)

        # Código de barras
        barcode_value = str(self.op_dataframe['num_op'])
        barcode_img = generate_barcode(barcode_value)
        self.c.drawImage(barcode_img, self.width-9*cm, self.height-3*cm,
                         width=4*cm, height=2*cm)

        # Título
        self.c.setFont("Helvetica-Bold", 16)
        self.c.drawString(2*cm, self.height-4*cm, f"ORDEM DE PRODUÇÃO Nº {barcode_value}")

    # TODO: IMPLEMENTAR LÓGICA
    def create_items_table(self):
        data = [["OP", "Código Pai", "Descrição", "Quantidade"]]
        data.extend(self.op_dataframe['itens'])

        table = Table(data, colWidths=[3*cm, 4*cm, 10*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#002060')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('ALIGN', (3,0), (-1,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,1), (-1,-1), 9),
        ]))

        table.wrapOn(self.c, self.width, self.height)
        table.drawOn(self.c, 2*cm, self.height-10*cm)

    def create_roteiro(self):
        if os.path.exists(self.roteiro_path):
            img = ImageReader(self.roteiro_path)
            self.c.drawImage(img, 2*cm, 10*cm,
                             width=self.width-4*cm, height=15*cm,
                             preserveAspectRatio=True)

    def create_verso(self):
        drawing_path = os.path.join(
            r"\\192.175.175.4\dados\EMPRESA\PROJETOS\PDF-OFICIAL",
            f"{self.op_dataframe['codigo_desenho']}.PDF"
        )

        if os.path.exists(drawing_path):
            merger = PdfMerger()
            merger.append(drawing_path)
            merger.write(self.filename)
            merger.close()
        else:
            self.c.showPage()
            self.c.setFont("Helvetica-Bold", 24)
            self.c.drawCentredString(self.width/2, self.height/2, "DESENHO NÃO ENCONTRADO")
            self.c.save()

    def generate(self):
        # Página frontal
        self.create_header()
        # self.create_items_table()
        self.create_roteiro()
        self.c.showPage()
        self.c.save()

        # Página verso
        self.create_verso()