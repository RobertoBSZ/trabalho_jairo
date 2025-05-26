import customtkinter as ctk
from tkinter import filedialog
import subprocess
import os
from PIL import Image, ImageTk
import sys
import shutil
import cv2
from threading import Thread

print(f"[INFO] Python em execução: {sys.executable}")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class YOLOv7App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Detector de Placas YOLOv7")
        self.geometry("800x600")

        self.arquivos = []

        self.select_button = ctk.CTkButton(self, text="Selecionar Arquivos (Imagem ou Vídeo)", command=self.selecionar_arquivos)
        self.select_button.pack(pady=10)

        self.detect_button = ctk.CTkButton(self, text="Detectar", command=self.executar_yolo, state="disabled")
        self.detect_button.pack(pady=10)

        self.image_frame = ctk.CTkScrollableFrame(self, width=700, height=400)
        self.image_frame.pack(pady=10)

    def selecionar_arquivos(self):
        arquivos = filedialog.askopenfilenames(title="Selecione arquivos", 
                                               filetypes=[("Arquivos de Mídia", "*.jpg;*.png;*.jpeg;*.mp4;*.avi;*.mov")])
        if arquivos:
            self.arquivos = arquivos
            self.detect_button.configure(state="normal")

    def executar_yolo(self):
        imagens = [f for f in self.arquivos if os.path.splitext(f)[1].lower() in ['.jpg', '.jpeg', '.png']]
        videos = [f for f in self.arquivos if os.path.splitext(f)[1].lower() in ['.mp4', '.avi', '.mov']]

        if imagens:
            pasta_temp = "temp_imagens"
            if os.path.exists(pasta_temp):
                shutil.rmtree(pasta_temp)
            os.makedirs(pasta_temp, exist_ok=True)

            for img in imagens:
                nome = os.path.basename(img)
                destino = os.path.join(pasta_temp, nome)
                shutil.copy2(img, destino)

            self.executar_detect(pasta_temp)
            self.mostrar_resultados()

        for video in videos:
            self.executar_detect(video)

            # Correção: pegar vídeo processado
            processed_video = self.pegar_video_processado()
            if processed_video:
                self.mostrar_video(processed_video)
            else:
                print(f"[ERRO] Não foi possível encontrar o vídeo processado para {video}")

    def executar_detect(self, source):
        python_exe = sys.executable
        comando = [
            python_exe, 'detect.py',
            '--weights', 'best.pt',
            '--img', '640',
            '--conf', '0.25',
            '--source', source
        ]
        print(f"[INFO] Executando YOLOv7 com: {comando}")
        try:
            subprocess.run(comando, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[ERRO] Falha na execução do detect.py: {e}")

    def mostrar_resultados(self):
        for widget in self.image_frame.winfo_children():
            widget.destroy()

        pasta_base = "runs/detect"
        pastas = [d for d in os.listdir(pasta_base) if d.startswith("exp")]
        pastas.sort(key=lambda x: int(x[3:]) if x != "exp" else 0, reverse=True)
        ultima_pasta = os.path.join(pasta_base, pastas[0])

        arquivos = [os.path.join(ultima_pasta, f) for f in os.listdir(ultima_pasta)]

        for arq in arquivos:
            if arq.lower().endswith(('.jpg', '.png')):
                img = Image.open(arq)
                img = img.resize((400, 300))
                img_tk = ImageTk.PhotoImage(img)
                label = ctk.CTkLabel(self.image_frame, image=img_tk, text="")
                label.image = img_tk
                label.pack(pady=5)

    def pegar_video_processado(self):
        pasta_base = "runs/detect"
        pastas = [d for d in os.listdir(pasta_base) if d.startswith("exp")]
        pastas.sort(key=lambda x: int(x[3:]) if x != "exp" else 0, reverse=True)

        ultima_pasta = os.path.join(pasta_base, pastas[0])
        arquivos = [os.path.join(ultima_pasta, f) for f in os.listdir(ultima_pasta)]

        for arq in arquivos:
            if arq.lower().endswith(('.mp4', '.avi', '.mov')):
                return arq  # retorna o caminho do vídeo processado
        return None

    def mostrar_video(self, video_path):
        for widget in self.image_frame.winfo_children():
            widget.destroy()

        label = ctk.CTkLabel(self.image_frame, text="Vídeo processado. Clique em Play para visualizar.")
        label.pack(pady=5)

        play_button = ctk.CTkButton(self.image_frame, text="Play", command=lambda: self.play_video(video_path))
        play_button.pack(pady=5)

    def play_video(self, video_path):
        def run_video():
            cap = cv2.VideoCapture(video_path)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                cv2.imshow('Resultado YOLOv7', frame)
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()

        Thread(target=run_video).start()

if __name__ == "__main__":
    app = YOLOv7App()
    app.mainloop()
