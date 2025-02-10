from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from barcode import Code128
from barcode.writer import ImageWriter
import tempfile

class PDFGenerator:
    def __init__(self, filename, ops_data, logo_path, roteiro_path):
        self.c = canvas.Canvas(filename, pagesize=A4)
        self.width, self.height = A4
        self.ops_data = ops_data
        self.logo_path = logo_path
        self.roteiro_path = roteiro_path

    def create_header(self, op_number):
        # Logo
        self.c.drawImage(self.logo_path, 1*cm, self.height-3*cm, width=4*cm, height=2*cm)

        # Código de barras
        barcode_file = self.create_barcode(op_number)
        self.c.drawImage(barcode_file, 16*cm, self.height-3*cm, width=4*cm, height=2*cm)

    def create_barcode(self, data):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
            Code128(str(data), writer=ImageWriter()).write(f)
            return f.name

    def create_table(self, data):
        # Configurar coordenadas e dimensões da tabela
        col_widths = [3*cm, 4*cm, 8*cm, 3*cm]
        x_start = 1*cm
        y_start = self.height - 5*cm

        # Cabeçalho
        headers = ["OP", "Código Pai", "Descrição", "Quantidade"]
        for i, header in enumerate(headers):
            self.c.drawString(x_start + sum(col_widths[:i]), y_start, header)

        # Dados
        y = y_start - 0.5*cm
        for row in data:
            for i, value in enumerate(row):
                self.c.drawString(x_start + sum(col_widths[:i]), y, str(value))
            y -= 0.5*cm

    def generate(self):
        for op in self.ops_data:
            # Frente
            self.create_header(op['num_op'])
            self.create_table(op['itens'])
            self.c.showPage()

            # Verso
            self.c.drawImage(self.roteiro_path, 0, 0, width=self.width, height=self.height)
            self.c.showPage()

        self.c.save()