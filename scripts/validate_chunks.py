#!/usr/bin/env python3
"""Quality gate dos chunks antes da geração de embeddings."""

import json
import os
import sys
from collections import Counter

from ingestion_utils import validate_embedding_input_sizes

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CHUNKS_PATH = os.path.join(DATA_DIR, "books_chunks.json")


def main() -> None:
    if not os.path.exists(CHUNKS_PATH):
        print("✗ books_chunks.json não encontrado. Execute parse_books.py primeiro.")
        sys.exit(1)

    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    if not chunks:
        print("✗ Nenhum chunk encontrado.")
        sys.exit(1)

    errors: list[str] = []

    oversized = validate_embedding_input_sizes([chunk.get("text", "") for chunk in chunks])
    if oversized:
        errors.append(
            "Há chunks acima do limite seguro de embedding: "
            + ", ".join(f"#{idx}~{tokens}t" for idx, tokens in oversized[:5])
        )

    for idx, chunk in enumerate(chunks):
        text = chunk.get("text", "").strip()
        page = chunk.get("page")
        page_end = chunk.get("page_end", page)
        word_count = chunk.get("word_count", len(text.split()))

        if not text:
            errors.append(f"Chunk #{idx} está vazio.")
            continue
        if not isinstance(page, int) or not isinstance(page_end, int):
            errors.append(f"Chunk #{idx} não tem metadata de página válida.")
        elif page_end < page:
            errors.append(f"Chunk #{idx} tem intervalo de páginas inválido: {page}-{page_end}.")
        if word_count < 40:
            errors.append(f"Chunk #{idx} está pequeno demais ({word_count} palavras).")
        if text.count("\n\n") > 20:
            errors.append(f"Chunk #{idx} parece mal normalizado.")

        if len(errors) >= 10:
            break

    books = Counter(chunk.get("book", "") for chunk in chunks)
    if "O Livro dos Espíritos" not in books:
        errors.append("O Livro dos Espíritos não apareceu em books_chunks.json.")

    if errors:
        print("✗ Quality gate falhou:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("✓ Quality gate aprovado.")
    print(f"  Total de chunks: {len(chunks)}")
    print(f"  Livros: {', '.join(sorted(books))}")


if __name__ == "__main__":
    main()
