from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from config import EMBEDDING_MODEL, CHROMA_DIR
from config import (
    SEARCH_TYPE,
    TOP_K,
    FETCH_K,
    LAMBDA_MULT,
)

embeddings = HuggingFaceEmbeddings(
    model_name = EMBEDDING_MODEL
)

def create_vector_store(chunks, persist_directory="./chroma_db"):
    vector_store = Chroma.from_documents(
        documents = chunks,
        embedding = embeddings,
        persist_directory = persist_directory
    )
    return vector_store

def load_vector_store():
    return Chroma(
        persist_directory = CHROMA_DIR,
        embedding_function = embeddings
    )

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
