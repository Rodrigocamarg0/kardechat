"""Rotas da API."""

from fastapi import APIRouter, Depends
from app.auth import verify_supabase_token
from app.chat import generate_chat_response
from app.models import ChatRequest, ChatResponse, HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok", version="1.0.0")


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: dict = Depends(verify_supabase_token),
):
    """
    Endpoint principal de chat.

    Recebe a pergunta do usuário e retorna a resposta usando
    confidence-based routing:
    - Alta confiança → resposta direta do L.E.
    - Média confiança → LLM reformula
    - Baixa confiança → RAG nos demais livros
    """
    result = await generate_chat_response(
        user_question=request.question,
        extensive=request.extensive,
        previous_answer=request.previous_answer,
    )

    return ChatResponse(
        answer=result["answer"],
        citations=[
            {
                "book": c["book"],
                "reference": c["reference"],
                "question": c.get("question"),
                "answer": c.get("answer"),
                "text": c.get("text"),
                "score": c["score"],
            }
            for c in result["citations"]
        ],
        strategy=result["strategy"],
        confidence=result["confidence"],
        top_score=result["top_score"],
    )
