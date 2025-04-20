from uuid import uuid4
from langchain.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from config import config
from dotenv import load_dotenv
from uuid import uuid4
from .vars import *
load_dotenv()

class RAG:
    """Class to handle the ingestion of PDF files into a vector store."""
    
    embeddings = OllamaEmbeddings(model=OLLAMA_EMBED_MODEL)
    
    vector_store = Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_PATH,
    )
    
    @classmethod
    def ingest_file(cls, file_path: str):
        """Loads, splits, cleans, and ingests a single PDF file into Chroma."""
        
        if not file_path.lower().endswith('.pdf'):
            print(f"Skipping non-PDF file: {file_path}")
            return

        try:
            print(f"Loading PDF: {file_path}")
            loader = PyPDFLoader(file_path=file_path)
            loaded_documents = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                separators=["\n\n", "\n", " ", ""]
            )
            docs = text_splitter.split_documents(loaded_documents)
            cleaned_docs = []
            doc_ids = []
            for i, doc in enumerate(docs):
                try:
                    cleaned_content = doc.page_content.encode('utf-8', errors='replace').decode('utf-8')

                    if not cleaned_content.strip():
                        continue
                    
                    doc.page_content = cleaned_content
                    cleaned_docs.append(doc)
                    doc_ids.append(str(uuid4()))
                except Exception as e:
                    continue

            if cleaned_docs: 
                cls.vector_store.add_documents(documents=cleaned_docs, ids=doc_ids)
                
            else:
                pass

        except Exception as e:
            pass

if __name__ == "__main__":
    rag = RAG()
    rag.ingest_file("/home/aishik/Documents/Programming/Hackathons/Hack4Bengal2025/backend/uploads/documents/4b973b38-a0f5-4dda-a503-2bea6b73badf.pdf")