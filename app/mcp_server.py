from mcp.server.fastmcp import FastMCP
from qdrant_client import QdrantClient
from typing import Dict, Any

# FastMCP Server Initialization
mcp = FastMCP("KnowledgeBase_Server")

# Qdrant Client Setup (Local execution or cloud URL)
qdrant_client = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "user_documents"

# Minimum similarity score for confidence threshold
SIMILARITY_THRESHOLD = 0.65 

@mcp.tool()
def search_notes(query: str, user_id: str, top_k: int = 3) -> Dict[str, Any]:
    """Search indexed documents using semantic search with user isolation and confidence filtering."""
    try:
        # Dummy vector search placeholder until embeddings are connected by Member 2
        results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=[0.0] * 1536, # Placeholder embedding
            query_filter={"must": [{"key": "user_id", "match": {"value": user_id}}]},
            limit=top_k
        )
        
        filtered_chunks = []
        for res in results:
            if res.score >= SIMILARITY_THRESHOLD:
                filtered_chunks.append({
                    "score": res.score,
                    "content": res.payload.get("content"),
                    "source": res.payload.get("source_file"),
                    "doc_id": res.payload.get("doc_id")
                })
        
        if not filtered_chunks:
            return {"status": "no_match", "message": "No confident match found above threshold."}
            
        return {"status": "success", "data": filtered_chunks}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def get_document(doc_id: str, user_id: str) -> Dict[str, Any]:
    """Fetch complete source document context by doc_id for a specific user."""
    try:
        records, _ = qdrant_client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter={"must": [
                {"key": "user_id", "match": {"value": user_id}},
                {"key": "doc_id", "match": {"value": doc_id}}
            ]},
            limit=100
        )
        
        if not records:
            return {"status": "not_found", "message": f"Document {doc_id} not found."}
            
        full_text = "\n".join([r.payload.get("content", "") for r in records])
        return {"status": "success", "doc_id": doc_id, "content": full_text}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def list_sources(user_id: str) -> Dict[str, Any]:
    """Enumerate all unique source documents indexed for the user."""
    try:
        records, _ = qdrant_client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter={"must": [{"key": "user_id", "match": {"value": user_id}}]},
            limit=500
        )
        
        sources = list(set([r.payload.get("source_file") for r in records if "source_file" in r.payload]))
        return {"status": "success", "sources": sources}

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    mcp.run()
