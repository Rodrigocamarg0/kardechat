#!/usr/bin/env python3
"""
Parser dos demais livros do Pentateuco Espírita – RAG tradicional.

Extrai texto dos PDFs e divide em chunks para indexação vetorial.
"""

import os
import re
import json
import fitz  # PyMuPDF
from config import CHUNK_SIZE, CHUNK_OVERLAP

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

BOOKS_TO_PARSE = [
    {
        "filename": "livro_dos_mediuns.pdf",
        "nome": "O Livro dos Médiuns",
    },
    {
        "filename": "evangelho_segundo_espiritismo.pdf",
        "nome": "O Evangelho Segundo o Espiritismo",
    },
    {
        "filename": "ceu_e_inferno.pdf",
        "nome": "O Céu e o Inferno",
    },
    {
        "filename": "a_genese.pdf",
        "nome": "A Gênese",
    },
]


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


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Divide texto em chunks com overlap."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunk = re.sub(r'\s+', ' ', chunk).strip()
        if len(chunk) > 20:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def process_book(book_info: dict) -> list[dict]:
    """Processa um livro inteiro em chunks."""
    pdf_path = os.path.join(DATA_DIR, book_info["filename"])
    if not os.path.exists(pdf_path):
        print(f"  ✗ PDF não encontrado: {pdf_path}")
        return []

    pages = extract_pages(pdf_path)
    all_chunks = []

    for page_data in pages:
        chunks = chunk_text(page_data["text"], CHUNK_SIZE, CHUNK_OVERLAP)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "book": book_info["nome"],
                "page": page_data["page"],
                "chunk_index": i,
                "text": chunk,
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
