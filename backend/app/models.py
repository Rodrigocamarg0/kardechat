"""Modelos Pydantic para request/response."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    session_id: str | None = None
    # 'extensive' e 'previous_answer' foram removidos:
    # - histórico é mantido automaticamente pelo Agno via session_id
    # - o usuário pode pedir respostas extensas diretamente na pergunta


class Citation(BaseModel):
    book: str
    reference: str
    question: str | None = None
    answer: str | None = None
    text: str | None = None
    score: float = 0.0


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    citations: list[Citation] = []
    strategy: str | None = None  # mantido para compatibilidade com o frontend


class HealthResponse(BaseModel):
    status: str
    version: str
