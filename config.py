import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

# Directories
UPLOAD_DIR = str(BASE_DIR / "uploads")
CHROMA_DIR = str(BASE_DIR / "chroma_db")

# Embedding Model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# LLM
LLM_MODEL = "qwen2.5:7b"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "cloud")  # "local" for Qwen/Ollama, "cloud" for Groq API
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# Text Splitting
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# Retrieval
SEARCH_TYPE = "mmr"

TOP_K = 4
FETCH_K = 10
LAMBDA_MULT = 0.5