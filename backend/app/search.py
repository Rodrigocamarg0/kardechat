"""
Serviço de busca com sistema multi-camada:

1. Q-to-Q matching no Livro dos Espíritos
2. Busca híbrida (vetorial + BM25) nos demais livros
3. Confidence-based routing para decidir tipo de resposta
"""

import numpy as np
from app.config import settings
from app.database import get_db
from app.embeddings import generate_embedding


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calcula similaridade cosseno entre dois vetores."""
    a_np = np.array(a)
    b_np = np.array(b)
    dot = np.dot(a_np, b_np)
    norm_a = np.linalg.norm(a_np)
    norm_b = np.linalg.norm(b_np)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


async def search_le_questions(
    query_embedding: list[float],
    top_k: int = 3,
) -> list[dict]:
    """
    Busca semântica Q-to-Q no Livro dos Espíritos.
    Compara a pergunta do usuário com as perguntas indexadas.
    Retorna as perguntas mais similares com suas respostas.
    """
    db = get_db()
    collection = db[settings.qa_collection]

    # Busca todos os documentos (o L.E. tem ~1019 perguntas, cabe em memória)
    cursor = collection.find({}, {"_id": 0})
    docs = await cursor.to_list(length=2000)

    if not docs:
        return []

    # Calcula similaridade cosseno para cada pergunta
    scored = []
    for doc in docs:
        emb = doc.get("question_embedding")
        if not emb:
            continue
        score = cosine_similarity(query_embedding, emb)
        scored.append({
            "number": doc["number"],
            "question": doc["question"],
            "answer": doc["answer"],
            "book": doc["book"],
            "score": score,
        })

    # Ordena por score decrescente
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


async def search_le_keywords(query: str, top_k: int = 3) -> list[dict]:
    """Busca por palavras-chave (BM25) no Livro dos Espíritos."""
    db = get_db()
    collection = db[settings.qa_collection]

    cursor = collection.find(
        {"$text": {"$search": query}},
        {"score": {"$meta": "textScore"}, "_id": 0, "question_embedding": 0},
    ).sort([("score", {"$meta": "textScore"})]).limit(top_k)

    return await cursor.to_list(length=top_k)


async def search_books_vector(
    query_embedding: list[float],
    top_k: int = 5,
) -> list[dict]:
    """
    Busca vetorial nos demais livros do Pentateuco.
    RAG tradicional com chunks.
    """
    db = get_db()
    collection = db[settings.books_collection]

    # Busca por similaridade (sem Atlas Search, fazemos em memória
    # para coleções pequenas)
    cursor = collection.find({}, {"_id": 0})
    docs = await cursor.to_list(length=50000)

    if not docs:
        return []

    scored = []
    for doc in docs:
        emb = doc.get("text_embedding")
        if not emb:
            continue
        score = cosine_similarity(query_embedding, emb)
        scored.append({
            "book": doc["book"],
            "page": doc["page"],
            "text": doc["text"],
            "score": score,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


async def search_books_keywords(query: str, top_k: int = 5) -> list[dict]:
    """Busca por palavras-chave nos demais livros."""
    db = get_db()
    collection = db[settings.books_collection]

    cursor = collection.find(
        {"$text": {"$search": query}},
        {"score": {"$meta": "textScore"}, "_id": 0, "text_embedding": 0},
    ).sort([("score", {"$meta": "textScore"})]).limit(top_k)

    return await cursor.to_list(length=top_k)


async def hybrid_search(
    query: str,
    query_embedding: list[float],
) -> dict:
    """
    Sistema multi-camada com confidence-based routing:

    1. Busca Q-to-Q no Livro dos Espíritos
    2. Se score alto → resposta direta
    3. Se score médio → reformula com LLM
    4. Se score baixo → busca nos demais livros (RAG)
    """
    # Passo 1: Busca semântica no L.E.
    le_results = await search_le_questions(query_embedding, top_k=3)

    if le_results and le_results[0]["score"] >= settings.high_confidence:
        # Alta confiança: resposta direta do L.E.
        return {
            "strategy": "direct",
            "confidence": "high",
            "top_score": le_results[0]["score"],
            "le_results": le_results,
            "book_results": [],
        }

    if le_results and le_results[0]["score"] >= settings.medium_confidence:
        # Média confiança: reformula com LLM
        return {
            "strategy": "reformulate",
            "confidence": "medium",
            "top_score": le_results[0]["score"],
            "le_results": le_results,
            "book_results": [],
        }

    # Baixa confiança: busca nos demais livros
    book_vector = await search_books_vector(query_embedding, top_k=5)
    book_kw = await search_books_keywords(query, top_k=3)

    # Combina resultados (merge simples por score)
    seen_texts = set()
    combined = []
    for r in book_vector:
        key = r["text"][:100]
        if key not in seen_texts:
            seen_texts.add(key)
            combined.append(r)

    for r in book_kw:
        key = r.get("text", "")[:100]
        if key not in seen_texts:
            seen_texts.add(key)
            combined.append({**r, "score": r.get("score", 0.5)})

    combined.sort(key=lambda x: x.get("score", 0), reverse=True)

    return {
        "strategy": "rag",
        "confidence": "low",
        "top_score": le_results[0]["score"] if le_results else 0,
        "le_results": le_results[:2] if le_results else [],
        "book_results": combined[:5],
    }
