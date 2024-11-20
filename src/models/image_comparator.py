import os
import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import ttk

import cv2
import pyautogui


class ImageComparatorApp:
    def __init__(self, window):
        self.log_text = None
        self.root = window
        self.root.title("ImageComparator®")

        # Adicionar ícone personalizado
        icon_path = "image-comparator.ico"  # Substitua pelo caminho do seu ícone .ico
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        # Define o caminho padrão para salvar as imagens
        self.image_folder = os.path.join(os.path.expanduser("~"), "Pictures", "ImageCompare")
        os.makedirs(self.image_folder, exist_ok=True)  # Cria a pasta se não existir

        self.sensitivity = tk.IntVar(value=0)

        # Layout ajustado
        self.create_layout()

        # Armazena os caminhos das imagens
        self.image1_path = ""
        self.image2_path = ""
        self.diff_image_path = ""

    def create_layout(self):
        """Configura o layout da interface"""
        # Título
        title_label = ttk.Label(self.root, text="ImageComparator®", font=("Segoe UI", 18, "bold"))
        title_label.pack(pady=20)

        # Primeira linha de botões (Capturar Imagem 1 e Capturar Imagem 2)
        capture_buttons_frame = ttk.Frame(self.root)
        capture_buttons_frame.pack(pady=10)

        ttk.Button(capture_buttons_frame, text="Capturar Imagem 1", command=self.capture_image1, width=20).pack(
            side="left", padx=10)
        ttk.Button(capture_buttons_frame, text="Capturar Imagem 2", command=self.capture_image2, width=20).pack(
            side="left", padx=10)

        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 10, "normal"))
        style.configure("Compare.TButton", font=("Segoe UI", 12, "normal"))

        compare_button = ttk.Button(self.root, text="COMPARAR", command=self.compare_images, width=33,
                                    padding=(10, 20), style="Compare.TButton")
        compare_button.pack(pady=10)

        # Ajuste de Sensibilidade
        ttk.Label(self.root, text="Ajuste a Sensibilidade:").pack(pady=5)
        ttk.Scale(self.root, from_=0, to=100, orient="horizontal", variable=self.sensitivity).pack(pady=5)

        self.log_text = tk.Text(self.root, wrap="word", height=10, state="disabled", bg="white", fg="black", width=59)
        self.log_text.pack(pady=10)

        # Segunda linha de botões (Abrir Imagem 1, Abrir Imagem 2 e Abrir Comparação)
        open_buttons_frame = ttk.Frame(self.root)
        open_buttons_frame.pack(pady=10)

        ttk.Button(open_buttons_frame, text="Abrir Imagem 1", command=self.show_image1, width=20).pack(
            side="left", padx=10)
        ttk.Button(open_buttons_frame, text="Abrir Imagem 2", command=self.show_image2, width=20).pack(
            side="left", padx=10)
        ttk.Button(open_buttons_frame, text="Abrir Comparação", command=self.show_difference, width=20).pack(
            side="left", padx=10)

        # Rodapé com créditos
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(side="bottom", pady=10)

        ttk.Label(footer_frame, text="Created by ").pack(side="left", padx=5)
        # ttk.Button(footer_frame, text="GitHub", command=self.open_github).pack(side="left", padx=5)

        github_link = ttk.Label(footer_frame, text="Eliezer Moraes Silva", foreground="blue", cursor="hand2")
        github_link.pack(side="left", padx=5)
        github_link.bind("<Button-1>", lambda e: self.open_github())

        ttk.Label(footer_frame, text=" v1.0_built-11122024").pack(side="left", padx=5)

    def log_message(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", "\n" + message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def open_github(self):
        """Abre o link do GitHub no navegador"""
        webbrowser.open("https://github.com/eliezermoraesss")

    def generate_filename(self, base_name):
        # Gera o nome do arquivo com data e hora atuais
        timestamp = datetime.now().strftime("%d-%m-%Y_%H%M%S")
        return os.path.join(self.image_folder, f"{base_name}_{timestamp}.png")

    def capture_image1(self):
        self.image1_path = self.generate_filename("image1")
        self.capture_screenshot(self.image1_path)
        self.log_message(f"IMAGEM 1 capturada e salva em: {self.image1_path}")

    def capture_image2(self):
        self.image2_path = self.generate_filename("image2")
        self.capture_screenshot(self.image2_path)
        self.log_message(f"IMAGEM 2 capturada e salva em: {self.image2_path}")

    def capture_screenshot(self, filename):
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)

    def preprocess_image(self, image_path):
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        return gray

    def compare_images(self):
        if not self.image1_path or not self.image2_path:
            self.log_message("Capture ambas as imagens antes de comparar.")
            return

        threshold_value = self.sensitivity.get()
        self.diff_image_path = self.generate_filename("output_diff")
        self.find_differences(self.image1_path, self.image2_path, self.diff_image_path, threshold_value)
        self.log_message(f"COMPARAÇÃO salva em: {self.diff_image_path}")

        # Abre a imagem de diferença automaticamente
        if os.path.exists(self.diff_image_path):
            os.startfile(self.diff_image_path)

    def find_differences(self, image1_path, image2_path, output_path, threshold_value):
        gray1 = self.preprocess_image(image1_path)
        gray2 = self.preprocess_image(image2_path)

        diff = cv2.absdiff(gray1, gray2)
        _, thresh = cv2.threshold(diff, threshold_value, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        image1 = cv2.imread(image1_path)
        for contour in contours:
            if cv2.contourArea(contour) > 10:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(image1, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imwrite(output_path, image1)

    def show_image1(self):
        if os.path.exists(self.image1_path):
            os.startfile(self.image1_path)
        else:
            self.log_message("A IMAGEM 1 ainda não foi capturada.")

    def show_image2(self):
        if os.path.exists(self.image2_path):
            os.startfile(self.image2_path)
        else:
            self.log_message("A IMAGEM 2 ainda não foi capturada.")

    def show_difference(self):
        if os.path.exists(self.diff_image_path):
            os.startfile(self.diff_image_path)
        else:
            self.log_message("A COMPARAÇÃO ainda não foi calculada.\n\nCapture as imagens!")


if __name__ == "__main__":
    # Inicializa a aplicação
    root = tk.Tk()
    app = ImageComparatorApp(root)

    # Configurações para desabilitar redimensionamento
    root.resizable(False, False)
    root.geometry('500x560')  # Ajusta o tamanho da janela
    root.mainloop()
