from langchain_chroma import Chroma
from config import CHROMA_DIR
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

def create_vector_store(chunks, persist_directory=CHROMA_DIR, ids=None):
    vector_store = Chroma.from_documents(
        documents = chunks,
        embedding = embeddings,
        persist_directory = persist_directory,
        ids = ids
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


def reindex_active_resume():
    """
    Reloads active resume.pdf, splits text into chunks, assigns chunk_id metadata,
    resets ChromaDB collection, and indexes the new chunks.
    """
    from services.resume_service import load_resume_documents
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from config import CHUNK_SIZE, CHUNK_OVERLAP

    documents = load_resume_documents()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = text_splitter.split_documents(documents)

    for i, chunk in enumerate(chunks):
        chunk.metadata = dict(chunk.metadata)
        chunk.metadata["chunk_id"] = f"chunk_{i}"

    # Reset existing collection if present
    if os.path.exists(CHROMA_DIR):
        try:
            vs = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
            vs.delete_collection()
        except Exception as e:
            print(f"[WARN] Error resetting collection: {e}")

    ids = [chunk.metadata["chunk_id"] for chunk in chunks]
    create_vector_store(chunks, ids=ids)
    return len(chunks)
