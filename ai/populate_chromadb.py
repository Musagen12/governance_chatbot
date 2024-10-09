from fastapi import APIRouter, HTTPException
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_chroma import Chroma
from .get_embeddings import get_embedding_function
import os
import shutil

router = APIRouter()

CHROMA_PATH = "chroma"  # Path where Chroma DB will be stored
DATA_PATH = "/teamspace/studios/this_studio/governance_chatbot/data_sources"  # Directory for document sources

@router.post("/populate_db", status_code=200)
def populate_chroma_db(reset: bool = False):
    """Endpoint to populate Chroma DB with documents from the specified directory."""
    try:
        if reset:
            print("✨ Clearing Database")
            clear_database()

        # Load text documents and split them
        documents = load_documents()
        if not documents:
            return {"message": "No documents found to load"}

        chunks = split_documents(documents)

        # Add to Chroma DB
        add_to_chroma(chunks)
        return {"message": "Database populated successfully."}

    except Exception as e:
        print(f"Error populating database: {e}")
        raise HTTPException(status_code=500, detail=f"Error populating database: {str(e)}")

def load_documents() -> list[Document]:
    """Load all documents from the specified directory using PyPDFDirectoryLoader."""
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()

def split_documents(documents: list[Document]) -> list:
    """Split documents into chunks using RecursiveCharacterTextSplitter."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def add_to_chroma(chunks: list[Document]):
    """Add the text chunks to the Chroma DB."""
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    
    chunks_with_ids = calculate_chunk_ids(chunks)
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    
    print(f"Number of existing documents in DB: {len(existing_ids)}")  # Debug existing items

    new_chunks = [chunk for chunk in chunks_with_ids if chunk.metadata["id"] not in existing_ids]
    
    if new_chunks:
        print(f"👉 Adding new documents: {len(new_chunks)}")  # Debug added documents
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)

    else:
        print("✅ No new documents to add")

def calculate_chunk_ids(chunks: list[Document]) -> list[Document]:
    """Assign unique IDs to each chunk based on source and chunk index."""
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        current_page_id = f"{source}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        chunk.metadata["id"] = chunk_id
        last_page_id = current_page_id

    return chunks

def clear_database():
    """Clear the existing Chroma database."""
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    print("🧹 Chroma database cleared.")
