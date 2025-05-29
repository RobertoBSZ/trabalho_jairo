import streamlit as st
import torch
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os
import sys
from pathlib import Path
import re
import warnings
import shutil
warnings.filterwarnings('ignore')

# Configuração do PyTorch
torch.set_grad_enabled(False)
if torch.cuda.is_available():
    torch.cuda.empty_cache()

# Configuração da página
st.set_page_config(
    page_title="YOLOv7 Detector de Placas",
    page_icon="🚗",
    layout="wide"
)

# Estilo personalizado
st.markdown("""
    <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .stButton button {
            width: 100%;
        }
        .detected-text {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: white;
            color: black;
            padding: 10px;
            border-radius: 5px;
            font-size: 18px;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_image(image_file):
    """Carrega e retorna uma imagem."""
    return Image.open(image_file)

def extract_text_from_labels(output_path):
    """Extrai o texto detectado das labels do YOLO."""
    try:
        # Procura pelo arquivo de labels na pasta labels
        label_path = output_path.parent / 'labels' / output_path.with_suffix('.txt').name
        if not label_path.exists():
            st.warning("Nenhum texto detectado na imagem.")
            return []
        
        detected_texts = []
        with open(label_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    # O formato esperado é: class_id x_center y_center width height confidence
                    parts = line.strip().split()
                    if len(parts) >= 6:  # Precisamos de pelo menos as coordenadas básicas
                        # Vamos tentar extrair as coordenadas
                        class_id, x_center, y_center, width, height = map(float, parts[:5])
                        # Se houver texto após as coordenadas, vamos usá-lo
                        if len(parts) > 6:
                            text = ' '.join(parts[6:])
                        else:
                            # Se não houver texto, vamos usar um formato padrão
                            text = f"Placa {len(detected_texts) + 1}"
                        detected_texts.append(text)
                except Exception as e:
                    st.warning(f"Erro ao processar uma linha do arquivo de labels: {e}")
                    continue
        
        if not detected_texts:
            st.warning("Nenhum texto foi extraído das detecções.")
        return detected_texts
    except Exception as e:
        st.error(f"Erro ao extrair texto das labels: {e}")
        return []

def add_text_overlay(image_path, detected_texts):
    """Adiciona o texto detectado como overlay na imagem."""
    try:
        # Abre a imagem
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        # Define a fonte e tamanho
        font_size = int(img.height * 0.04)  # Tamanho da fonte proporcional à altura da imagem
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                # Tenta encontrar alguma fonte do sistema
                system_fonts = ['arial.ttf', 'Arial.ttf', 'Helvetica.ttf', 'segoeui.ttf']
                for font_name in system_fonts:
                    try:
                        font = ImageFont.truetype(font_name, font_size)
                        break
                    except:
                        continue
                if not font:
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
        
        # Posição inicial para o texto (canto inferior direito)
        padding = int(img.width * 0.02)  # Padding proporcional à largura da imagem
        current_y = img.height - padding - font_size
        
        # Adiciona cada texto detectado
        for text in detected_texts:
            # Cria um retângulo branco como fundo
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Posição do texto
            x = img.width - text_width - padding
            
            # Desenha o fundo branco com borda preta
            rect_coords = [
                x - padding/2,
                current_y - padding/2,
                x + text_width + padding/2,
                current_y + text_height + padding/2
            ]
            
            # Desenha a borda preta
            draw.rectangle(rect_coords, outline='black', width=2)
            # Desenha o fundo branco
            draw.rectangle(rect_coords, fill='white')
            
            # Desenha o texto em preto
            draw.text((x, current_y), text, fill='black', font=font)
            
            current_y -= (text_height + padding)
        
        # Salva a imagem modificada
        output_path = image_path.parent / f"overlay_{image_path.name}"
        img.save(output_path)
        return output_path
    except Exception as e:
        st.error(f"Erro ao adicionar overlay: {e}")
        st.error("Detalhes técnicos do erro:", exc_info=True)
        return image_path

def run_detection(input_path, device, img_size, confidence):
    """Executa a detecção YOLOv7."""
    try:
        python_exe = sys.executable
        cmd = [
            python_exe, 'detect.py',
            '--weights', 'best.pt',
            '--img', str(img_size),
            '--conf', str(confidence),
            '--source', input_path,
            '--device', device,
            '--save-txt'
        ]
        
        import subprocess
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        
        if process.returncode != 0:
            st.error(f"Erro na detecção: {error.decode()}")
            return None
            
        return True
    except Exception as e:
        st.error(f"Erro ao executar detecção: {e}")
        return None

def convert_video_to_mp4(input_path, output_path):
    """Converte o vídeo para MP4 com codec H.264."""
    try:
        # Abre o vídeo original
        cap = cv2.VideoCapture(str(input_path))
        
        # Obtém propriedades do vídeo
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        # Define o codec e cria o objeto VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        # Lê e escreve cada frame
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
        
        # Libera os recursos
        cap.release()
        out.release()
        
        return True
    except Exception as e:
        st.error(f"Erro ao converter vídeo: {e}")
        return False

def main():
    st.title("Detector de Placas com YOLOv7")

    # Sidebar para configurações
    with st.sidebar:
        st.header("Configurações")
        
        # Seleção do dispositivo (CPU/GPU)
        device_option = st.selectbox(
            "Dispositivo de Processamento",
            options=["CPU", "GPU"],
            help="Selecione o dispositivo para executar o modelo"
        )
        
        # Configurações de detecção
        confidence = st.slider(
            "Confiança Mínima",
            min_value=0.0,
            max_value=1.0,
            value=0.25,
            help="Limite mínimo de confiança para detecções"
        )
        
        # Tamanho da imagem
        img_size = st.select_slider(
            "Tamanho da Imagem",
            options=[320, 416, 512, 640, 736],
            value=640,
            help="Tamanho da imagem para processamento"
        )

    # Área principal
    col1, col2 = st.columns(2)
    
    with col1:
        # Upload de arquivo
        uploaded_file = st.file_uploader(
            "Escolha uma imagem ou vídeo",
            type=['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov'],
            help="Suporta imagens (JPG, PNG) e vídeos (MP4, AVI, MOV)"
        )

    with col2:
        if uploaded_file is not None:
            # Mostrar preview do arquivo
            file_type = uploaded_file.type.split('/')[0]
            if file_type == 'image':
                st.image(uploaded_file, caption="Arquivo selecionado", use_container_width=True)
            elif file_type == 'video':
                st.video(uploaded_file)

    # Botão de detecção
    if uploaded_file is not None:
        if st.button("🔍 Iniciar Detecção", use_container_width=True):
            with st.spinner("Processando..."):
                try:
                    # Configurar dispositivo
                    device = "cuda:0" if device_option == "GPU" and torch.cuda.is_available() else "cpu"
                    
                    # Criar diretório temporário
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Salvar arquivo temporário
                        input_path = Path(temp_dir) / uploaded_file.name
                        with open(input_path, 'wb') as f:
                            f.write(uploaded_file.getvalue())

                        # Executar detecção
                        if run_detection(input_path, device, img_size, confidence):
                            # Mostrar resultado
                            output_dir = Path("runs/detect")
                            latest_exp = max(output_dir.glob("exp*"), key=lambda p: int(p.name.replace("exp", "") or 0))
                            result_file = next(latest_exp.glob(f"*{os.path.splitext(uploaded_file.name)[1]}"))

                            if file_type == 'image':                                
                                st.image(str(result_file), caption="Resultado da Detecção", use_container_width=True)
                            elif file_type == 'video':
                                # Converter o vídeo para um formato compatível com o navegador
                                converted_path = result_file.parent / f"converted_{result_file.name}"
                                if convert_video_to_mp4(result_file, converted_path):
                                    # Copiar o vídeo convertido para um local permanente
                                    final_path = Path("processed_videos")
                                    final_path.mkdir(exist_ok=True)
                                    final_video = final_path / f"processed_{uploaded_file.name}"
                                    shutil.copy2(converted_path, final_video)
                                    
                                    # Adicionar link para download
                                    with open(final_video, 'rb') as f:
                                        st.download_button(
                                            label="⬇️ Download do Vídeo Processado",
                                            data=f.read(),
                                            file_name=f"processed_{uploaded_file.name}",
                                            mime="video/mp4"
                                        )
                                else:
                                    st.error("Não foi possível converter o vídeo para um formato compatível.")

                except Exception as e:
                    st.error(f"Erro durante o processamento: {e}")
                    st.error("Detalhes técnicos do erro:", exc_info=True)

    # Informações adicionais
    with st.expander("ℹ️ Informações do Sistema"):
        st.write(f"Device: {'GPU disponível' if torch.cuda.is_available() else 'CPU apenas'}")
        if torch.cuda.is_available():
            st.write(f"GPU: {torch.cuda.get_device_name(0)}")
        st.write(f"Python: {sys.version}")

if __name__ == "__main__":
    main() 