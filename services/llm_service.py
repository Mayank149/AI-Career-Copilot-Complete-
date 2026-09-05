import os
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from config import LLM_MODEL, LLM_PROVIDER, GROQ_API_KEY, GROQ_MODEL

def get_llm():
    provider = (LLM_PROVIDER or "local").strip().lower()

    if provider in ["cloud", "groq"]:
        api_key = GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is empty. Please set GROQ_API_KEY in config.py or export GROQ_API_KEY as an environment variable."
            )
        return ChatGroq(
            model=GROQ_MODEL,
            api_key=api_key
        )

    # Default to local Qwen model via ChatOllama
    return ChatOllama(
        model=LLM_MODEL
    )