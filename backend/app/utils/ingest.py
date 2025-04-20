import os
import time
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from uuid import uuid4
# from .vars import *

# Load environment variables (if any, e.g., for Ollama settings)
load_dotenv()

MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"
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

# --- Initialization ---
print("Initializing Ollama embeddings...")
try:
    # Initialize the embedding function
    embeddings = OllamaEmbeddings(model=OLLAMA_EMBED_MODEL)
except Exception as e:
    print(f"Error initializing OllamaEmbeddings: {e}")
    print(
        f"Ensure Ollama is running and the model '{OLLAMA_EMBED_MODEL}' is available.")
    exit()

print(f"Initializing Chroma vector store at: {CHROMA_DB_PATH}")
try:
    # Initialize Chroma vector store
    vector_store = Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_PATH,
    )
    print(
        f"Chroma vector store initialized. Collection: '{CHROMA_COLLECTION_NAME}'")
except Exception as e:
    print(f"Error initializing Chroma DB from {CHROMA_DB_PATH}: {e}")
    print("Ensure the Chroma DB directory exists and is accessible.")
    exit()

# --- File Ingestion Function ---


def ingest_file(file_path: str):
    """Loads, splits, cleans, and ingests a single PDF file into Chroma."""
    print(f"--- Starting ingestion for file: {file_path} ---")

    # Skip non-PDF files
    if not file_path.lower().endswith('.pdf'):
        print(f"Skipping non-PDF file: {file_path}")
        return

    try:
        # 1. Load PDF
        print(f"Loading PDF: {file_path}")
        loader = PyPDFLoader(file_path=file_path)
        loaded_documents = loader.load()
        print(f"Loaded {len(loaded_documents)} pages from PDF.")

        # 2. Split Documents
        print("Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            # Added more separators for robustness
            separators=["\n\n", "\n", " ", ""]
        )
        docs = text_splitter.split_documents(loaded_documents)
        print(f"Split into {len(docs)} document chunks.")

        # 3. Clean Documents and Generate IDs
        print("Cleaning document chunks and generating IDs...")
        cleaned_docs = []
        doc_ids = []
        for i, doc in enumerate(docs):
            try:
                # **FIX:** Clean page content by encoding to UTF-8 (replacing errors)
                # and decoding back. This removes/replaces problematic characters
                # like surrogates that cause issues downstream.
                cleaned_content = doc.page_content.encode(
                    'utf-8', errors='replace').decode('utf-8')
                doc.metadata['filename'] = os.path.basename(file_path)
                # Check if cleaning resulted in empty content (optional)
                if not cleaned_content.strip():
                    print(
                        f"Warning: Chunk {i} became empty after cleaning. Skipping.")
                    continue

                # Update the document's content
                doc.page_content = cleaned_content
                cleaned_docs.append(doc)
                # Generate UUID only for successfully cleaned docs
                doc_ids.append(str(uuid4()))
            except Exception as e:
                print(
                    f"Warning: Could not process/clean document chunk {i}: {e}. Skipping.")

        print(
            f"Successfully processed {len(cleaned_docs)} document chunks for ingestion.")

        # 4. Add to Vector Store
        if cleaned_docs:  # Only add if there are documents left after cleaning
            print(
                f"Adding {len(cleaned_docs)} cleaned documents to the vector store...")
            vector_store.add_documents(documents=cleaned_docs, ids=doc_ids)
            print(
                f"Successfully added {len(cleaned_docs)} documents to Chroma collection '{CHROMA_COLLECTION_NAME}'.")
        else:
            print(
                "No valid documents were found to add to the vector store after cleaning.")

    except Exception as e:
        print(f"Error during ingestion of {file_path}: {e}")

    print(f"--- Finished ingestion for file: {file_path} ---")


# --- Main Watch Loop ---
list_of_ingested_files = []


def main():
    """Monitors the data folder and ingests new PDF files."""
    print(f"Monitoring folder '{DATA_FOLDER}' for new PDF files...")
    if not os.path.exists(DATA_FOLDER):
        print(
            f"Error: Data folder '{DATA_FOLDER}' does not exist. Please create it.")
        exit()
    while True:
        try:
            files = os.listdir(DATA_FOLDER)
            ingested_something = False
            for file in files:
                # Process files that are PDFs and don't start with "ingested_"
                if file.lower().endswith('.pdf') and not file.startswith("ingested_"):
                    file_path = os.path.join(DATA_FOLDER, file)
                    ingest_file(file_path)
                    file_name = os.path.basename(file_path)
                    list_of_ingested_files.append(file_name)
                    # from test import knowledge_base
                    # knowledge_base.load(recreate=True)
                    # Rename the file to mark it as ingested
                    try:
                        new_file = "ingested_" + file
                        new_file_path = os.path.join(DATA_FOLDER, new_file)
                        os.rename(file_path, new_file_path)
                        print(f"Renamed '{file}' to '{new_file}'")
                        ingested_something = True
                    except OSError as e:
                        print(f"Error renaming file {file}: {e}")

            if not ingested_something:
                print(
                    f"No new files found. Waiting for {CHECK_INTERVAL} seconds...")

            # Wait before checking again
            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\nIngestion process stopped by user.")
            break
        except Exception as e:
            print(f"An unexpected error occurred in the main loop: {e}")
            # Optional: add a longer sleep here to prevent rapid error loops
            time.sleep(CHECK_INTERVAL * 2)


if __name__ == "__main__":
    main()
