#!/usr/bin/env python3
"""
Baixa os PDFs dos 5 livros do Pentateuco Espírita.

Os PDFs são de domínio público e estão disponíveis em repositórios
abertos de obras espíritas. Caso algum link quebre, substitua pela
URL correta de um PDF em português do respectivo livro.
"""

import os
import requests
from tqdm import tqdm

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# URLs de PDFs públicos (domínio público – obras de Allan Kardec)
# Caso algum link quebre, substitua por outra fonte pública.
PDF_SOURCES = {
    "livro_dos_espiritos.pdf": (
        "https://www.febnet.org.br/portal/wp-content/uploads/2012/06/"
        "O-Livro-dos-Espiritos.pdf"
    ),
    "livro_dos_mediuns.pdf": (
        "https://www.febnet.org.br/portal/wp-content/uploads/2012/06/"
        "O-livro-dos-mediuns.pdf"
    ),
    "evangelho_segundo_espiritismo.pdf": (
        "https://www.febnet.org.br/portal/wp-content/uploads/2012/06/"
        "O-Evangelho-segundo-o-Espiritismo.pdf"
    ),
    "ceu_e_inferno.pdf": (
        "https://www.febnet.org.br/portal/wp-content/uploads/2012/06/"
        "O-ceu-e-o-inferno.pdf"
    ),
    "a_genese.pdf": (
        "https://www.febnet.org.br/portal/wp-content/uploads/2012/06/"
        "A-Genese.pdf"
    ),
}


def download_pdf(filename: str, url: str) -> None:
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        print(f"  ✓ {filename} já existe, pulando download.")
        return

    print(f"  ⬇ Baixando {filename}...")
    try:
        resp = requests.get(url, timeout=120, stream=True)
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        with open(filepath, "wb") as f:
            with tqdm(total=total, unit="B", unit_scale=True, desc=filename) as bar:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
                    bar.update(len(chunk))
        print(f"  ✓ {filename} baixado com sucesso.")
    except Exception as e:
        print(f"  ✗ Erro ao baixar {filename}: {e}")
        print(f"    Baixe manualmente e salve em: {filepath}")


def main() -> None:
    print("=== Download dos livros do Pentateuco Espírita ===\n")
    for filename, url in PDF_SOURCES.items():
        download_pdf(filename, url)
    print("\n=== Download concluído ===")


if __name__ == "__main__":
    main()
