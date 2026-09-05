import os
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
import config

def get_llm():
    provider = (config.LLM_PROVIDER or "local").strip().lower()

    if provider in ["cloud", "groq"]:
        api_key = config.GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is empty. Please set GROQ_API_KEY in config.py or export GROQ_API_KEY as an environment variable."
            )
        return ChatGroq(
            model=config.GROQ_MODEL,
            groq_api_key=api_key,
            max_tokens=1500
        )

    # Default to local Qwen model via ChatOllama
    return ChatOllama(
        model=config.LLM_MODEL,
        base_url=config.OLLAMA_BASE_URL
    )