import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchAny

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
qdrant = QdrantClient(url=os.environ["QDRANT_URL"], api_key=os.environ.get("QDRANT_API_KEY"))

COLLECTION = "company_docs"
DIM = 768

def embed_query(query: str) -> list[float]:
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=query,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY", output_dimensionality=DIM),
    )
    return result.embeddings[0].values

def retrieve(query: str, user_departments: list[str] = ["all"], top_k: int = 3):
    query_vector = embed_query(query)

    acl_filter = Filter(
        must=[FieldCondition(key="department", match=MatchAny(any=user_departments + ["all"]))]
    )

    results = qdrant.query_points(
        collection_name=COLLECTION,
        query=query_vector,
        query_filter=acl_filter,
        limit=top_k,
    ).points

    return [{"text": r.payload["text"], "score": r.score, "source": r.payload["source"]} for r in results]

if __name__ == "__main__":
    results = retrieve("How many days can I work from home?")
    for r in results:
        print(f"\n[score: {r['score']:.3f}] {r['source']}")
        print(r["text"][:200])