#!/usr/bin/env python3
"""
Baixa os PDFs das obras indexadas de Allan Kardec.

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
    "livro_dos_espiritos": {
        "filenames": [
            "WEB-Livro-dos-Espíritos-Guillon-1.pdf",
            "livro_dos_espiritos.pdf",
        ],
        "url": (
            "https://www.febnet.org.br/portal/wp-content/uploads/2012/06/"
            "O-Livro-dos-Espiritos.pdf"
        ),
    },
    "livro_dos_mediuns": {
        "filenames": [
            "WEB-Livro-dos-Mediuns-Guillon-1.pdf",
            "livro_dos_mediuns.pdf",
        ],
        "url": (
            "https://www.febnet.org.br/portal/wp-content/uploads/2012/06/"
            "O-livro-dos-mediuns.pdf"
        ),
    },
    "evangelho_segundo_espiritismo": {
        "filenames": [
            "WEB-O-Evangelho-segundo-o-Espiritismo-Guillon.pdf",
            "evangelho_segundo_espiritismo.pdf",
        ],
        "url": (
            "https://www.febnet.org.br/portal/wp-content/uploads/2012/06/"
            "O-Evangelho-segundo-o-Espiritismo.pdf"
        ),
    },
    "ceu_e_inferno": {
        "filenames": [
            "WEB-O-Ceu-e-o-inferno-Guillon.pdf",
            "ceu_e_inferno.pdf",
        ],
        "url": (
            "https://www.febnet.org.br/portal/wp-content/uploads/2012/06/"
            "O-ceu-e-o-inferno.pdf"
        ),
    },
    "a_genese": {
        "filenames": [
            "WEB-A-Genese-Guillon.pdf",
            "a_genese.pdf",
        ],
        "url": (
            "https://www.febnet.org.br/portal/wp-content/uploads/2012/06/"
            "A-Genese.pdf"
        ),
    },
    "o_que_e_o_espiritismo": {
        "filenames": [
            "WEB-O-que-e-o-Espiritismo-Reformador.pdf",
            "o_que_e_o_espiritismo.pdf",
        ],
        "url": (
            "https://www.febnet.org.br/portal/wp-content/uploads/2012/06/"
            "O-que-e-o-Espiritismo.pdf"
        ),
    },
    "obras_postumas": {
        "filenames": [
            "WEB-Obras-postumas-Guillon.pdf",
            "obras_postumas.pdf",
        ],
        "url": (
            "https://www.febnet.org.br/portal/wp-content/uploads/2012/06/"
            "Obras-Postumas.pdf"
        ),
    },
}


def find_existing_file(filenames: list[str]) -> str | None:
    """Retorna o primeiro nome de arquivo já existente em data/."""
    for filename in filenames:
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            return filename
    return None


def download_pdf(filenames: list[str], url: str) -> None:
    filename = filenames[0]
    filepath = os.path.join(DATA_DIR, filename)
    existing = find_existing_file(filenames)
    if existing:
        print(f"  ✓ {existing} já existe, pulando download.")
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
    print("=== Download das obras indexadas de Allan Kardec ===\n")
    for source in PDF_SOURCES.values():
        download_pdf(source["filenames"], source["url"])
    print("\n=== Download concluído ===")


if __name__ == "__main__":
    main()
