import os
import re
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from config import LLM_MODEL, LLM_PROVIDER, GROQ_API_KEY, GROQ_MODEL


def clean_llm_output(text: str) -> str:
    """
    Strips out internal reasoning/thinking blocks enclosed in <think>...</think>
    and returns only the clean final response summary.
    """
    if not text:
        return ""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned.strip()


def get_llm():
    provider = (LLM_PROVIDER or "local").strip().lower()

    if provider in ["cloud", "groq"]:
        api_key = GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is empty. Please set GROQ_API_KEY in backend/.env file."
            )
        return ChatGroq(
            model=GROQ_MODEL,
            api_key=api_key
        )

    # Default to local Qwen model via ChatOllama
    return ChatOllama(
        model=LLM_MODEL
    )