import os

from PyQt5 import QtWidgets
from PyQt5.QtCore import QUrl, QCoreApplication
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QProgressDialog, QMessageBox

from src.app.utils.pdf_generator import PDFGenerator


def get_image_path(image_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, '..', '..', 'resources', 'images', image_path)


class PrintOPWindowV2(QtWidgets.QDialog):
    def __init__(self, parent=None, dataframe=None):
        super().__init__(parent)
        self.dataframe = dataframe
        self.print_all_ops()

    def print_all_ops(self):
        logo_path = get_image_path('logo_enaplic.jpg')
        roteiro_path = get_image_path('roteiro.png')
        progress = QProgressDialog("Gerando PDFs...", "Cancelar", 0, len(self.dataframe), self)
        progress.setWindowTitle("Processando OPs")
        progress.show()

        output_dir = r"\\192.175.175.4\dados\EMPRESA\PRODUCAO\ORDEM_DE_PRODUCAO"

        try:
            for idx, row in self.dataframe.iterrows():
                if progress.wasCanceled():
                    break

                op_data = {
                    'num_op': row['OP'],
                    'codigo_desenho': row['Código'].strip()
                }

                filename = os.path.join(output_dir, f"OP_{op_data['num_op']}_{op_data['codigo_desenho']}.pdf")
                generator = PDFGenerator(filename, op_data, logo_path, roteiro_path)
                generator.generate()

                progress.setValue(idx + 1)
                QCoreApplication.processEvents()

            QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha na geração: {str(e)}")
        finally:
            progress.close()
