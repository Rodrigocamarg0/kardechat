"""Helpers de parsing, chunking e validação para a pipeline de ingestão."""

from __future__ import annotations

import re


def normalize_text(text: str) -> str:
    """Normaliza espaços e remove linhas vazias redundantes."""
    text = text.replace("\r", "\n")
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def is_heading(line: str) -> bool:
    """Heurística simples para identificar títulos e divisões."""
    stripped = line.strip()
    if not stripped:
        return False

    if re.match(r"^(cap[ií]tulo|parte|livro|se[cç][aã]o)\b", stripped, re.IGNORECASE):
        return True
    if re.match(r"^[IVXLCDM]+\s*[-–—]?\s*[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]", stripped):
        return True

    words = stripped.split()
    if len(words) > 12:
        return False

    letters = [c for c in stripped if c.isalpha()]
    if letters and sum(1 for c in letters if c.isupper()) / len(letters) > 0.7:
        return True

    if stripped.endswith(":") and len(words) <= 12:
        return True

    return False


def page_to_blocks(text: str, page_number: int) -> list[dict]:
    """
    Divide uma página em blocos semânticos.

    Cada bloco pode ser um heading, um parágrafo ou um marcador de quebra de página.
    """
    normalized = normalize_text(text)
    if not normalized:
        return []

    lines = [line.strip() for line in normalized.splitlines()]
    blocks: list[dict] = []
    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return
        paragraph = " ".join(paragraph_lines)
        paragraph = re.sub(r"\s+", " ", paragraph).strip()
        if paragraph:
            blocks.append(
                {"type": "paragraph", "text": paragraph, "page": page_number}
            )
        paragraph_lines.clear()

    for line in lines:
        if not line:
            flush_paragraph()
            continue
        if re.fullmatch(r"\d+", line):
            continue
        if is_heading(line):
            flush_paragraph()
            blocks.append({"type": "heading", "text": line, "page": page_number})
            continue
        paragraph_lines.append(line)

    flush_paragraph()
    blocks.append({"type": "page_break", "text": "", "page": page_number})
    return blocks


def should_skip_page(text: str) -> bool:
    """Descarta páginas de sumário, expediente e material editorial."""
    normalized = normalize_text(text)
    if not normalized:
        return True

    lowered = normalized.lower()
    editorial_markers = [
        "produção editorial",
        "projeto gráfico",
        "diagramação",
        "normalização técnica",
        "biblioteca de obras raras",
        "sumário",
        "índice geral",
        "nota da editora",
        "capa:",
        "revisão:",
    ]
    if any(marker in lowered for marker in editorial_markers):
        return True

    chapter_hits = len(re.findall(r"cap[ií]tulo", lowered))
    part_hits = len(re.findall(r"\bparte\b", lowered))
    if chapter_hits >= 5 or (chapter_hits >= 3 and part_hits >= 1):
        return True

    words = normalized.split()
    if len(words) <= 6 and is_heading(normalized):
        return True

    return False


def block_word_count(block: dict) -> int:
    return len(block.get("text", "").split())


def _tail_overlap_blocks(blocks: list[dict], overlap_words: int) -> list[dict]:
    """Seleciona os últimos blocos úteis para overlap sem quebrar parágrafos."""
    if overlap_words <= 0:
        return []

    selected: list[dict] = []
    words = 0
    for block in reversed(blocks):
        if block["type"] == "page_break":
            continue
        if block["type"] == "heading" and not selected:
            continue
        selected.insert(0, block)
        words += block_word_count(block)
        if words >= overlap_words:
            break
    return selected


def blocks_to_chunks(
    blocks: list[dict],
    chunk_size: int,
    overlap: int,
    min_chunk_words: int = 120,
) -> list[dict]:
    """Agrupa blocos em chunks respeitando fronteiras semânticas."""
    chunks: list[dict] = []
    current_blocks: list[dict] = []
    current_words = 0
    current_start_page: int | None = None

    def flush(force: bool = False, keep_overlap: bool = True) -> None:
        nonlocal current_blocks, current_words, current_start_page

        content_blocks = [b for b in current_blocks if b["type"] != "page_break"]
        if not content_blocks:
            current_blocks = []
            current_words = 0
            current_start_page = None
            return

        if not force and current_words < min_chunk_words:
            return

        text_parts = [b["text"] for b in content_blocks]
        chunk_text = "\n\n".join(text_parts).strip()
        if chunk_text:
            chunks.append(
                {
                    "page_start": current_start_page or content_blocks[0]["page"],
                    "page_end": content_blocks[-1]["page"],
                    "text": chunk_text,
                    "word_count": len(chunk_text.split()),
                }
            )

        overlap_blocks = (
            _tail_overlap_blocks(content_blocks, overlap) if keep_overlap else []
        )
        current_blocks = list(overlap_blocks)
        current_words = sum(block_word_count(b) for b in current_blocks)
        current_start_page = current_blocks[0]["page"] if current_blocks else None

    for block in blocks:
        if block["type"] == "page_break":
            if current_words >= min_chunk_words:
                flush(force=True)
            continue

        if (
            block["type"] == "heading"
            and current_blocks
            and current_words >= min_chunk_words
        ):
            flush(force=True, keep_overlap=False)

        block_words = block_word_count(block)
        if current_start_page is None:
            current_start_page = block["page"]

        if current_blocks and current_words + block_words > chunk_size and current_words >= min_chunk_words:
            flush(force=True)
            if current_start_page is None:
                current_start_page = block["page"]

        current_blocks.append(block)
        current_words += block_words

        if block["type"] == "heading" and current_words >= min_chunk_words:
            flush(force=True)

    flush(force=True)
    return chunks


def merge_small_adjacent_chunks(
    chunks: list[dict],
    min_words: int = 40,
) -> list[dict]:
    """Funde chunks curtos com o próximo chunk do mesmo livro."""
    if not chunks:
        return []

    merged: list[dict] = []
    index = 0
    while index < len(chunks):
        current = dict(chunks[index])
        if current["word_count"] >= min_words:
            merged.append(current)
            index += 1
            continue

        if (
            index + 1 < len(chunks)
            and chunks[index + 1].get("book") == current.get("book")
        ):
            nxt = chunks[index + 1]
            text = f"{current['text']}\n\n{nxt['text']}".strip()
            merged.append(
                {
                    **nxt,
                    "page_start": current.get("page_start", current.get("page", nxt["page_start"])),
                    "page_end": nxt["page_end"],
                    "text": text,
                    "word_count": len(text.split()),
                }
            )
            index += 2
            continue

        if merged and merged[-1].get("book") == current.get("book"):
            prev = merged[-1]
            prev["text"] = f"{prev['text']}\n\n{current['text']}".strip()
            prev["page_end"] = current.get("page_end", current.get("page", prev["page_end"]))
            prev["word_count"] = len(prev["text"].split())
        else:
            merged.append(current)

        index += 1

    return merged


def estimate_tokens(text: str) -> int:
    """Estimativa conservadora de tokens para evitar inputs grandes demais."""
    return max(1, len(text) // 4)


def validate_embedding_input_sizes(
    texts: list[str],
    max_tokens: int = 6000,
) -> list[tuple[int, int]]:
    """Retorna a lista de inputs que excedem o limite seguro estimado."""
    oversized: list[tuple[int, int]] = []
    for index, text in enumerate(texts):
        tokens = estimate_tokens(text)
        if tokens > max_tokens:
            oversized.append((index, tokens))
    return oversized
