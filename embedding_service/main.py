from fastapi import FastAPI
from pydantic import BaseModel

from model import embed_documents

app = FastAPI()


class EmbeddingRequest(BaseModel):
    texts: list[str]

@app.get("/")
def home():
    return {"message": "Embedding Service API"}

@app.post("/embed")
def embed(request: EmbeddingRequest):
    embeddings = embed_documents(request.texts)

    return {
        "embeddings": embeddings
    }