#!/usr/bin/env python3
"""
Pipeline completo de ingestão – executa uma vez.

1. Baixa os PDFs
2. Faz parsing do Livro dos Espíritos (Q/A)
3. Faz parsing dos demais livros (chunks)
4. Gera embeddings e armazena no MongoDB
"""

import subprocess
import sys
import os

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def run_step(description: str, script: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}\n")
    result = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS_DIR, script)],
        cwd=SCRIPTS_DIR,
    )
    if result.returncode != 0:
        print(f"\n✗ Erro no passo: {description}")
        print("  Corrija o erro e execute novamente.")
        sys.exit(1)


def main() -> None:
    print("╔══════════════════════════════════════════════╗")
    print("║   Kardechat – Pipeline de Ingestão           ║")
    print("║   Executar uma única vez                      ║")
    print("╚══════════════════════════════════════════════╝")

    run_step("Passo 1/4: Baixando PDFs", "download_books.py")
    run_step("Passo 2/4: Parsing do Livro dos Espíritos (Q&A)", "parse_le.py")
    run_step("Passo 3/4: Parsing dos demais livros (chunks)", "parse_books.py")
    run_step("Passo 4/4: Gerando embeddings e armazenando no MongoDB", "embed_and_store.py")

    print("\n╔══════════════════════════════════════════════╗")
    print("║   ✓ Pipeline concluído com sucesso!           ║")
    print("║   O banco MongoDB está pronto para uso.       ║")
    print("╚══════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
