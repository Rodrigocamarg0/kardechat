"""
Serviço de chat com confidence-based routing.

- Alta confiança  → retorna resposta direta do L.E.
- Média confiança → LLM reformula com base nas respostas encontradas
- Baixa confiança → RAG completo nos demais livros
"""

from app.config import settings
from app.embeddings import get_openai_client, generate_embedding
from app.search import hybrid_search


SYSTEM_PROMPT = """Você é Kardechat, um assistente especializado na Doutrina Espírita
codificada por Allan Kardec. Você responde em português brasileiro.

Suas respostas devem ser:
- Fiéis ao conteúdo original dos livros de Allan Kardec
- Claras e acessíveis, mas respeitando a profundidade do tema
- Sempre baseadas nos trechos fornecidos como contexto

IMPORTANTE: Nunca invente informações. Se o contexto não for suficiente,
diga que não encontrou uma resposta precisa nos livros.

Quando o usuário pedir uma resposta mais extensa, aprofunde a explicação
usando todo o contexto disponível."""


DIRECT_TEMPLATE = """O usuário fez a seguinte pergunta:
"{user_question}"

Encontrei no Livro dos Espíritos a seguinte pergunta muito semelhante:

Pergunta #{number}: "{original_question}"
Resposta: "{original_answer}"

{extra_context}

Apresente a resposta de forma natural e resumida, como se Allan Kardec
estivesse respondendo diretamente. Não diga "no livro diz que..." —
responda de forma direta. Ao final, mencione brevemente que esta resposta
se encontra na pergunta #{number} do Livro dos Espíritos."""


REFORMULATE_TEMPLATE = """O usuário fez a seguinte pergunta:
"{user_question}"

Encontrei algumas perguntas relacionadas no Livro dos Espíritos:

{qa_context}

A pergunta do usuário não é idêntica, mas é relacionada.
Elabore uma resposta que sintetize as informações encontradas,
sendo fiel ao conteúdo original. Indique quais perguntas do L.E.
são mais relevantes."""


RAG_TEMPLATE = """O usuário fez a seguinte pergunta:
"{user_question}"

{le_context}

Encontrei os seguintes trechos relevantes nos livros do Pentateuco Espírita:

{book_context}

Com base nesses trechos, elabore uma resposta resumida e fiel ao conteúdo
original de Allan Kardec. Cite os livros e páginas quando possível."""


EXTENSIVE_TEMPLATE = """O usuário pediu uma resposta mais detalhada sobre:
"{user_question}"

Resposta anterior resumida:
"{previous_answer}"

Contexto completo disponível:

{full_context}

Elabore uma resposta extensa e detalhada, explorando todos os aspectos
encontrados nos livros. Inclua citações diretas quando possível."""


def format_citations(search_result: dict) -> list[dict]:
    """Formata citações para o componente colapsável."""
    citations = []

    for r in search_result.get("le_results", []):
        citations.append({
            "book": r["book"],
            "reference": f"Pergunta #{r['number']}",
            "question": r["question"],
            "answer": r["answer"],
            "score": round(r["score"], 3),
        })

    for r in search_result.get("book_results", []):
        citations.append({
            "book": r["book"],
            "reference": f"Página {r['page']}",
            "text": r["text"][:500],
            "score": round(r.get("score", 0), 3),
        })

    return citations


async def generate_chat_response(
    user_question: str,
    extensive: bool = False,
    previous_answer: str | None = None,
) -> dict:
    """
    Gera resposta usando confidence-based routing.

    Args:
        user_question: Pergunta do usuário
        extensive: Se True, gera resposta mais detalhada
        previous_answer: Resposta anterior para expandir (modo extenso)

    Returns:
        dict com answer, citations, strategy, confidence
    """
    # Gera embedding da pergunta
    query_embedding = await generate_embedding(user_question)

    # Busca híbrida
    search_result = await hybrid_search(user_question, query_embedding)

    strategy = search_result["strategy"]
    confidence = search_result["confidence"]
    le_results = search_result["le_results"]
    book_results = search_result["book_results"]

    # Monta prompt baseado na estratégia
    if extensive and previous_answer:
        # Modo extenso
        full_context_parts = []
        for r in le_results:
            full_context_parts.append(
                f"[L.E. #{r['number']}] P: {r['question']}\nR: {r['answer']}"
            )
        for r in book_results:
            full_context_parts.append(
                f"[{r['book']}, p.{r['page']}] {r['text']}"
            )
        full_context = "\n\n".join(full_context_parts)

        user_prompt = EXTENSIVE_TEMPLATE.format(
            user_question=user_question,
            previous_answer=previous_answer,
            full_context=full_context,
        )

    elif strategy == "direct":
        # Alta confiança: resposta direta
        top = le_results[0]
        extra = ""
        if len(le_results) > 1:
            extras = [
                f"Pergunta #{r['number']}: {r['question']}"
                for r in le_results[1:]
            ]
            extra = "Perguntas relacionadas:\n" + "\n".join(extras)

        user_prompt = DIRECT_TEMPLATE.format(
            user_question=user_question,
            number=top["number"],
            original_question=top["question"],
            original_answer=top["answer"],
            extra_context=extra,
        )

    elif strategy == "reformulate":
        # Média confiança: reformula
        qa_parts = []
        for r in le_results:
            qa_parts.append(
                f"Pergunta #{r['number']} (similaridade: {r['score']:.2f}):\n"
                f"P: {r['question']}\nR: {r['answer']}"
            )
        qa_context = "\n\n".join(qa_parts)

        user_prompt = REFORMULATE_TEMPLATE.format(
            user_question=user_question,
            qa_context=qa_context,
        )

    else:
        # Baixa confiança: RAG nos demais livros
        le_context = ""
        if le_results:
            le_parts = [
                f"[L.E. #{r['number']}] P: {r['question']}\nR: {r['answer']}"
                for r in le_results
            ]
            le_context = (
                "Do Livro dos Espíritos (menor relevância):\n"
                + "\n\n".join(le_parts)
            )

        book_parts = [
            f"[{r['book']}, p.{r['page']}]\n{r['text']}"
            for r in book_results
        ]
        book_context = "\n\n".join(book_parts)

        user_prompt = RAG_TEMPLATE.format(
            user_question=user_question,
            le_context=le_context,
            book_context=book_context,
        )

    # Chama LLM
    client = get_openai_client()
    completion = await client.chat.completions.create(
        model=settings.chat_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=1500 if not extensive else 3000,
    )

    answer = completion.choices[0].message.content
    citations = format_citations(search_result)

    return {
        "answer": answer,
        "citations": citations,
        "strategy": strategy,
        "confidence": confidence,
        "top_score": search_result["top_score"],
    }
