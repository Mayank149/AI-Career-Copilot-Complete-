# Directories
UPLOAD_DIR = "uploads"
CHROMA_DIR = "chroma_db"

# Embedding Model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# LLM
LLM_MODEL = "qwen2.5:7b"

# Text Splitting
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# Retrieval
SEARCH_TYPE = "mmr"

TOP_K = 4
FETCH_K = 10
LAMBDA_MULT = 0.5