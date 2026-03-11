#!/usr/bin/env python3
"""
Parser das obras indexadas de Allan Kardec para RAG.

Extrai texto dos PDFs e divide em chunks para indexação vetorial.
"""

import os
import json
import fitz  # PyMuPDF
from config import CHUNK_SIZE, CHUNK_OVERLAP
from ingestion_utils import (
    blocks_to_chunks,
    merge_small_adjacent_chunks,
    page_to_blocks,
    should_skip_page,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

BOOKS_TO_PARSE = [
    {
        "filenames": [
            "WEB-Livro-dos-Espíritos-Guillon-1.pdf",
            "livro_dos_espiritos.pdf",
        ],
        "nome": "O Livro dos Espíritos",
    },
    {
        "filenames": [
            "WEB-Livro-dos-Mediuns-Guillon-1.pdf",
            "livro_dos_mediuns.pdf",
        ],
        "nome": "O Livro dos Médiuns",
    },
    {
        "filenames": [
            "WEB-O-Evangelho-segundo-o-Espiritismo-Guillon.pdf",
            "evangelho_segundo_espiritismo.pdf",
        ],
        "nome": "O Evangelho Segundo o Espiritismo",
    },
    {
        "filenames": [
            "WEB-O-Ceu-e-o-inferno-Guillon.pdf",
            "ceu_e_inferno.pdf",
        ],
        "nome": "O Céu e o Inferno",
    },
    {
        "filenames": [
            "WEB-A-Genese-Guillon.pdf",
            "a_genese.pdf",
        ],
        "nome": "A Gênese",
    },
    {
        "filenames": [
            "WEB-O-que-e-o-Espiritismo-Reformador.pdf",
            "o_que_e_o_espiritismo.pdf",
        ],
        "nome": "O que é o Espiritismo",
    },
    {
        "filenames": [
            "WEB-Obras-postumas-Guillon.pdf",
            "obras_postumas.pdf",
        ],
        "nome": "Obras Póstumas",
    },
]


def resolve_pdf_path(book_info: dict) -> str | None:
    """Retorna o primeiro nome de arquivo existente para um livro."""
    for filename in book_info["filenames"]:
        pdf_path = os.path.join(DATA_DIR, filename)
        if os.path.exists(pdf_path):
            return pdf_path
    return None


def extract_pages(pdf_path: str) -> list[dict]:
    """Extrai texto por página do PDF."""
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            pages.append({"page": i + 1, "text": text})
    doc.close()
    return pages


def process_book(book_info: dict) -> list[dict]:
    """Processa um livro inteiro em chunks."""
    pdf_path = resolve_pdf_path(book_info)
    if not pdf_path:
        accepted = ", ".join(book_info["filenames"])
        print(f"  ✗ PDF não encontrado para {book_info['nome']}")
        print(f"    Arquivos aceitos: {accepted}")
        return []

    print(f"    Arquivo: {os.path.basename(pdf_path)}")
    pages = extract_pages(pdf_path)
    all_chunks = []
    all_blocks = []

    for page_data in pages:
        if should_skip_page(page_data["text"]):
            continue
        all_blocks.extend(page_to_blocks(page_data["text"], page_data["page"]))

    chunks = blocks_to_chunks(
        all_blocks,
        chunk_size=CHUNK_SIZE,
        overlap=CHUNK_OVERLAP,
    )
    chunks = merge_small_adjacent_chunks(chunks)
    for i, chunk in enumerate(chunks):
        all_chunks.append({
            "book": book_info["nome"],
            "page": chunk["page_start"],
            "page_end": chunk["page_end"],
            "chunk_index": i,
            "word_count": chunk["word_count"],
            "text": chunk["text"],
        })

    return all_chunks


def main() -> None:
    print("=== Parsing dos livros (RAG tradicional) ===\n")

    all_chunks = []
    for book in BOOKS_TO_PARSE:
        print(f"  Processando: {book['nome']}...")
        chunks = process_book(book)
        print(f"    → {len(chunks)} chunks extraídos")
        all_chunks.extend(chunks)

    output_path = os.path.join(DATA_DIR, "books_chunks.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"\n  ✓ Total: {len(all_chunks)} chunks salvos em {output_path}")


if __name__ == "__main__":
    main()
