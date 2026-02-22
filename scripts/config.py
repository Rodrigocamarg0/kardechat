"""
Configuração central do pipeline de ingestão.
"""

import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://kardechat:kardechat_secret@localhost:27017/kardechat?authSource=admin",
)
DB_NAME = "kardechat"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIMENSIONS = 3072

# Coleções
QA_COLLECTION = "le_questions"  # Livro dos Espíritos – Q&A matching
BOOKS_COLLECTION = "books_chunks"  # Demais livros – RAG tradicional

# Livros do Pentateuco Espírita
# O Livro dos Espíritos é tratado separadamente (Q-to-Q matching)
BOOKS = {
    "livro_dos_espiritos": {
        "nome": "O Livro dos Espíritos",
        "ano": 1857,
        "tipo": "qa",  # question-answer matching
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
}

# Tamanho de chunk para RAG tradicional (demais livros)
CHUNK_SIZE = 800
CHUNK_OVERLAP = 200
