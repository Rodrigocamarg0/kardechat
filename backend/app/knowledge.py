"""Knowledge base com busca vetorial nativa do MongoDB."""

from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure

from agno.knowledge.embedder.openai import OpenAIEmbedder

from app.config import settings

embedder = OpenAIEmbedder(
    id=settings.embedding_model,
    dimensions=settings.embedding_dimensions,
    api_key=settings.openai_api_key,
)

_motor_client: AsyncIOMotorClient | None = None


def get_motor_client() -> AsyncIOMotorClient:
    global _motor_client
    if _motor_client is None:
        _motor_client = AsyncIOMotorClient(settings.mongo_uri)
    return _motor_client


def get_db():
    return get_motor_client()[settings.db_name]


def _num_candidates(limit: int) -> int:
    return max(
        limit * settings.vector_num_candidates_factor,
        settings.vector_min_num_candidates,
    )


async def search_books_vector(
    query_embedding: list[float],
    top_k: int = 5,
) -> list[dict]:
    """Executa vector search nativo no MongoDB via aggregation."""
    db = get_db()
    collection = db[settings.books_collection]

    pipeline = [
        {
            "$vectorSearch": {
                "index": settings.books_vector_index,
                "path": "text_embedding",
                "queryVector": query_embedding,
                "numCandidates": _num_candidates(top_k),
                "limit": top_k,
            }
        },
        {
            "$project": {
                "_id": 0,
                "book": 1,
                "page": 1,
                "page_end": 1,
                "chunk_index": 1,
                "word_count": 1,
                "text": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]

    try:
        cursor = collection.aggregate(pipeline)
        return await cursor.to_list(length=top_k)
    except OperationFailure as exc:
        raise RuntimeError(
            "O deployment MongoDB atual nao suporta $vectorSearch ou o indice "
            f"'{settings.books_vector_index}' ainda nao esta disponivel."
        ) from exc
