#!/usr/bin/env python3
"""
Parser do Livro dos Espíritos – extrai pares pergunta/resposta.

O Livro dos Espíritos é estruturado como uma lista numerada de perguntas
e respostas. Este script extrai cada par Q/A para indexação semântica
(Q-to-Q matching).
"""

import os
import re
import json
import fitz  # PyMuPDF


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PDF_PATH = os.path.join(DATA_DIR, "livro_dos_espiritos.pdf")
OUTPUT_PATH = os.path.join(DATA_DIR, "le_qa_pairs.json")


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrai texto completo do PDF."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    doc.close()
    return text


def parse_qa_pairs(text: str) -> list[dict]:
    """
    Identifica pares de pergunta/resposta numerados no texto.

    O Livro dos Espíritos segue o padrão:
    N. Pergunta? ou N – Pergunta?
    R. Resposta. ou — Resposta.

    Ajustamos com regex para capturar variações de formatação do PDF.
    """
    qa_pairs = []

    # Padrão: número seguido de ponto/traço/parêntese e texto da pergunta
    # A resposta vem logo após, frequentemente com travessão ou "R."
    pattern = re.compile(
        r'(\d{1,4})\s*[\.\)\–\-—]\s*(.+?)(?:\n\s*[-–—]\s*|\n\s*R[\.\)]\s*)'
        r'(.+?)(?=\n\s*\d{1,4}\s*[\.\)\–\-—]|\Z)',
        re.DOTALL,
    )

    matches = pattern.findall(text)

    for num_str, question, answer in matches:
        num = int(num_str)
        question = question.strip().replace("\n", " ")
        question = re.sub(r'\s+', ' ', question)
        answer = answer.strip().replace("\n", " ")
        answer = re.sub(r'\s+', ' ', answer)

        if len(question) < 10 or len(answer) < 5:
            continue

        qa_pairs.append({
            "number": num,
            "question": question,
            "answer": answer,
            "book": "O Livro dos Espíritos",
        })

    return qa_pairs


def fallback_parse(text: str) -> list[dict]:
    """
    Parser alternativo mais simples caso o padrão principal não funcione.
    Tenta capturar linhas que começam com número e interrogação.
    """
    lines = text.split("\n")
    qa_pairs = []
    current_q = None
    current_num = None
    current_answer_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detecta nova pergunta: começa com número
        q_match = re.match(r'^(\d{1,4})\s*[\.\)\–\-—]\s*(.+)', line)
        if q_match:
            # Salva pergunta anterior se existir
            if current_q and current_answer_lines:
                answer = " ".join(current_answer_lines)
                answer = re.sub(r'\s+', ' ', answer).strip()
                if len(answer) > 5:
                    qa_pairs.append({
                        "number": current_num,
                        "question": current_q,
                        "answer": answer,
                        "book": "O Livro dos Espíritos",
                    })

            current_num = int(q_match.group(1))
            current_q = q_match.group(2).strip()
            current_answer_lines = []
            continue

        # Detecta resposta (travessão no início)
        r_match = re.match(r'^[-–—]\s*(.+)', line)
        if r_match and current_q:
            current_answer_lines.append(r_match.group(1))
            continue

        r_match2 = re.match(r'^R[\.\)]\s*(.+)', line)
        if r_match2 and current_q:
            current_answer_lines.append(r_match2.group(1))
            continue

        # Continuação da resposta
        if current_q and current_answer_lines:
            current_answer_lines.append(line)

    # Última pergunta
    if current_q and current_answer_lines:
        answer = " ".join(current_answer_lines)
        answer = re.sub(r'\s+', ' ', answer).strip()
        if len(answer) > 5:
            qa_pairs.append({
                "number": current_num,
                "question": current_q,
                "answer": answer,
                "book": "O Livro dos Espíritos",
            })

    return qa_pairs


def main() -> None:
    if not os.path.exists(PDF_PATH):
        print(f"✗ PDF não encontrado: {PDF_PATH}")
        print("  Execute primeiro: python download_books.py")
        return

    print("=== Parsing do Livro dos Espíritos ===\n")
    text = extract_text_from_pdf(PDF_PATH)
    print(f"  Texto extraído: {len(text)} caracteres")

    # Tenta parser principal
    qa_pairs = parse_qa_pairs(text)
    print(f"  Parser principal: {len(qa_pairs)} pares Q/A encontrados")

    # Se encontrou poucos, tenta fallback
    if len(qa_pairs) < 100:
        print("  Poucos resultados, tentando parser alternativo...")
        qa_pairs_alt = fallback_parse(text)
        print(f"  Parser alternativo: {len(qa_pairs_alt)} pares Q/A encontrados")
        if len(qa_pairs_alt) > len(qa_pairs):
            qa_pairs = qa_pairs_alt

    # Salva JSON intermediário
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(qa_pairs, f, ensure_ascii=False, indent=2)

    print(f"\n  ✓ {len(qa_pairs)} pares salvos em {OUTPUT_PATH}")

    # Mostra amostra
    if qa_pairs:
        print("\n  --- Amostra (3 primeiros) ---")
        for qa in qa_pairs[:3]:
            print(f"  #{qa['number']}: {qa['question'][:80]}...")
            print(f"    R: {qa['answer'][:80]}...")
            print()


if __name__ == "__main__":
    main()
