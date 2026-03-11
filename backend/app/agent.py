"""Agente Kardechat com RAG sobre busca vetorial nativa do MongoDB."""

import json

from agno.agent import Agent
from agno.models.openai import OpenAIChat

from app.config import settings
from app.knowledge import embedder, search_books_vector
from app.session_store import make_agent_storage


SYSTEM_INSTRUCTIONS = [
    "Voce e Kardechat, um assistente especializado na Doutrina Espirita "
    "codificada por Allan Kardec. Responda sempre em portugues brasileiro.",
    "Suas respostas devem ser fieis ao conteudo original dos livros de Allan Kardec, "
    "claras e acessiveis, mas respeitando a profundidade do tema.",
    "Sempre use a ferramenta `buscar_obras` antes de responder.",
    "Use apenas os trechos recuperados via RAG. Nao invente informacoes.",
    "Se nao houver contexto suficiente, informe que nao encontrou resposta precisa nos livros.",
    "Ao citar, mencione o livro e a pagina quando disponivel.",
]


async def buscar_obras(pergunta: str) -> str:
    """Busca RAG nas obras indexadas com vector search nativo do MongoDB."""
    query_embedding = await embedder.async_get_embedding(pergunta)
    results = await search_books_vector(query_embedding, top_k=8)

    if not results:
        return json.dumps(
            {"encontrado": False, "fonte": "Obras indexadas", "resultados": []},
            ensure_ascii=False,
        )

    formatted = []
    for r in results:
        formatted.append(
            {
                "livro": r.get("book", ""),
                "pagina": r.get("page", ""),
                "pagina_fim": r.get("page_end", r.get("page", "")),
                "trecho": r.get("text", ""),
                "score": round(float(r.get("score", 0.0)), 4),
            }
        )

    return json.dumps(
        {"encontrado": True, "fonte": "Obras indexadas", "resultados": formatted},
        ensure_ascii=False,
        indent=2,
    )


def get_kardechat_agent(session_id: str | None = None) -> Agent:
    """Instancia o agente Kardechat para uma sessao especifica."""
    return Agent(
        name="Kardechat",
        model=OpenAIChat(
            id=settings.chat_model,
            api_key=settings.openai_api_key,
            temperature=0.3,
            max_tokens=3000,
        ),
        tools=[buscar_obras],
        db=make_agent_storage(),
        session_id=session_id,
        add_history_to_context=True,
        num_history_runs=5,
        instructions=SYSTEM_INSTRUCTIONS,
        markdown=True,
    )
