import os
from datetime import datetime

from PyQt5 import QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QVBoxLayout, QTableView, QRadioButton, QLineEdit, QDateEdit, \
    QDialogButtonBox, QLabel, QProgressDialog, QMessageBox

from src.app.utils.print_op_v2 import PDFGenerator


class PrintOPWindowV2(QtWidgets.QDialog):
    def __init__(self, parent=None, dataframe=None):
        super().__init__(parent)
        self.dataframe = dataframe
        self.selected_ops = []
        self.initUI()
        self.load_data()

    def initUI(self):
        self.setWindowTitle("Impressão de Ordens de Produção")
        self.resize(1200, 600)

        # Layout principal
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Container esquerdo (Tabela)
        left_container = QWidget()
        left_layout = QVBoxLayout()
        self.table = QTableView()
        left_layout.addWidget(self.table)
        left_container.setLayout(left_layout)

        # Container direito (Opções)
        right_container = QWidget()
        right_layout = QVBoxLayout()

        # Opções de seleção
        self.manual_radio = QRadioButton("Seleção manual")
        self.range_radio = QRadioButton("Intervalo de OPs")
        self.date_radio = QRadioButton("Intervalo de datas")

        # Campos para intervalos
        self.op_start = QLineEdit()
        self.op_end = QLineEdit()
        self.date_start = QDateEdit()
        self.date_end = QDateEdit()

        # Botões
        btn_box = QDialogButtonBox()
        self.print_btn = btn_box.addButton("Imprimir", QDialogButtonBox.AcceptRole)
        self.close_btn = btn_box.addButton("Fechar", QDialogButtonBox.RejectRole)

        # Adicionar componentes ao layout direito
        right_layout.addWidget(self.manual_radio)
        right_layout.addWidget(self.range_radio)
        right_layout.addWidget(QLabel("De OP:"))
        right_layout.addWidget(self.op_start)
        right_layout.addWidget(QLabel("Até OP:"))
        right_layout.addWidget(self.op_end)
        right_layout.addWidget(self.date_radio)
        right_layout.addWidget(QLabel("De data:"))
        right_layout.addWidget(self.date_start)
        right_layout.addWidget(QLabel("Até data:"))
        right_layout.addWidget(self.date_end)
        right_layout.addStretch()
        right_layout.addWidget(btn_box)

        right_container.setLayout(right_layout)

        main_layout.addWidget(left_container, 70)
        main_layout.addWidget(right_container, 30)

        # Conexões
        self.manual_radio.toggled.connect(self.toggle_selection_mode)
        self.print_btn.clicked.connect(self.generate_pdf)
        self.close_btn.clicked.connect(self.close)

    def load_data(self):
        # Implementar carregamento dos dados na tabela
        model = PandasModel(self.dataframe)
        self.table.setModel(model)
        self.table.setSelectionMode(QTableView.MultiSelection)
        self.table.setSelectionBehavior(QTableView.SelectRows)

    def generate_pdf(self):
        # Obter OPs selecionadas
        selected_ops = self.get_selected_ops()

        # Configurar progresso
        progress = QProgressDialog("Gerando PDF...", "Cancelar", 0, len(selected_ops), self)
        progress.setWindowTitle("Publicando OPs")
        progress.show()

        # Gerar PDF
        try:
            output_dir = r"\\192.175.175.4\dados\EMPRESA\PRODUCAO\ORDEM_DE_PRODUCAO"
            filename = os.path.join(output_dir, f"OP_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")

            generator = PDFGenerator(
                filename,
                self.prepare_op_data(selected_ops),
                "caminho/para/logo.png",
                "caminho/para/roteiro.png"
            )

            generator.generate()

            # Abrir PDF após criação
            QDesktopServices.openUrl(QUrl.fromLocalFile(filename))

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar PDF: {str(e)}")
        finally:
            progress.close()