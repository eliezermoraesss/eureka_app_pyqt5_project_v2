# Caminho absoluto para o diretório onde o módulo src está localizado
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.app.views.solic_compras_window import SolicitacaoComprasWindow
from src.models.engenharia_model import EngenhariaApp

from src.models.pcp_model import PcpApp


def executar_consulta_solic_compras():
    solic_compras_window = SolicitacaoComprasWindow()
    solic_compras_window.showMaximized()


def abrir_modulo_engenharia():
    eng_window = EngenhariaApp()
    eng_window.showMaximized()


def abrir_modulo_pcp():
    pcp_window = PcpApp()
    pcp_window.showMaximized()
