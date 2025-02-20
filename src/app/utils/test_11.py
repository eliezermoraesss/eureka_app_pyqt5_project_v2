import subprocess
import os

def imprimir_pdf(caminho_pdf, impressora="Nome_da_Impressora"):
    sumatra_path = r"C:\Program Files\SumatraPDF\SumatraPDF.exe"

    if not os.path.exists(caminho_pdf):
        print("Arquivo PDF não encontrado!")
        return

    comando = [
        sumatra_path,
        "-print-to", impressora,
        "-print-settings", "duplex,portrait",
        caminho_pdf
    ]

    try:
        subprocess.run(comando, check=True)
        print("Impressão enviada com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao imprimir: {e}")

# Caminho da pasta de rede
caminho_pdf = r"\\servidor\pasta\documento.pdf"
imprimir_pdf(caminho_pdf, "Minha_Impressora")
