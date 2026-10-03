import pytest
import requests
from embeddings import get_embedding_model


def ollama_is_running():
    try:
        requests.get("http://localhost:11434", timeout=2)
        return True
    except requests.exceptions.ConnectionError:
        return False


@pytest.mark.skipif(not ollama_is_running(), reason="Ollama is not running locally")
def test_embedding_model_returns_correct_dimension():
    model = get_embedding_model()
    vector = model.embed_query("texto de prueba")
    assert len(vector) == 768
    assert all(isinstance(value, float) for value in vector)