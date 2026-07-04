from fastapi import FastAPI
from pydantic import BaseModel
from .orchestrator import run_pipeline

app = FastAPI(title="RAG Security API")

class ChatRequest(BaseModel):
    query: str
    user_departments: list[str] = ["all"]

@app.post("/chat")
def chat(payload: ChatRequest):
    return run_pipeline(payload.query, payload.user_departments)

@app.get("/health")
def health():
    return {"status": "ok"}