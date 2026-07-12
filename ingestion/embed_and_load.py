import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from chunker import chunk_text

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
qdrant = QdrantClient(url=os.environ["QDRANT_URL"], api_key=os.environ.get("QDRANT_API_KEY"))

COLLECTION = "company_docs"
DIM = 768  # reduced from Gemini's default 3072 to keep storage small

def ensure_collection():
    if not qdrant.collection_exists(COLLECTION):
        qdrant.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=DIM, distance=Distance.COSINE),
        )

def embed_batch(texts: list[str], task_type: str) -> list[list[float]]:
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
        config=types.EmbedContentConfig(task_type=task_type, output_dimensionality=DIM),
    )
    return [e.values for e in result.embeddings]

def ingest_file(path: str, department: str = "all", sensitivity: str = "internal"):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)
    vectors = embed_batch(chunks, task_type="RETRIEVAL_DOCUMENT")

    points = [
        PointStruct(
            id=i,
            vector=vectors[i],
            payload={"text": chunks[i], "source": path, "department": department, "sensitivity": sensitivity},
        )
        for i in range(len(chunks))
    ]
    qdrant.upsert(collection_name=COLLECTION, points=points)
    print(f"Ingested {len(chunks)} chunks from {path}")

if __name__ == "__main__":
    ensure_collection()
    ingest_file("ingestion/sample_doc.txt")