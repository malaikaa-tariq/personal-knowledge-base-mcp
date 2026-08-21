import pytest

from app.services import vector_store


class FakeQueryResult:
    def __init__(self):
        self.points = [
            {
                "score": 0.91,
                "payload": {
                    "user_id": "1",
                    "doc_id": "10",
                },
            }
        ]


class FakeQdrantClient:
    def __init__(self):
        self.created_collection = None
        self.indexes = []
        self.upserted_points = []
        self.deleted_selector = None
        self.query_filter = None

    def collection_exists(self, collection_name):
        return False

    def create_collection(
        self,
        collection_name,
        vectors_config,
    ):
        self.created_collection = (
            collection_name,
            vectors_config,
        )

    def create_payload_index(
        self,
        collection_name,
        field_name,
        field_schema,
    ):
        self.indexes.append(
            (
                collection_name,
                field_name,
                field_schema,
            )
        )

    def upsert(
        self,
        collection_name,
        points,
        wait,
    ):
        self.upserted_points = points

    def delete(
        self,
        collection_name,
        points_selector,
        wait,
    ):
        self.deleted_selector = points_selector

    def query_points(
        self,
        collection_name,
        query,
        query_filter,
        limit,
        with_payload,
    ):
        self.query_filter = query_filter
        return FakeQueryResult()


@pytest.fixture
def fake_client(monkeypatch):
    client = FakeQdrantClient()

    monkeypatch.setattr(
        vector_store,
        "get_qdrant_client",
        lambda: client,
    )

    return client


def fake_vector():
    return [
        0.01
        for _ in range(
            vector_store.settings.EMBEDDING_DIMENSION
        )
    ]


def test_ensure_collection(fake_client):
    vector_store.ensure_collection()

    assert fake_client.created_collection is not None

    field_names = [
        item[1]
        for item in fake_client.indexes
    ]

    assert "user_id" in field_names
    assert "doc_id" in field_names


def test_upsert_document_chunks(fake_client):
    chunks = [
        "First semantic search chunk.",
        "Second knowledge base chunk.",
    ]

    vectors = [
        fake_vector(),
        fake_vector(),
    ]

    count = vector_store.upsert_document_chunks(
        user_id=1,
        doc_id=20,
        filename="notes.txt",
        chunks=chunks,
        vectors=vectors,
    )

    assert count == 2
    assert len(fake_client.upserted_points) == 2

    first = fake_client.upserted_points[0]

    assert first.payload["user_id"] == "1"
    assert first.payload["doc_id"] == "20"
    assert first.payload["filename"] == "notes.txt"
    assert first.payload["chunk_index"] == 0
    assert first.payload["text"] == chunks[0]


def test_chunk_vector_count_must_match(fake_client):
    with pytest.raises(ValueError):
        vector_store.upsert_document_chunks(
            user_id=1,
            doc_id=1,
            filename="notes.txt",
            chunks=["one", "two"],
            vectors=[fake_vector()],
        )


def test_wrong_vector_dimension_rejected(fake_client):
    with pytest.raises(ValueError):
        vector_store.upsert_document_chunks(
            user_id=1,
            doc_id=1,
            filename="notes.txt",
            chunks=["content"],
            vectors=[[0.1, 0.2]],
        )


def test_empty_chunks_returns_zero(fake_client):
    count = vector_store.upsert_document_chunks(
        user_id=1,
        doc_id=1,
        filename="empty.txt",
        chunks=[],
        vectors=[],
    )

    assert count == 0


def test_delete_document_vectors(fake_client):
    vector_store.delete_document_vectors(
        user_id=8,
        doc_id=100,
    )

    assert fake_client.deleted_selector is not None


def test_search_vectors_has_user_filter(fake_client):
    results = vector_store.search_vectors(
        user_id=55,
        query_vector=fake_vector(),
        limit=5,
    )

    assert len(results) == 1
    assert fake_client.query_filter is not None

    condition = fake_client.query_filter.must[0]

    assert condition.key == "user_id"
    assert condition.match.value == "55"


def test_search_rejects_invalid_dimension(fake_client):
    with pytest.raises(ValueError):
        vector_store.search_vectors(
            user_id=1,
            query_vector=[0.1, 0.2],
        )


def test_search_rejects_invalid_limit(fake_client):
    with pytest.raises(ValueError):
        vector_store.search_vectors(
            user_id=1,
            query_vector=fake_vector(),
            limit=0,
        )