from typing import Dict, Any, List
from math import sqrt
from api.services.mongo_client import get_db
from api.models.schemas import ImageEmbedding

COLL = "image_embeddings"

def _cosine(a: List[float], b: List[float]) -> float:
    s = sum(x*y for x,y in zip(a,b))
    na = sqrt(sum(x*x for x in a)) or 1.0
    nb = sqrt(sum(y*y for y in b)) or 1.0
    return s / (na * nb)

async def upsert_embedding(doc: ImageEmbedding) -> None:
    """
    Store embedding & metadata. Use image_id as unique key.
    """
    db = get_db()
    await db[COLL].update_one(
        {"image_id": doc.image_id},
        {"$set": {"embedding": doc.embedding, "metadata": doc.metadata or {}}},
        upsert=True
    )

async def search_similar(query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Simple in-memory cosine similarity: pulls all embeddings and ranks.
    Fine for hackathon scale; switch to vector index later if needed.
    """
    db = get_db()
    cursor = db[COLL].find({}, {"_id": 0, "image_id": 1, "embedding": 1, "metadata": 1})
    results: List[Dict[str, Any]] = []
    async for row in cursor:
        score = _cosine(query_embedding, row["embedding"])
        results.append({
            "image_id": row["image_id"],
            "score": score,
            "metadata": row.get("metadata", {})
        })
    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_k]
