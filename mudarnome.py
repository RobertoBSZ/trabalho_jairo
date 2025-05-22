import os
import unicodedata

def sanitize_filename(filename):
    """Remove acentos, espaços e caracteres especiais, mantendo extensão."""
    name, ext = os.path.splitext(filename)
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    name = name.replace(' ', '_')
    return name + ext

def rename_dataset(image_dir, label_dir):
    log = []
    renamed_count = 0

    for filename in os.listdir(image_dir):
        if not filename.lower().endswith(('.jpg', '.png')):
            continue

        image_old_path = os.path.join(image_dir, filename)
        label_old_name = os.path.splitext(filename)[0] + '.txt'
        label_old_path = os.path.join(label_dir, label_old_name)

        if not os.path.exists(label_old_path):
            log.append(f"SKIPPED (sem rótulo): {filename}")
            continue

        image_new_name = sanitize_filename(filename)
        label_new_name = os.path.splitext(image_new_name)[0] + '.txt'

        image_new_path = os.path.join(image_dir, image_new_name)
        label_new_path = os.path.join(label_dir, label_new_name)

        # Evita sobrescrever
        if os.path.exists(image_new_path) or os.path.exists(label_new_path):
            log.append(f"SKIPPED (já existe): {image_new_name}")
            continue

        # Renomeia os dois arquivos
        os.rename(image_old_path, image_new_path)
        os.rename(label_old_path, label_new_path)

        renamed_count += 1
        log.append(f"OK: {filename} → {image_new_name}")

    # Imprime o log
    print(f"\n✅ Renomeados: {renamed_count} arquivos de imagem + rótulo\n")
    for entry in log:
        print(entry)

# Caminhos dos diretórios de treino e validação

rename_dataset(
    image_dir='C:/Users/Rober/Downloads/teste1/image',
    label_dir='C:/Users/Rober/Downloads/teste1/label'
)
