# 📝 Como testar a rede YOLOv7 com imagens

## ✅ Pré-requisitos

1. Python **3.10**.
2. `pip` instalado.
3. Git para clonar o repositório.
4. CUDA e cuDNN instalados (se quiser usar GPU).
5. Baixar a pasta "runs" no OneDrive, depois coloca na pasta yolov7

---

## ✅ 1. Clone o repositório

```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
```
---

## ✅ 2. Instale as dependências

Use um ambiente virtual:

```bash
python -m venv yolov7-env
yolov7-env\Scripts\activate  # No Windows
source yolov7-env/bin/activate  # No Linux/Mac
```
Instale os requisitos:

```bash
pip install -r requirements.txt
```
---

## ✅ 3. Coloque o modelo treinado

- Copie o arquivo do **modelo treinado** (por exemplo: `best.pt`) para a pasta raiz do projeto.  
Ou baixe de onde for indicado.

---

## ✅ 4. Prepare a pasta com as imagens

- Crie uma pasta, por exemplo:

```bash
/caminho/para/imagens/

- Coloque dentro as imagens que deseja testar (`.jpg`, `.png` etc.).
```
---

## ✅ 5. Execute a detecção

No terminal, dentro da pasta do projeto, rode:

```bash
python detect.py --weights runs/train/exp6/weights/best.pt --img 640 --conf 0.25 --source /caminho/para/imagens
```
### ⚙️ Parâmetros importantes:

| Parâmetro      | O que faz                                    |
|----------------|---------------------------------------------|
| `--weights`    | O arquivo do modelo treinado (`best.pt`)     |
| `--img`        | Tamanho da imagem de entrada (640 é padrão)  |
| `--conf`       | Confiança mínima para mostrar detecções      |
| `--source`     | Pasta com imagens ou caminho para vídeo      |

---

## ✅ 6. Veja os resultados

- As imagens **processadas com as detecções** ficarão salvas automaticamente em:

```bash
runs/detect/exp/
```
ou, se já tiver outras detecções:

```bash
runs/detect/exp1/
runs/detect/exp2/
...
```
---

## ✅ 7. (Opcional) Salve também as detecções em arquivos `.txt`

Se quiser salvar as detecções no formato YOLO (`.txt`), adicione a flag `--save-txt`:

```bash
python detect.py --weights runs/train/exp6/weights/best.pt --img 640 --conf 0.25 --source /caminho/para/imagens --save-txt
```
Os arquivos `.txt` serão salvos em:

```bash
runs/detect/exp/labels/
```
---

## ✅ 8. (Opcional) Teste com vídeos ou webcam

Para um **vídeo**:

```bash
python detect.py --weights best.pt --img 640 --source video.mp4
```
Para a **webcam**:

```bash
python detect.py --weights best.pt --img 640 --source 0
```
---

## ✅ 9. Pronto!

Agora você já sabe como testar a rede YOLOv7 com suas imagens!  
As detecções estarão salvas para você analisar.

---

## ✅ Passo a passo para configurar o PyTorch com suporte à GPU (CUDA 12.1)

### 1. Instale a versão correta do PyTorch com CUDA 12.1:

```bash
pip install torch==2.5.1+cu121 torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
```
### Isso garante que será baixada a versão com suporte CUDA 12.1, compatível com sua GPU NVIDIA.
## Importante:
### Não pule o --extra-index-url → sem ele, o pip baixa a versão CPU-only automaticamente.
### Pode usar torch==2.5.1+cu121 pois essa versão já funcionou na outra pasta.

### 2. Confirme a instalação:

```bash
pip show torch
```
### O resultado esperado deve mostrar:
### Version: 2.5.1+cu121
### Se aparecer cpu ou +cpu, significa que não pegou a versão CUDA → revise o comando de instalação.

### 3. Teste se o PyTorch reconhece a GPU:

```bash
python
import torch
print(torch.cuda.is_available())
```
## O retorno esperado:
### True
### Se aparecer False → significa que:
### - O driver NVIDIA pode não estar atualizado.
### - A instalação não foi feita com suporte a CUDA.

## ✅ Feito isso, seu ambiente estará pronto para usar a GPU com YOLOv7!


