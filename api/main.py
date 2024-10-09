from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ai import ai_router
from ai import populate_chromadb 

app = FastAPI()

origins = [
    "https://localhost:3000",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"Message": "Welcome"}

@app.get("/test")
def api_status():
    return {"Status": "Up an running!!!!!!!"}

app.include_router(ai_router.router)
app.include_router(populate_chromadb.router)