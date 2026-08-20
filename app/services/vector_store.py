from functools import lru_cache
from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient, models

from app.core.config import settings


class VectorStoreError(RuntimeError):
    """Raised when the Qdrant vector store cannot be used."""


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    """
    Create and reuse the Qdrant Cloud client.
    """

    if not settings.QDRANT_URL:
        raise VectorStoreError(
            "QDRANT_URL is not configured."
        )

    if not settings.QDRANT_API_KEY:
        raise VectorStoreError(
            "QDRANT_API_KEY is not configured."
        )

    return QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
    )


def ensure_collection() -> None:
    """
    Create the vector collection and payload indexes
    if they do not already exist.
    """

    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION

    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=settings.EMBEDDING_DIMENSION,
                distance=models.Distance.COSINE,
            ),
        )

    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name="user_id",
            field_schema=models.KeywordIndexParams(
                type=models.KeywordIndexType.KEYWORD,
                is_tenant=True,
            ),
        )
    except Exception as exc:
        message = str(exc).lower()

        if (
            "already exists" not in message
            and "already exist" not in message
        ):
            raise

    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name="doc_id",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
    except Exception as exc:
        message = str(exc).lower()

        if (
            "already exists" not in message
            and "already exist" not in message
        ):
            raise


def _point_id(
    user_id: int | str,
    doc_id: int | str,
    chunk_index: int,
) -> str:
    key = f"{user_id}:{doc_id}:{chunk_index}"

    return str(
        uuid5(
            NAMESPACE_URL,
            key,
        )
    )


def upsert_document_chunks(
    user_id: int | str,
    doc_id: int | str,
    filename: str,
    chunks: list[str],
    vectors: list[list[float]],
) -> int:
    if not chunks:
        return 0

    if len(chunks) != len(vectors):
        raise ValueError(
            "Number of chunks must match number of vectors."
        )

    ensure_collection()

    points: list[models.PointStruct] = []

    for chunk_index, (chunk, vector) in enumerate(
        zip(chunks, vectors)
    ):
        if len(vector) != settings.EMBEDDING_DIMENSION:
            raise ValueError(
                f"Vector {chunk_index} has dimension "
                f"{len(vector)}; expected "
                f"{settings.EMBEDDING_DIMENSION}."
            )

        points.append(
            models.PointStruct(
                id=_point_id(
                    user_id=user_id,
                    doc_id=doc_id,
                    chunk_index=chunk_index,
                ),
                vector=vector,
                payload={
                    "user_id": str(user_id),
                    "doc_id": str(doc_id),
                    "filename": filename,
                    "chunk_index": chunk_index,
                    "text": chunk,
                },
            )
        )

    client = get_qdrant_client()

    client.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=points,
        wait=True,
    )

    return len(points)


def delete_document_vectors(
    user_id: int | str,
    doc_id: int | str,
) -> None:
    client = get_qdrant_client()

    client.delete(
        collection_name=settings.QDRANT_COLLECTION,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="user_id",
                        match=models.MatchValue(
                            value=str(user_id),
                        ),
                    ),
                    models.FieldCondition(
                        key="doc_id",
                        match=models.MatchValue(
                            value=str(doc_id),
                        ),
                    ),
                ]
            )
        ),
        wait=True,
    )


def search_vectors(
    user_id: int | str,
    query_vector: list[float],
    limit: int = 5,
):
    if len(query_vector) != settings.EMBEDDING_DIMENSION:
        raise ValueError(
            "Query vector has invalid dimension."
        )

    if limit <= 0:
        raise ValueError(
            "limit must be greater than 0."
        )

    client = get_qdrant_client()

    result = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="user_id",
                    match=models.MatchValue(
                        value=str(user_id),
                    ),
                )
            ]
        ),
        limit=limit,
        with_payload=True,
    )

    return result.points