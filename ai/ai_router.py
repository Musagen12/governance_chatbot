from fastapi import APIRouter, HTTPException
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from .get_embeddings import get_embedding_function
from .english_to_swahili import convert_to_swahili
from .swahili_to_english import convert_to_english
from pydantic import BaseModel

router = APIRouter(
    prefix="/ai",
    tags=["ai"]
)

class QueryRequest(BaseModel):
    query_text: str

CHROMA_PATH = "chroma"
PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

@router.post("/query_db")
def query_chroma_db(request: QueryRequest):
    """Query the Chroma DB for a specific question"""
    try:
        # Convert input query to English
        original_query = request.query_text
        print(f"Original query: {original_query} (Type: {type(original_query)})")
        
        # Perform translation
        translated_query = convert_to_english(text=[{'text': original_query}])
        
        # Ensure translated_query is a list and extract the first translation
        if translated_query and isinstance(translated_query, list):
            query_text = translated_query[0]  # Directly take the text as it's a string now
        else:
            query_text = ""  # Handle the case where translation fails
        print(f"Query text after translation: {query_text} (Type: {type(query_text)})")

        # Prepare the DB and embedding function
        embedding_function = get_embedding_function()
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
        
        # Search for the most relevant documents
        results = db.similarity_search_with_score(query_text, k=5)
        if not results:
            return {"response": "No relevant documents found", "sources": []}

        # Extract relevant context from search results
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        print(f"Context text: {context_text} (Type: {type(context_text)})")

        # Prepare the prompt
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)
        print(f"Prompt sent to LLM: {prompt} (Type: {type(prompt)})")

        # Get response from LLM
        model = OllamaLLM(model="mistral", base_url="https://5ff0-34-125-68-154.ngrok-free.app/")
        response_text = model.invoke(prompt)
        print(f"Response from LLM: {response_text} (Type: {type(response_text)})")

        # Translate response back to Swahili
        response = convert_to_swahili(text=[{'text': response_text}])
        
        # Ensure the response is properly formatted
        if response and isinstance(response, list):
            return {"response": response[0]}  # Return the first translated response
        else:
            return {"response": "Translation error"}

    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
