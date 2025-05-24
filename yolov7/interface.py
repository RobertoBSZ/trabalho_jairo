import customtkinter as ctk
from tkinter import filedialog
import subprocess
import os
from PIL import Image, ImageTk
import sys

# Mostra qual Python está rodando
print(f"[INFO] Python em execução: {sys.executable}")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class YOLOv7App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Detector de Placas YOLOv7")
        self.geometry("800x600")

        self.imagens = []

        self.select_button = ctk.CTkButton(self, text="Selecionar Imagens", command=self.selecionar_imagens)
        self.select_button.pack(pady=10)

        self.detect_button = ctk.CTkButton(self, text="Detectar", command=self.executar_yolo, state="disabled")
        self.detect_button.pack(pady=10)

        self.image_frame = ctk.CTkScrollableFrame(self, width=700, height=400)
        self.image_frame.pack(pady=10)

    def selecionar_imagens(self):
        arquivos = filedialog.askopenfilenames(title="Selecione as imagens", filetypes=[("Imagens", "*.jpg;*.png;*.jpeg")])
        if arquivos:
            self.imagens = arquivos
            self.detect_button.configure(state="normal")

    def executar_yolo(self):
        pasta_temp = "temp_imagens"
        os.makedirs(pasta_temp, exist_ok=True)

        for img in self.imagens:
            nome = os.path.basename(img)
            destino = os.path.join(pasta_temp, nome)
            with open(img, 'rb') as fsrc, open(destino, 'wb') as fdst:
                fdst.write(fsrc.read())

        python_exe = sys.executable
        comando = [
            python_exe, 'detect.py',
            '--weights', 'best.pt',
            '--img', '640',
            '--conf', '0.25',
            '--source', pasta_temp
        ]

        print(f"[INFO] Executando YOLOv7 com: {comando}")

        try:
            subprocess.run(comando, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[ERRO] Falha na execução do detect.py: {e}")
            return

        self.mostrar_resultados()

    def mostrar_resultados(self):
        for widget in self.image_frame.winfo_children():
            widget.destroy()

        pasta_base = "runs/detect"
        pastas = [d for d in os.listdir(pasta_base) if d.startswith("exp")]
        pastas.sort(key=lambda x: int(x[3:]) if x != "exp" else 0, reverse=True)
        ultima_pasta = os.path.join(pasta_base, pastas[0])

        imagens = [os.path.join(ultima_pasta, f) for f in os.listdir(ultima_pasta) if f.lower().endswith(('.jpg', '.png'))]

        for img_path in imagens:
            img = Image.open(img_path)
            img = img.resize((400, 300))
            img_tk = ImageTk.PhotoImage(img)

            label = ctk.CTkLabel(self.image_frame, image=img_tk, text="")
            label.image = img_tk
            label.pack(pady=5)

if __name__ == "__main__":
    app = YOLOv7App()
    app.mainloop()
