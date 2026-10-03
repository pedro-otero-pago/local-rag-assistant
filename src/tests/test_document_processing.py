import os
import pytest
from document_processing import load_pdf_text, split_text

TEST_PDF = os.path.join(os.path.dirname(__file__), "..", "..", "data", "MAAAI_Tema_1.pdf")


# --- load_pdf_text ---

def test_load_pdf_text_returns_string():
    text = load_pdf_text(TEST_PDF)
    assert isinstance(text, str)
    assert len(text) > 0


def test_load_pdf_text_extracts_known_content():
    text = load_pdf_text(TEST_PDF)
    assert "APRENDIZAJE INCREMENTAL" in text
    assert "concept drift" in text.lower() or "Concept drift" in text


# --- split_text ---

def test_split_text_returns_list_of_strings():
    chunks = split_text("Este es un texto de prueba. " * 50)
    assert isinstance(chunks, list)
    assert all(isinstance(chunk, str) for chunk in chunks)


def test_split_text_respects_chunk_size_roughly():
    text = "Este es un texto de prueba. " * 100
    chunks = split_text(text)
    for chunk in chunks:
        assert len(chunk) <= 600  # chunk_size=500 with some tolerance for splitter boundaries


def test_split_text_short_text_returns_single_chunk():
    short_text = "Un texto corto."
    chunks = split_text(short_text)
    assert len(chunks) == 1
    assert chunks[0] == short_text


def test_split_text_consecutive_chunks_overlap():
    text = "Palabra uno dos tres cuatro cinco seis siete ocho. " * 30
    chunks = split_text(text)
    if len(chunks) > 1:
        end_of_first = chunks[0][-20:]
        assert end_of_first in chunks[1] or any(
            word in chunks[1] for word in end_of_first.split()
        )


def test_split_text_empty_string_returns_empty_list():
    chunks = split_text("")
    assert chunks == []