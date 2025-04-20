import os
MODEL_NAME="meta-llama/llama-4-scout-17b-16e-instruct"
# --- Configuration ---
# Embedding model configuration (ensure consistency with main.py)
OLLAMA_EMBED_MODEL = "nomic-embed-text"
# Path to the directory containing PDFs to ingest
# Ensure this 'uploads' directory exists relative to where you run this script
DATA_FOLDER = os.path.join(os.getcwd(), "uploads")
# Text splitting parameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 50
# Directory to persist Chroma DB (ensure consistency with main.py)
CHROMA_DB_PATH = "/home/aishik/Documents/Programming/Hackathons/Hack4Bengal2025/backend/db/chroma_langchain_db"
# Collection name within Chroma DB (ensure consistency with main.py)
CHROMA_COLLECTION_NAME = "documents"
# Interval to check for new files (in seconds)
CHECK_INTERVAL = 10