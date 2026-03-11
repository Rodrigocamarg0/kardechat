import json
import os
import subprocess
import sys
import tempfile
import unittest


SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from ingestion_utils import (  # noqa: E402
    blocks_to_chunks,
    merge_small_adjacent_chunks,
    page_to_blocks,
    should_skip_page,
    validate_embedding_input_sizes,
)


class IngestionQualityTests(unittest.TestCase):
    def test_page_to_blocks_preserves_headings_and_paragraphs(self):
        text = """
CAPÍTULO I

Bem-aventurados os aflitos

Primeiro parágrafo com conteúdo suficiente para ser preservado.
Ainda no mesmo parágrafo.

Segundo parágrafo em seguida.
"""
        blocks = page_to_blocks(text, page_number=12)

        self.assertEqual(blocks[0]["type"], "heading")
        self.assertEqual(blocks[0]["text"], "CAPÍTULO I")
        self.assertEqual(blocks[1]["type"], "paragraph")
        self.assertIn("Bem-aventurados os aflitos", blocks[1]["text"])
        self.assertEqual(blocks[2]["type"], "paragraph")
        self.assertTrue(blocks[-1]["type"], "page_break")

    def test_blocks_to_chunks_respects_semantic_boundaries_and_overlap(self):
        page_1 = """
CAPÍTULO I

Tema geral

""" + ("Primeiro parágrafo com muitas palavras para encher o chunk. " * 20) + """

""" + ("Segundo parágrafo com continuação e detalhes doutrinários. " * 18)

        page_2 = """
CAPÍTULO II

Novo tema

""" + ("Terceiro parágrafo em nova seção para validar quebra semântica. " * 20)

        blocks = page_to_blocks(page_1, 1) + page_to_blocks(page_2, 2)
        chunks = blocks_to_chunks(blocks, chunk_size=140, overlap=30, min_chunk_words=60)

        self.assertGreaterEqual(len(chunks), 2)
        self.assertTrue(chunks[0]["text"].startswith("CAPÍTULO I"))
        self.assertTrue(any(chunk["text"].startswith("CAPÍTULO II") for chunk in chunks))
        self.assertTrue(all(chunk["page_end"] >= chunk["page_start"] for chunk in chunks))

        first_tail = set(chunks[0]["text"].split()[-20:])
        second_head = set(chunks[1]["text"].split()[:40])
        self.assertTrue(first_tail & second_head)

    def test_validate_embedding_input_sizes_flags_oversized_inputs(self):
        texts = ["texto curto", "a" * 26000]
        oversized = validate_embedding_input_sizes(texts, max_tokens=6000)
        self.assertEqual(len(oversized), 1)
        self.assertEqual(oversized[0][0], 1)

    def test_should_skip_page_filters_sumario_and_editorial_pages(self):
        self.assertTrue(
            should_skip_page(
                "Capítulo I\nCapítulo II\nCapítulo III\nCapítulo IV\nCapítulo V\nParte Primeira"
            )
        )
        self.assertTrue(
            should_skip_page(
                "Produção Editorial:\nRosiane Dias Rodrigues\nProjeto Gráfico:\nEquipe"
            )
        )
        self.assertFalse(
            should_skip_page(
                "Capítulo I\n\nHá algo de verdadeiro na doutrina quando bem examinada."
            )
        )

    def test_merge_small_adjacent_chunks_absorbs_short_residual_chunk(self):
        chunks = [
            {
                "book": "O Livro dos Espíritos",
                "page_start": 10,
                "page_end": 10,
                "text": "Introdução curta",
                "word_count": 2,
            },
            {
                "book": "O Livro dos Espíritos",
                "page_start": 10,
                "page_end": 11,
                "text": " ".join(["conteudo"] * 80),
                "word_count": 80,
            },
        ]

        merged = merge_small_adjacent_chunks(chunks, min_words=40)
        self.assertEqual(len(merged), 1)
        self.assertIn("Introdução curta", merged[0]["text"])
        self.assertGreaterEqual(merged[0]["word_count"], 82)


class ValidateChunksScriptTests(unittest.TestCase):
    def test_validate_chunks_accepts_minimal_valid_dataset(self):
        sample = [
            {
                "book": "O Livro dos Espíritos",
                "page": 1,
                "page_end": 2,
                "chunk_index": 0,
                "word_count": 60,
                "text": " ".join(["conteudo"] * 60),
            },
            {
                "book": "O Livro dos Médiuns",
                "page": 3,
                "page_end": 3,
                "chunk_index": 1,
                "word_count": 70,
                "text": " ".join(["doutrina"] * 70),
            },
        ]

        with tempfile.TemporaryDirectory() as tmp:
            data_dir = os.path.join(tmp, "data")
            os.makedirs(data_dir, exist_ok=True)
            chunks_path = os.path.join(data_dir, "books_chunks.json")
            with open(chunks_path, "w", encoding="utf-8") as f:
                json.dump(sample, f)

            env = os.environ.copy()
            env["PYTHONPATH"] = SCRIPTS_DIR + os.pathsep + env.get("PYTHONPATH", "")
            script = os.path.join(SCRIPTS_DIR, "validate_chunks.py")
            copied_script = os.path.join(tmp, "validate_chunks.py")
            with open(script, "r", encoding="utf-8") as src, open(copied_script, "w", encoding="utf-8") as dst:
                dst.write(src.read())

            result = subprocess.run(
                [sys.executable, copied_script],
                cwd=tmp,
                env=env,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Quality gate aprovado", result.stdout)


if __name__ == "__main__":
    unittest.main()
