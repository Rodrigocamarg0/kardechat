#!/usr/bin/env python3
"""
Gera embeddings e armazena no MongoDB.

- Livro dos Espíritos: indexa SOMENTE as perguntas (Q-to-Q matching)
- Demais livros: indexa chunks de texto (RAG tradicional)

Cria índices vetoriais com similaridade cosseno.
"""

import os
import json
import time
from pymongo import MongoClient
from openai import OpenAI
from tqdm import tqdm
from config import (
    MONGO_URI,
    DB_NAME,
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS,
    QA_COLLECTION,
    BOOKS_COLLECTION,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

client_openai = OpenAI(api_key=OPENAI_API_KEY)
client_mongo = MongoClient(MONGO_URI)
db = client_mongo[DB_NAME]


def get_embeddings(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    """Gera embeddings em batch usando OpenAI."""
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        retries = 0
        while retries < 3:
            try:
                response = client_openai.embeddings.create(
                    model=EMBEDDING_MODEL,
                    input=batch,
                    dimensions=EMBEDDING_DIMENSIONS,
                )
                all_embeddings.extend([d.embedding for d in response.data])
                break
            except Exception as e:
                retries += 1
                print(f"  Erro na API (tentativa {retries}/3): {e}")
                time.sleep(2 ** retries)
    return all_embeddings


def ingest_le_questions() -> None:
    """Ingere perguntas do Livro dos Espíritos com Q-to-Q matching."""
    qa_path = os.path.join(DATA_DIR, "le_qa_pairs.json")
    if not os.path.exists(qa_path):
        print("  ✗ le_qa_pairs.json não encontrado. Execute parse_le.py primeiro.")
        return

    with open(qa_path, "r", encoding="utf-8") as f:
        qa_pairs = json.load(f)

    if not qa_pairs:
        print("  ✗ Nenhum par Q/A encontrado.")
        return

    print(f"  Gerando embeddings para {len(qa_pairs)} perguntas...")
    questions = [qa["question"] for qa in qa_pairs]
    embeddings = get_embeddings(questions)

    if len(embeddings) != len(qa_pairs):
        print(f"  ✗ Erro: {len(embeddings)} embeddings para {len(qa_pairs)} perguntas")
        return

    # Prepara documentos
    docs = []
    for qa, emb in zip(qa_pairs, embeddings):
        docs.append({
            "number": qa["number"],
            "question": qa["question"],
            "answer": qa["answer"],
            "book": qa["book"],
            "question_embedding": emb,
        })

    # Insere no MongoDB
    collection = db[QA_COLLECTION]
    collection.drop()
    collection.insert_many(docs)

    print(f"  ✓ {len(docs)} perguntas inseridas na coleção '{QA_COLLECTION}'")


def ingest_book_chunks() -> None:
    """Ingere chunks dos demais livros com RAG tradicional."""
    chunks_path = os.path.join(DATA_DIR, "books_chunks.json")
    if not os.path.exists(chunks_path):
        print("  ✗ books_chunks.json não encontrado. Execute parse_books.py primeiro.")
        return

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    if not chunks:
        print("  ✗ Nenhum chunk encontrado.")
        return

    print(f"  Gerando embeddings para {len(chunks)} chunks...")
    texts = [c["text"] for c in chunks]
    embeddings = []

    batch_size = 100
    for i in tqdm(range(0, len(texts), batch_size), desc="  Batches"):
        batch = texts[i:i + batch_size]
        batch_embeddings = get_embeddings(batch, batch_size=batch_size)
        embeddings.extend(batch_embeddings)

    if len(embeddings) != len(chunks):
        print(f"  ✗ Erro: {len(embeddings)} embeddings para {len(chunks)} chunks")
        return

    # Prepara documentos
    docs = []
    for chunk, emb in zip(chunks, embeddings):
        docs.append({
            "book": chunk["book"],
            "page": chunk["page"],
            "chunk_index": chunk["chunk_index"],
            "text": chunk["text"],
            "text_embedding": emb,
        })

    # Insere no MongoDB
    collection = db[BOOKS_COLLECTION]
    collection.drop()

    # Insere em batches para evitar problemas de memória
    batch_insert = 500
    for i in range(0, len(docs), batch_insert):
        collection.insert_many(docs[i:i + batch_insert])

    print(f"  ✓ {len(docs)} chunks inseridos na coleção '{BOOKS_COLLECTION}'")


def create_text_indexes() -> None:
    """Cria índices de texto para busca BM25 / keyword."""
    # Índice de texto para perguntas do L.E.
    qa_col = db[QA_COLLECTION]
    qa_col.create_index([("question", "text"), ("answer", "text")], name="qa_text_idx")

    # Índice de texto para chunks dos livros
    books_col = db[BOOKS_COLLECTION]
    books_col.create_index([("text", "text")], name="books_text_idx")
    books_col.create_index("book", name="book_idx")

    print("  ✓ Índices de texto criados para busca híbrida (BM25)")


def main() -> None:
    print("=== Ingestão de embeddings no MongoDB ===\n")

    print("[1/3] Livro dos Espíritos (Q-to-Q matching):")
    ingest_le_questions()

    print("\n[2/3] Demais livros (RAG tradicional):")
    ingest_book_chunks()

    print("\n[3/3] Criando índices de texto:")
    create_text_indexes()

    print("\n=== Ingestão concluída ===")
    print(f"  Banco: {DB_NAME}")
    print(f"  Coleção Q&A: {QA_COLLECTION}")
    print(f"  Coleção RAG: {BOOKS_COLLECTION}")


if __name__ == "__main__":
    main()
