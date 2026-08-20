from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app
from app.routers import documents

# Import models so SQLAlchemy knows about all tables.
from app.models import user as user_model
from app.models import document as document_model
from app.models import history as history_model


client = TestClient(app)


@pytest.fixture
def isolated_database():
    """
    Give the document tests their own temporary SQLite database.

    This prevents tests/test_auth.py and tests/test_documents.py
    from interfering with each other's database setup/cleanup.
    """

    test_engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    # Create users, documents, search history, etc.
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    # Remember any previous override created by another test module.
    previous_override = app.dependency_overrides.get(get_db)

    # Use our isolated DB during this test.
    app.dependency_overrides[get_db] = override_get_db

    try:
        yield
    finally:
        # Restore whatever dependency state existed before this test.
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override

        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


def create_user_and_token(
    email: str,
    password: str = "StrongPassword123",
):
    signup_response = client.post(
        "/auth/signup",
        json={
            "email": email,
            "password": password,
            "full_name": email.split("@")[0],
        },
    )

    assert signup_response.status_code in (200, 201), signup_response.text

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200, login_response.text

    return login_response.json()["access_token"]


def auth_header(token: str):
    return {
        "Authorization": f"Bearer {token}"
    }


def test_users_cannot_access_each_others_documents(
    monkeypatch,
    isolated_database,
):
    """
    Verify multi-user document isolation.

    User A:
    - uploads a document
    - can list it
    - can retrieve it

    User B:
    - cannot see User A's document
    - cannot retrieve User A's document

    Also verify that the correct user ID is sent
    to the vector-storage layer.
    """

    # ---------------------------------------------------------
    # Mock text extraction
    # ---------------------------------------------------------

    monkeypatch.setattr(
        documents,
        "extract_text",
        lambda *_args, **_kwargs:
        "Semantic search uses embeddings to retrieve related information.",
    )

    # ---------------------------------------------------------
    # Mock chunking
    # ---------------------------------------------------------

    monkeypatch.setattr(
        documents,
        "chunk_text",
        lambda *_args, **_kwargs: [
            "Semantic search uses embeddings to retrieve related information."
        ],
    )

    # ---------------------------------------------------------
    # Mock embeddings
    # ---------------------------------------------------------

    monkeypatch.setattr(
        documents,
        "embed_chunks",
        lambda *_args, **_kwargs: [
            [0.0] * 384
        ],
    )

    # ---------------------------------------------------------
    # Mock Qdrant
    # ---------------------------------------------------------

    captured = {}

    def fake_upsert(
        user_id,
        doc_id,
        filename,
        chunks,
        vectors,
    ):
        captured["user_id"] = str(user_id)
        captured["doc_id"] = str(doc_id)
        captured["filename"] = filename
        captured["chunks"] = chunks
        captured["vectors"] = vectors

        return len(chunks)

    monkeypatch.setattr(
        documents,
        "upsert_document_chunks",
        fake_upsert,
    )

    # ---------------------------------------------------------
    # Create two unique users
    # ---------------------------------------------------------

    unique_id = uuid4().hex[:8]

    email_a = f"member2-user-a-{unique_id}@example.com"
    email_b = f"member2-user-b-{unique_id}@example.com"

    token_a = create_user_and_token(email_a)
    token_b = create_user_and_token(email_b)

    # ---------------------------------------------------------
    # User A uploads a private document
    # ---------------------------------------------------------

    upload = client.post(
        "/documents/upload",
        headers=auth_header(token_a),
        files={
            "file": (
                "private-notes.txt",
                b"Private software engineering notes",
                "text/plain",
            )
        },
    )

    assert upload.status_code == 201, upload.text

    uploaded = upload.json()

    document_id = uploaded["id"]
    owner_id = uploaded["owner_id"]

    # ---------------------------------------------------------
    # Verify upload
    # ---------------------------------------------------------

    assert uploaded["filename"] == "private-notes.txt"
    assert uploaded["chunks"] == 1
    assert uploaded["vectors_stored"] == 1

    assert (
        uploaded["message"]
        == "Document indexed successfully."
    )

    # ---------------------------------------------------------
    # Verify tenant data sent to Qdrant
    # ---------------------------------------------------------

    assert captured["user_id"] == str(owner_id)
    assert captured["doc_id"] == str(document_id)

    assert (
        captured["filename"]
        == "private-notes.txt"
    )

    assert len(captured["chunks"]) == 1
    assert len(captured["vectors"]) == 1
    assert len(captured["vectors"][0]) == 384

    # ---------------------------------------------------------
    # User A can list their document
    # ---------------------------------------------------------

    response_a = client.get(
        "/documents",
        headers=auth_header(token_a),
    )

    assert response_a.status_code == 200, response_a.text

    documents_a = response_a.json()

    assert any(
        item["id"] == document_id
        for item in documents_a
    )

    # ---------------------------------------------------------
    # User A can retrieve their own document
    # ---------------------------------------------------------

    own_document = client.get(
        f"/documents/{document_id}",
        headers=auth_header(token_a),
    )

    assert own_document.status_code == 200, own_document.text

    own_document_data = own_document.json()

    assert own_document_data["id"] == document_id

    # ---------------------------------------------------------
    # User B cannot see User A's document
    # ---------------------------------------------------------

    response_b = client.get(
        "/documents",
        headers=auth_header(token_b),
    )

    assert response_b.status_code == 200, response_b.text

    documents_b = response_b.json()

    assert not any(
        item["id"] == document_id
        for item in documents_b
    )

    # ---------------------------------------------------------
    # User B cannot retrieve User A's document
    # ---------------------------------------------------------

    forbidden_document = client.get(
        f"/documents/{document_id}",
        headers=auth_header(token_b),
    )

    assert forbidden_document.status_code == 404