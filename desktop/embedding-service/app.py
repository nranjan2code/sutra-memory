"""
Simple embedding service for Sutra Desktop Edition.
Uses sentence-transformers for generating embeddings.
"""
import os
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

app = FastAPI(title="Sutra Embedding Service")

# Load model on startup
MODEL_NAME = os.getenv("MODEL_NAME", "all-mpnet-base-v2")
VECTOR_DIMENSION = int(os.getenv("VECTOR_DIMENSION", "768"))

print(f"Loading model: {MODEL_NAME}")
model = SentenceTransformer(MODEL_NAME)
print(f"Model loaded. Expected dimension: {VECTOR_DIMENSION}")


class EmbeddingRequest(BaseModel):
    text: str | List[str]


class EmbeddingResponse(BaseModel):
    embeddings: List[List[float]]
    dimension: int


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model": MODEL_NAME,
        "dimension": VECTOR_DIMENSION
    }


@app.post("/embed", response_model=EmbeddingResponse)
async def generate_embeddings(request: EmbeddingRequest):
    """Generate embeddings for input text."""
    try:
        texts = [request.text] if isinstance(request.text, str) else request.text
        
        # Generate embeddings
        embeddings = model.encode(texts, convert_to_numpy=True)
        
        # Convert to list format
        embeddings_list = embeddings.tolist()
        
        return EmbeddingResponse(
            embeddings=embeddings_list,
            dimension=len(embeddings_list[0])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Sutra Embedding Service",
        "model": MODEL_NAME,
        "dimension": VECTOR_DIMENSION,
        "endpoints": {
            "health": "/health",
            "embed": "/embed (POST)"
        }
    }
