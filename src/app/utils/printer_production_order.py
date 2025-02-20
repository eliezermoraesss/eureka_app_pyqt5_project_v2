import fitz  # PyMuPDF
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QImage, QTransform
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog


class PrinterProductionOrder(QtWidgets.QDialog):
    def __init__(self, generated_pdf_paths):
        super().__init__()
        self.generated_pdf_paths = generated_pdf_paths

        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.A4)
        printer.setOutputFormat(QPrinter.NativeFormat)
        printer.setDuplex(QPrinter.DuplexAuto)

        print_dialog = QPrintDialog(printer)
        if print_dialog.exec_() == QPrintDialog.Accepted:
            try:
                for pdf_path in self.generated_pdf_paths:
                    document = fitz.open(pdf_path)
                    painter = QPainter(printer)

                    for page_number in range(document.page_count):
                        page = document.load_page(page_number)
                        zoom = 6.0  # Increase the zoom factor to improve resolution
                        mat = fitz.Matrix(zoom, zoom)
                        pix = page.get_pixmap(matrix=mat)

                        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)

                        if img.width() > img.height():
                            img = img.transformed(QTransform().rotate(90))

                        rect = painter.viewport()
                        scaled_size = img.size().scaled(rect.size(), Qt.KeepAspectRatio)
                        painter.setViewport(rect.x(), rect.y(), scaled_size.width(), scaled_size.height())
                        painter.setWindow(img.rect())

                        painter.drawImage(0, 0, img)

                        if page_number < document.page_count - 1:
                            printer.newPage()

                    painter.end()
            except Exception:
                raise
