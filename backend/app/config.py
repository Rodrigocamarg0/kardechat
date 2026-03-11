"""Configuração do backend via variáveis de ambiente."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB
    mongo_uri: str = "mongodb://localhost:27017/kardechat?directConnection=true"
    db_name: str = "kardechat"

    # Coleção de dados indexados
    books_collection: str = "books_chunks"
    books_vector_index: str = "books_vector_idx"
    vector_num_candidates_factor: int = 20
    vector_min_num_candidates: int = 100

    # OpenAI
    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-large"
    embedding_dimensions: int = 3072
    chat_model: str = "gpt-4o-mini"

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # CORS
    cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = Path(__file__).resolve().parents[2] / ".env"


settings = Settings()
