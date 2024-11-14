import webbrowser
import os

from src.app.utils.utils import exibir_janela_mensagem_opcao


def open_dashboard_firefox(url):
    # Possíveis caminhos do Firefox no Windows
    firefox_paths = [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        os.path.expanduser(r"~\AppData\Local\Mozilla Firefox\firefox.exe"),
    ]

    # Tenta encontrar o Firefox
    firefox_path = None
    for path in firefox_paths:
        if os.path.exists(path):
            firefox_path = path
            break

    if firefox_path:
        # Registra o Firefox como navegador
        browser = webbrowser.Mozilla(firefox_path)
        webbrowser.register('firefox', None, browser)

        # Abre a URL no Firefox
        webbrowser.get('firefox').open(url)
    else:
        response = exibir_janela_mensagem_opcao("Atenção", "Firefox não encontrado."
                                                           "\nDeseja abrir o navegador padrão?")
        if response:
            print("Firefox não encontrado. Abrindo no navegador padrão...")
            webbrowser.open(url)
