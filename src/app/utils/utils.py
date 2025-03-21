import os
import tempfile
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
import sys
import pandas as pd
import pyperclip
from barcode import Code128
from barcode.writer import ImageWriter

# Caminho absoluto para o diretório onde o módulo src está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt5.QtCore import QCoreApplication, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QMessageBox, QHeaderView, QFileDialog
from src.dialog.information_dialog import information_dialog


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


def exibir_janela_mensagem_opcao(titulo, mensagem):
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal
    root.attributes('-topmost', True)  # Garante que a janela estará sempre no topo
    root.lift()  # Traz a janela para frente
    root.focus_force()  # Força o foco na janela

    # Mostrar a mensagem
    user_choice = messagebox.askquestion(
        titulo,
        mensagem,
        parent=root  # Define a janela principal como pai da mensagem
    )

    # Fechar a janela principal após a escolha do usuário
    root.destroy()

    if user_choice == "yes":
        return True
    else:
        return False


def copiar_linha(item):
    # Verificar se um item foi clicado
    if item is not None:
        valor_campo = item.text()
        pyperclip.copy(str(valor_campo))


def abrir_desenho(self, table=None, codigo_param=None):
    codigo_desenho = ''
    if table is not None:
        item_selecionado = table.currentItem()
    else:
        item_selecionado = ''

    if item_selecionado or codigo_param:
        if table is not None:
            header = table.horizontalHeader()
            codigo_col = None

            for col in range(header.count()):
                header_text = table.horizontalHeaderItem(col).text().lower()
                if header_text == 'código':
                    codigo_col = col

                if codigo_col is not None:
                    codigo = table.item(item_selecionado.row(), codigo_col).text()
                    codigo_desenho = codigo
        else:
            codigo_desenho = codigo_param

        pdf_path = os.path.join(r"\\192.175.175.4\dados\EMPRESA\PROJETOS\PDF-OFICIAL", f"{codigo_desenho}.PDF")
        pdf_path = os.path.normpath(pdf_path)

        if os.path.exists(pdf_path):
            QCoreApplication.processEvents()
            QDesktopServices.openUrl(QUrl.fromLocalFile(pdf_path))
        else:
            mensagem = f"Desenho não encontrado!\n\n:-("
            QMessageBox.information(self, f"{codigo_desenho}", mensagem)

def open_op(self, table):
    op_code = ''
    product_code = ''
    item_selecionado = table.currentItem()

    if item_selecionado:
        header = table.horizontalHeader()
        op_col = None
        product_col = None

        for col in range(header.count()):
            header_text = table.horizontalHeaderItem(col).text().lower()
            if header_text == 'código':
                product_col = col
            elif header_text == 'op':
                op_col = col

            if product_col is not None:
                codigo = table.item(item_selecionado.row(), product_col).text()
                product_code = codigo
            elif op_col is not None:
                op = table.item(item_selecionado.row(), op_col).text()
                op_code = op

        pdf_path = os.path.join(r"\\192.175.175.4\dados\EMPRESA\PRODUCAO\ORDEM_DE_PRODUCAO", f"OP_{op_code}_{product_code}.pdf")
        pdf_path = os.path.normpath(pdf_path)

        if os.path.exists(pdf_path):
            QCoreApplication.processEvents()
            QDesktopServices.openUrl(QUrl.fromLocalFile(pdf_path))
        else:
            title = f"Eureka® PCP - OP {op_code}"
            message = f"OP não encontrada!\n🙁"
            information_dialog(self, title, message)

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

        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Dados', index=False)

        worksheet = writer.sheets['Dados']

        for i, col in enumerate(df.columns):
            max_len = df[col].astype(str).map(len).max()
            worksheet.set_column(i, i, max_len + 2)

        writer.close()

        os.startfile(file_path)


def format_log_description(selected_row_before_changed, selected_row_after_changed):
    before_change = {}
    after_change = {}
    column_names = {
        1: 'Descricao: ',
        2: 'Desc. Compl.: ',
        3: 'Tipo: ',
        4: 'Unid. Med.: ',
        6: 'Armazem: ',
        7: 'Grupo: ',
        8: 'Desc. Grupo: ',
        9: 'Centro Custo: ',
        10: 'Bloqueio: ',
        15: 'Endereco: ',
        16: 'NCM: ',
        17: 'Peso Líq.: '
    }
    for value in selected_row_after_changed:
        if value not in selected_row_before_changed:
            index = selected_row_after_changed.index(value)
            after_change[index] = value
    for value in selected_row_before_changed:
        if value not in selected_row_after_changed:
            index = selected_row_before_changed.index(value)
            before_change[index] = value
    result = 'Antes:\n'
    for key, value in before_change.items():
        result += column_names[key] + value + '\n'
    result += '\nDepois:\n'
    for key, value in after_change.items():
        result += column_names[key] + value + '\n'
    return result


def numero_linhas_consulta(query_consulta):
    order_by_followup = f"""ORDER BY PC.R_E_C_N_O_ DESC;"""
    query_count = query_consulta.replace(order_by_followup, "")

    query = f"""
            SELECT 
                COUNT(*) AS total_records
            FROM 
                ({query_count}
                )
            AS combined_results;
        """
    return query


def tratar_campo_codigo(campo):
    return campo.text().upper().strip().replace(" ", "").replace("\n", "")


def formatar_campo(campo):
    return campo.text().upper().strip()


def format_cnpj(cnpj):
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"  # Saída: 12.345.678/9012-34


def abrir_tabela_pesos():
    os.startfile(r'\\192.175.175.4\desenvolvimento\REPOSITORIOS\resources\assets\excel\TABELA_PESO.xlsx')


def obter_codigo_item_selecionado(table):
    item_selecionado = table.currentItem()

    header = table.horizontalHeader()
    for col in range(header.count()):
        header_text = table.horizontalHeaderItem(col).text().lower()
        if header_text == 'código':
            codigo_desenho = table.item(item_selecionado.row(), col).text()
            return codigo_desenho

def generate_barcode(data):
    temp_barcode = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    Code128(data, writer=ImageWriter()).write(temp_barcode)
    temp_barcode.close()
    return temp_barcode.name
