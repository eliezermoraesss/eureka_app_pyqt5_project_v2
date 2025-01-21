import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
import sys
import pandas as pd
import pyperclip

# Caminho absoluto para o diretório onde o módulo src está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt5.QtCore import QCoreApplication, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QMessageBox, QHeaderView, QFileDialog
from src.app.utils.hierarquia_estrutura import BOMViewer as HierarquiaEstruturaWindow
from src.dialog.loading_dialog import loading_dialog


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
        5: 'Armazem: ',
        6: 'Grupo: ',
        7: 'Desc. Grupo: ',
        8: 'Centro Custo: ',
        9: 'Bloqueio: ',
        13: 'Endereco: '
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
    order_by_sc = f"""ORDER BY "SOLIC. COMPRA" DESC;"""

    query_sem_order_by = ""
    if order_by_followup in query_consulta:
        query_sem_order_by = query_consulta.replace(order_by_followup, "")
    elif order_by_sc in query_consulta:
        query_sem_order_by = query_consulta.replace(order_by_sc, "")

    query = f"""
            SELECT 
                COUNT(*) AS total_records
            FROM 
                ({query_sem_order_by}
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


def abrir_hierarquia_estrutura(self, codigo_pai=None):
    if codigo_pai is None:
        selected_row_table = self.linha_selecionada()
        if selected_row_table:
            codigo_index = self.tree.horizontalHeaderItem(0).text().index("Código")
            codigo_pai = selected_row_table[codigo_index]  # Usa o índice encontrado
    dialog = loading_dialog(self, "Eureka® Engenharia", "🤖 Consultando dados...\n\nPor favor, aguarde!")
    hierarquia_estrutura_window = HierarquiaEstruturaWindow(codigo_pai)
    hierarquia_estrutura_window.showMaximized()
    dialog.close()
    hierarquia_estrutura_window.raise_()
    hierarquia_estrutura_window.activateWindow()
