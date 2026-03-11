#!/usr/bin/env python3
"""
Gera embeddings e armazena no MongoDB.

- Indexa apenas chunks de texto para RAG tradicional
"""

import os
import sys
import json
import time
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from pymongo.operations import SearchIndexModel
from openai import OpenAI
from tqdm import tqdm
from ingestion_utils import validate_embedding_input_sizes
from config import (
    MONGO_URI,
    DB_NAME,
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS,
    BOOKS_COLLECTION,
)

FORCE = "--force" in sys.argv
BOOKS_VECTOR_INDEX = "books_vector_idx"

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


def already_ingested(collection_name: str) -> bool:
    """Retorna True se a coleção já tem documentos no MongoDB."""
    count = db[collection_name].count_documents({})
    return count > 0


def ingest_book_chunks() -> None:
    """Ingere chunks dos demais livros com RAG tradicional."""
    if not FORCE and already_ingested(BOOKS_COLLECTION):
        count = db[BOOKS_COLLECTION].count_documents({})
        print(f"  ✓ Já ingerido ({count} chunks). Use --force para reingerir.")
        return

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
    oversized = validate_embedding_input_sizes(texts)
    if oversized:
        preview = ", ".join(
            f"#{index}~{tokens}t"
            for index, tokens in oversized[:5]
        )
        print("  ✗ Há chunks acima do limite seguro para embeddings.")
        print(f"    Exemplos: {preview}")
        print("    Corrija o parser/chunking antes de ingerir o livro inteiro.")
        return

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
            "page_end": chunk.get("page_end", chunk["page"]),
            "chunk_index": chunk["chunk_index"],
            "word_count": chunk.get("word_count", len(chunk["text"].split())),
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


def create_indexes() -> None:
    """Cria índices auxiliares e o índice vetorial nativo do MongoDB."""
    books_col = db[BOOKS_COLLECTION]
    books_col.create_index("book", name="book_idx")

    vector_definition = {
        "fields": [
            {
                "type": "vector",
                "path": "text_embedding",
                "numDimensions": EMBEDDING_DIMENSIONS,
                "similarity": "cosine",
            }
        ]
    }

    existing = {
        index.get("name"): index
        for index in books_col.list_search_indexes()
    }
    try:
        if BOOKS_VECTOR_INDEX in existing:
            books_col.update_search_index(
                name=BOOKS_VECTOR_INDEX,
                definition=vector_definition,
            )
        else:
            books_col.create_search_index(
                SearchIndexModel(
                    definition=vector_definition,
                    name=BOOKS_VECTOR_INDEX,
                    type="vectorSearch",
                )
            )
    except OperationFailure as exc:
        print("  ✗ Falha ao criar índice vetorial.")
        print("    Verifique se o Mongo local suporta Search/Vector Search.")
        raise exc

    deadline = time.time() + 120
    while time.time() < deadline:
        current = {
            index.get("name"): index
            for index in books_col.list_search_indexes()
        }
        index_info = current.get(BOOKS_VECTOR_INDEX)
        if index_info and (
            index_info.get("queryable") is True
            or index_info.get("status") in {"READY", "ACTIVE"}
        ):
            print("  ✓ Índice vetorial criado e pronto para consultas")
            break
        time.sleep(2)
    else:
        print("  ✗ Índice vetorial criado, mas ainda não ficou queryable a tempo.")
        print("    Aguarde e tente consultar novamente em instantes.")


def main() -> None:
    print("=== Ingestão de embeddings no MongoDB ===\n")
    if FORCE:
        print("  Modo --force: recriando todas as coleções.\n")
    else:
        print("  Modo padrão: pulando coleções já ingeridas (use --force para recriar).\n")

    print("[1/2] Demais livros (RAG tradicional):")
    ingest_book_chunks()

    print("\n[2/2] Criando índices e vector search:")
    create_indexes()

    print("\n=== Ingestão concluída ===")
    print(f"  Banco: {DB_NAME}")
    print(f"  Coleção RAG: {BOOKS_COLLECTION}")


if __name__ == "__main__":
    main()
