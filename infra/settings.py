import os

def env(key: str, default):
    return os.getenv(key, default)

# Version
TITLE = env("TITLE", "CychoB0T-uncensored ")
VERSION = env("VERSION", "v0.1.0")

OFFLINE_BACKEND = os.getenv("OFFLINE_BACKEND", "embedded") # values: "embedded" | "server"

# URLs
ONLINE_URL = env("ONLINE_URL", "http://127.0.0.1:9999")
# OFFLINE_URL = env("OFFLINE_URL", "http://host.docker.internal:8080/completion") # docker host
OFFLINE_URL = env("OFFLINE_URL", "http://localhost:8080/completion") # local host

# Database
DB_PATH = env("DB_PATH", "data/memory.db")
VECTOR_DB_PATH = env("VECTOR_DB_PATH", "data/vectors.db")

# Sentence-transformers model
SENTENCE_TRANSFORMERS_MODEL = env("SENTENCE_TRANSFORMERS_MODEL", "models/all-MiniLM-L6-v2")

# API keys
API_KEYS = env("API_KEYS", "API_KEYS")

# Prompt limits
MAX_PROMPT_CHARS = int(env("MAX_PROMPT_CHARS", 4000))
MAX_CONTEXT_CHARS = int(env("MAX_CONTEXT_CHARS", 8000))

# Request size
MAX_BODY_BYTES = int(env("MAX_BODY_BYTES", 64 * 1024))

# Networking
ONLINE_TIMEOUT = int(env("ONLINE_TIMEOUT", 30))
OFFLINE_TIMEOUT = int(env("OFFLINE_TIMEOUT", 180))

# Retries
RETRIES = int(env("RETRIES", 2))
RETRY_BASE_DELAY = int(env("RETRY_BASE_DELAY", 1))

# Concurrency
MAX_CONCURRENT_REQUESTS = int(env("MAX_CONCURRENT_REQUESTS", 2))

# Rate limiting
WINDOW_SECONDS = int(env("WINDOW_SECONDS", 60))
MAX_REQUESTS = int(env("MAX_REQUESTS", 30))
BURST_WINDOW_SEC = int(env("BURST_WINDOW_SEC", 2))
MAX_BURST = int(env("MAX_BURST", 5))

# RAG
ENABLE_RAG = env("ENABLE_RAG", "false").lower() == "true"
RAG_TOP_K = int(env("RAG_TOP_K", 3))
RAG_MAX_CHARS = int(env("RAG_MAX_CHARS", 2000))

# memory decay - # This gives ~50% weight after ~4 hours.
MEMORY_DECAY_LAMBDA = float(env("MEMORY_DECAY_LAMBDA", 0.00005))
