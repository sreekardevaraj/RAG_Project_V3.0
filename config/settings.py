from dotenv import load_dotenv
import os

load_dotenv()

# Base Directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# LLM
GROQ_API_KEY   = os.getenv("GROQ_API_KEY")
LLM_MODEL_NAME = "llama-3.3-70b-versatile"

# Embeddings
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Splitter
CHUNK_SIZE    = 520
CHUNK_OVERLAP = 50

# Paths
RAW_PDF_DIR   = os.path.join(BASE_DIR, "data", "raw")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "storage", "vector_db")

# Router
RELEVANCE_THRESHOLD = 0.45

# Web Search
WEB_SEARCH_MAX_RESULTS = 5

# Memory
MAX_MEMORY_MESSAGES = 10

# Follow-up
NUM_FOLLOWUP_QUESTIONS = 3