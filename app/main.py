from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.models import user, document, history
from app.routers import auth, documents


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Personal Knowledge Base API",
    description=(
        "Multi-user Personal Knowledge Base API with "
        "document ingestion, embeddings, Qdrant, and MCP."
    ),
    version="1.0.0",
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this before deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API routers
app.include_router(auth.router)
app.include_router(documents.router)


@app.get("/")
def root():
    return {
        "message": "Personal Knowledge Base API is running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "Personal Knowledge Base API",
        "status": "healthy",
    }