import os

def verificar_rotulos_sem_imagem(image_dir, label_dir):
    problemas = []
    imagens = {os.path.splitext(f)[0] for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.png'))}
    rotulos = [f for f in os.listdir(label_dir) if f.endswith('.txt')]

    for txt in rotulos:
        nome_base = os.path.splitext(txt)[0]
        if nome_base not in imagens:
            problemas.append(txt)

    if problemas:
        print("🚨 Rótulos sem imagem correspondente:")
        for r in problemas:
            print(f"- {r}")
    else:
        print("✅ Todos os rótulos têm imagens correspondentes.")

# Use os caminhos corretos:
verificar_rotulos_sem_imagem(
    image_dir='C:/Users/Rober/Downloads/IA/placas/images/train',
    label_dir='C:/Users/Rober/Downloads/IA/placas/labels/train'
)
