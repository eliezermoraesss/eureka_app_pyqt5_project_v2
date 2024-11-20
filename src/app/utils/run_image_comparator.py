import os

from PyQt5.QtCore import QProcess


def run_image_comparator_exe():
    program_path = (r'\\192.175.175.4\desenvolvimento\REPOSITORIOS\imageComparator\dist\ImageComparator_v1.0_built'
                    r'-11122024.exe')
    try:
        os.startfile(program_path)
        print("Programa executado com sucesso!")
    except FileNotFoundError:
        print('O programa não foi encontrado no caminho especificado.')
    except Exception as e:
        print(f"Ocorreu um erro ao executar o programa: {e}")


def run_image_comparator_model(self):
    process = QProcess()
    script_path = os.path.abspath(os.path.join(self.base_dir, 'image_comparator.py'))
    process.startDetached("python", [script_path])  # Usa startDetached para execução
