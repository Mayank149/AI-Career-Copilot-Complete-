from langchain_ollama import ChatOllama
from config import LLM_MODEL

llm = ChatOllama(
    model=LLM_MODEL
)

def get_llm():
    return llm