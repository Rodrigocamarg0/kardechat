"""Configuração do backend via variáveis de ambiente."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB
    mongo_uri: str = "mongodb://kardechat:kardechat_secret@localhost:27017/kardechat?authSource=admin"
    db_name: str = "kardechat"

    # Coleções
    qa_collection: str = "le_questions"
    books_collection: str = "books_chunks"

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

    # Thresholds de similaridade (Q-to-Q)
    high_confidence: float = 0.88
    medium_confidence: float = 0.75

    class Config:
        env_file = ".env"


settings = Settings()
