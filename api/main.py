from fastapi import FastAPI
from pydantic import BaseModel
from .orchestrator import run_pipeline
from .telemetry import get_stats
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RAG Security API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    user_departments: list[str] = ["all"]

@app.post("/chat")
def chat(payload: ChatRequest):
    return run_pipeline(payload.query, payload.user_departments)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/stats")
def stats():
    return get_stats()