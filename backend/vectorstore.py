from langchain_chroma import Chroma
from config import  CHROMA_DIR
from config import (
    SEARCH_TYPE,
    TOP_K,
    FETCH_K,
    LAMBDA_MULT,
)
from fastapi import HTTPException
import os
from services.embedding_client import get_embeddings

class RemoteEmbeddings:

    def embed_documents(self, texts):
        return get_embeddings(texts)

    def embed_query(self, text):
        return get_embeddings([text])[0]

embeddings = RemoteEmbeddings()

def create_vector_store(chunks, persist_directory=CHROMA_DIR):
    vector_store = Chroma.from_documents(
        documents = chunks,
        embedding = embeddings,
        persist_directory = persist_directory
    )
    return vector_store

def load_vector_store():
    if not os.path.exists(CHROMA_DIR):
        raise HTTPException(
            status_code=404, detail="Vector store not found. Please upload a resume first."
        )

    vector_store = Chroma(
        persist_directory = CHROMA_DIR,
        embedding_function = embeddings
    )

    if vector_store._collection.count() == 0:
        raise HTTPException(
            status_code=404, detail="Vector store is empty. Please upload a resume first."
        )

    return vector_store

def get_retriever():
    vector_store = load_vector_store()
    print(vector_store._collection.count())
    retriever = vector_store.as_retriever(
        search_type = SEARCH_TYPE,
        search_kwargs = {
            "k": TOP_K,
            "fetch_k": FETCH_K,
            "lambda_mult": LAMBDA_MULT
        }
        
    )

    return retriever
