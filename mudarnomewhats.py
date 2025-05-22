import os
import re
import unicodedata

def limpar_nome(filename):
    nome, ext = os.path.splitext(filename)
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')
    nome = re.sub(r'[^\w]', '_', nome)     # substitui espaços, parênteses, pontos, etc.
    nome = re.sub(r'_+', '_', nome)        # reduz múltiplos "_" seguidos
    return nome.strip('_') + ext.lower()

def renomear_arquivos_com_whatsapp(image_dir, label_dir):
    log = []
    arquivos = [f for f in os.listdir(image_dir) if 'whatsapp' in f.lower() and f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    for img in arquivos:
        label_old_name = os.path.splitext(img)[0] + '.txt'

        img_path_old = os.path.join(image_dir, img)
        lbl_path_old = os.path.join(label_dir, label_old_name)

        new_img_name = limpar_nome(img)
        new_lbl_name = os.path.splitext(new_img_name)[0] + '.txt'

        img_path_new = os.path.join(image_dir, new_img_name)
        lbl_path_new = os.path.join(label_dir, new_lbl_name)

        if os.path.exists(img_path_new) or os.path.exists(lbl_path_new):
            log.append(f"⏭️  SKIPPED (já existe): {new_img_name}")
            continue

        os.rename(img_path_old, img_path_new)

        if os.path.exists(lbl_path_old):
            os.rename(lbl_path_old, lbl_path_new)
            log.append(f"✔️  {img} + {label_old_name} → {new_img_name} + {new_lbl_name}")
        else:
            log.append(f"⚠️  {img} renomeada, mas sem rótulo correspondente")

    print("\n📄 Log de renomeações:")
    if not log:
        print("⚠️  Nenhum arquivo com 'WhatsApp' foi encontrado.")
    else:
        for l in log:
            print(l)

# Rodar para treino
renomear_arquivos_com_whatsapp(
    image_dir='C:/Users/Rober/Downloads/IA/placas/images/val',
    label_dir='C:/Users/Rober/Downloads/IA/placas/labels/val'
)