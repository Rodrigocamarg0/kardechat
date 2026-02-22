"""Modelos Pydantic para request/response."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    extensive: bool = False
    previous_answer: str | None = None


class Citation(BaseModel):
    book: str
    reference: str
    question: str | None = None
    answer: str | None = None
    text: str | None = None
    score: float


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    strategy: str
    confidence: str
    top_score: float


class HealthResponse(BaseModel):
    status: str
    version: str
