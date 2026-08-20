import numpy as np
import pytest

from app.services import embeddings


class FakeEmbeddingModel:
    def encode(
        self,
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    ):
        if isinstance(texts, str):
            return np.ones(
                embeddings.EMBEDDING_DIMENSION,
                dtype=np.float32,
            )

        return np.ones(
            (
                len(texts),
                embeddings.EMBEDDING_DIMENSION,
            ),
            dtype=np.float32,
        )


def test_embed_text(monkeypatch):
    monkeypatch.setattr(
        embeddings,
        "get_embedding_model",
        lambda: FakeEmbeddingModel(),
    )

    vector = embeddings.embed_text(
        "Semantic search uses embeddings."
    )

    assert isinstance(vector, list)
    assert len(vector) == 384
    assert all(isinstance(value, float) for value in vector)


def test_embed_chunks(monkeypatch):
    monkeypatch.setattr(
        embeddings,
        "get_embedding_model",
        lambda: FakeEmbeddingModel(),
    )

    chunks = [
        "Software engineering notes.",
        "Vector databases store embeddings.",
        "MCP exposes callable tools.",
    ]

    vectors = embeddings.embed_chunks(chunks)

    assert len(vectors) == 3

    for vector in vectors:
        assert len(vector) == 384


def test_empty_chunk_list(monkeypatch):
    monkeypatch.setattr(
        embeddings,
        "get_embedding_model",
        lambda: FakeEmbeddingModel(),
    )

    assert embeddings.embed_chunks([]) == []


def test_empty_text_rejected():
    with pytest.raises(ValueError):
        embeddings.embed_text("")


def test_blank_text_rejected():
    with pytest.raises(ValueError):
        embeddings.embed_text("   ")


def test_empty_chunk_rejected(monkeypatch):
    monkeypatch.setattr(
        embeddings,
        "get_embedding_model",
        lambda: FakeEmbeddingModel(),
    )

    with pytest.raises(ValueError):
        embeddings.embed_chunks(
            [
                "valid chunk",
                "",
            ]
        )