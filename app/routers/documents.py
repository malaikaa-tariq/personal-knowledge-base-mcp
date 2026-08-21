from pathlib import Path
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.document import Document
from app.models.user import User
from app.routers.auth import get_current_user
from app.services.chunking import chunk_text
from app.services.embeddings import embed_chunks
from app.services.extraction import (
    DocumentExtractionError,
    SUPPORTED_EXTENSIONS,
    extract_text,
)
from app.services.vector_store import (
    delete_document_vectors,
    upsert_document_chunks,
)


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: Annotated[UploadFile, File()],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filename = file.filename or ""

    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, MD, and TXT files are supported.",
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File is too large. Maximum size is 10 MB.",
        )

    try:
        text = extract_text(
            filename=filename,
            file_bytes=file_bytes,
        )
    except DocumentExtractionError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    chunks = chunk_text(text)

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="No usable text chunks were produced.",
        )

    try:
        vectors = embed_chunks(chunks)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate document embeddings.",
        ) from exc

    document = Document(
        owner_id=current_user.id,
        title=filename,
        content=text,
        file_path=None,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        vector_count = upsert_document_chunks(
            user_id=current_user.id,
            doc_id=document.id,
            filename=filename,
            chunks=chunks,
            vectors=vectors,
        )

    except Exception as exc:
        # Avoid leaving a SQL document without vectors.
        db.delete(document)
        db.commit()

        raise HTTPException(
            status_code=502,
            detail="Document could not be stored in the vector database.",
        ) from exc

    return {
        "id": document.id,
        "filename": document.title,
        "owner_id": document.owner_id,
        "chunks": len(chunks),
        "vectors_stored": vector_count,
        "message": "Document indexed successfully.",
    }


@router.get("")
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    documents = (
        db.query(Document)
        .filter(Document.owner_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )

    return [
        {
            "id": document.id,
            "title": document.title,
            "created_at": document.created_at,
        }
        for document in documents
    ]


@router.get("/{doc_id}")
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = (
        db.query(Document)
        .filter(
            Document.id == doc_id,
            Document.owner_id == current_user.id,
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return {
        "id": document.id,
        "title": document.title,
        "content": document.content,
        "created_at": document.created_at,
    }


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = (
        db.query(Document)
        .filter(
            Document.id == doc_id,
            Document.owner_id == current_user.id,
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    try:
        delete_document_vectors(
            user_id=current_user.id,
            doc_id=document.id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to remove document vectors.",
        ) from exc

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully.",
        "id": doc_id,
    }