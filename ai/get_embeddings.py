from langchain_ollama import OllamaEmbeddings

def get_embedding_function():
    embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="https://5ff0-34-125-68-154.ngrok-free.app/")
    return embeddings