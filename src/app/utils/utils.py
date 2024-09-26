import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

import pandas as pd
import pyperclip
from PyQt5.QtCore import QCoreApplication, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QMessageBox, QHeaderView, QFileDialog


def abrir_nova_janela(self, models):
    if not self.nova_janela or not self.nova_janela.isVisible():
        self.nova_janela = models
        self.nova_janela.setGeometry(self.x() + 50, self.y() + 50, self.width(), self.height())
        self.nova_janela.show()


def exibir_mensagem(title, message, icon_type):
    root = tk.Tk()
    root.withdraw()
    root.lift()  # Garante que a janela esteja na frente
    root.title(title)
    root.attributes('-topmost', True)

    if icon_type == 'info':
        messagebox.showinfo(title, message)
    elif icon_type == 'warning':
        messagebox.showwarning(title, message)
    elif icon_type == 'error':
        messagebox.showerror(title, message)

    root.destroy()


def copiar_linha(item):
    # Verificar se um item foi clicado
    if item is not None:
        valor_campo = item.text()
        pyperclip.copy(str(valor_campo))


def abrir_desenho(self, table):
    item_selecionado = table.currentItem()
    header = table.horizontalHeader()
    codigo_col = None
    codigo = None

    for col in range(header.count()):
        header_text = table.horizontalHeaderItem(col).text()
        if header_text == 'Código':
            codigo_col = col

        if codigo_col is not None:
            codigo = table.item(item_selecionado.row(), codigo_col).text()

    if item_selecionado:
        pdf_path = os.path.join(r"\\192.175.175.4\dados\EMPRESA\PROJETOS\PDF-OFICIAL", f"{codigo}.PDF")
        pdf_path = os.path.normpath(pdf_path)

        if os.path.exists(pdf_path):
            QCoreApplication.processEvents()
            QDesktopServices.openUrl(QUrl.fromLocalFile(pdf_path))
        else:
            mensagem = f"Desenho não encontrado!\n\n:-("
            QMessageBox.information(self, f"{codigo}", mensagem)


def ajustar_largura_coluna_descricao(tree_widget):
    header = tree_widget.horizontalHeader()
    header.setSectionResizeMode(1, QHeaderView.ResizeToContents)


def obter_dados_tabela(table):
    # Obter os dados da tabela
    data = []
    for i in range(table.rowCount()):
        row_data = []
        for j in range(table.columnCount()):
            item = table.item(i, j)
            if item is not None:
                row_data.append(item.text())
            else:
                row_data.append("")
        data.append(row_data)
    return data


def exportar_excel(self, table=None):

    desktop_path = os.path.join(os.path.expanduser("~"), 'Desktop')

    now = datetime.now()
    default_filename = f'report_{now.today().strftime('%Y-%m-%d_%H%M%S')}.xlsx'

    file_path, _ = QFileDialog.getSaveFileName(self, 'Salvar como', os.path.join(desktop_path, default_filename),
                                               'Arquivos Excel (*.xlsx);;Todos os arquivos (*)')

    if file_path:
        data = obter_dados_tabela(table)
        column_headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
        df = pd.DataFrame(data, columns=column_headers)

        if 'Quantidade' in column_headers:
            numeric_columns = ['Quantidade']
            df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Dados', index=False)

        worksheet = writer.sheets['Dados']

        for i, col in enumerate(df.columns):
            max_len = df[col].astype(str).map(len).max()
            worksheet.set_column(i, i, max_len + 2)

        writer.close()

        os.startfile(file_path)
