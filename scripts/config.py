"""
Configuração central do pipeline de ingestão.
"""

import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017/kardechat?directConnection=true",
)
DB_NAME = "kardechat"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIMENSIONS = 3072

# Coleção
BOOKS_COLLECTION = "books_chunks"

# Livros indexados
BOOKS = {
    "livro_dos_espiritos": {
        "nome": "O Livro dos Espíritos",
        "ano": 1857,
        "tipo": "rag",
    },
    "livro_dos_mediuns": {
        "nome": "O Livro dos Médiuns",
        "ano": 1861,
        "tipo": "rag",
    },
    "evangelho_segundo_espiritismo": {
        "nome": "O Evangelho Segundo o Espiritismo",
        "ano": 1864,
        "tipo": "rag",
    },
    "ceu_e_inferno": {
        "nome": "O Céu e o Inferno",
        "ano": 1865,
        "tipo": "rag",
    },
    "a_genese": {
        "nome": "A Gênese",
        "ano": 1868,
        "tipo": "rag",
    },
    "o_que_e_o_espiritismo": {
        "nome": "O que é o Espiritismo",
        "ano": 1859,
        "tipo": "rag",
    },
    "obras_postumas": {
        "nome": "Obras Póstumas",
        "ano": 1890,
        "tipo": "rag",
    },
}

# Tamanho de chunk para RAG
CHUNK_SIZE = 800
CHUNK_OVERLAP = 200
