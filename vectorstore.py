from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def create_retriever(chunks, persist_directory="./chroma_db"):
    vector_store = Chroma.from_documents(
        documents = chunks,
        embedding = embeddings,
        persist_directory = persist_directory
    )

    retriever = vector_store.as_retriever(
        search_type = "mmr",
        search_kwargs = {"k": 4}
    )

    return retriever