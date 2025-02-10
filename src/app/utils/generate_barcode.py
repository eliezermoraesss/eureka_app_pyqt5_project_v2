import os

import barcode
from barcode.writer import ImageWriter


def generate_barcode(text):
    """
    Gera um código de barras Code-128 a partir de uma string.

    Parâmetros:
    - text: String a ser convertida em código de barras

    Retorna o caminho do arquivo gerado
    """
    try:
        # Cria o código de barras Code-128
        code128 = barcode.get_barcode_class('code128')

        # Gera o código de barras
        generated_barcode = code128(text, writer=ImageWriter())

        # Obtém o caminho da pasta temporária
        temp_dir = os.getenv('TEMP')

        # Define o caminho completo do arquivo
        full_filename = os.path.join(temp_dir, f"{text}_barcode")

        # Salva o código de barras
        full_filename = generated_barcode.save(full_filename)

        print(f"Código de barras gerado com sucesso: {full_filename}")
        return full_filename

    except Exception as e:
        print(f"Erro ao gerar código de barras: {e}")
        return None
