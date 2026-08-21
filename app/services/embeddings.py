from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load the embedding model once and reuse it.

    lru_cache prevents the model from being downloaded/loaded
    again for every request.
    """
    return SentenceTransformer(MODEL_NAME)


def embed_text(text: str) -> list[float]:
    """
    Generate one normalized embedding vector for a string.
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    model = get_embedding_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    vector = embedding.astype(np.float32).tolist()

    if len(vector) != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Unexpected embedding dimension: {len(vector)}. "
            f"Expected {EMBEDDING_DIMENSION}."
        )

    return vector


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """
    Generate normalized embeddings for multiple text chunks.
    """

    if not chunks:
        return []

    if any(not chunk or not chunk.strip() for chunk in chunks):
        raise ValueError("Chunks cannot contain empty text.")

    model = get_embedding_model()

    embeddings = model.encode(
        chunks,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    vectors = embeddings.astype(np.float32).tolist()

    for vector in vectors:
        if len(vector) != EMBEDDING_DIMENSION:
            raise ValueError(
                f"Unexpected embedding dimension: {len(vector)}."
            )

    return vectors