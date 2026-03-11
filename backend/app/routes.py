"""Rotas da API."""

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.agent import get_kardechat_agent
from app.models import ChatRequest, ChatResponse, Citation, HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok", version="2.0.0")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint principal de chat com Agno Agent.

    - session_id opcional: mantém histórico de conversa entre requisições
    - O agente usa tools para buscar nas knowledge bases do Kardec
    - Retorna session_id para que o frontend persista a sessão
    """
    agent = get_kardechat_agent(session_id=request.session_id)

    run_response = await agent.arun(
        input=request.question,
        stream=False,
    )

    citations = _extract_citations_from_messages(run_response)
    session_id = agent.session_id or ""

    return ChatResponse(
        answer=run_response.content or "",
        session_id=session_id,
        citations=citations,
        strategy="rag",
    )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Endpoint de chat com streaming SSE.
    Tokens chegam progressivamente. Evento final inclui session_id e citations.
    """
    agent = get_kardechat_agent(session_id=request.session_id)

    async def token_generator():
        last_response = None
        async for chunk in agent.arun(
            input=request.question,
            stream=True,
        ):
            last_response = chunk
            if chunk.content:
                yield f"data: {chunk.content}\n\n"

        # Evento final com metadados
        citations = (
            _extract_citations_from_messages(last_response) if last_response else []
        )
        meta = {
            "session_id": agent.session_id or "",
            "citations": [c.model_dump() for c in citations],
            "done": True,
        }
        yield f"data: {json.dumps(meta, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        token_generator(),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_citations_from_messages(run_response) -> list[Citation]:
    """
    Extrai citações dos tool results presentes no RunOutput.
    Parseia o JSON retornado por buscar_obras.
    """
    citations = []
    if run_response is None:
        return citations

    messages = getattr(run_response, "messages", None) or []

    for msg in messages:
        role = getattr(msg, "role", None)
        if role != "tool":
            continue

        content = getattr(msg, "content", None)
        if not content:
            continue

        try:
            data = json.loads(content) if isinstance(content, str) else content
        except (json.JSONDecodeError, TypeError):
            continue

        if not isinstance(data, dict) or not data.get("encontrado"):
            continue

        for r in data.get("resultados", []):
            citations.append(
                Citation(
                    book=r.get("livro", ""),
                    reference=f"Página {r.get('pagina', '')}",
                    text=r.get("trecho", "")[:500],
                    score=r.get("score", 0.0),
                )
            )

    return citations
