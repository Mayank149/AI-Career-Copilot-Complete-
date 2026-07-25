from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def create_vector_store(chunks, persist_directory="./chroma_db"):
    vector_store = Chroma.from_documents(
        documents = chunks,
        embedding = embeddings,
        persist_directory = persist_directory
    )
    return vector_store

def load_vectore_store():
    return Chroma(
        persist_directory = "./chroma_db",
        embedding_function = embeddings
    )

def create_retriever():
    vector_store = load_vectore_store()
    
    retriever = vector_store.as_retriever(
        search_type = "mmr",
        search_kwargs = {"k": 4},
        fetch_k = 10,
        lambda_mult = 0.5
    )

    return retriever