from pydantic import BaseModel, Field
from typing import Any, Dict, List
from datetime import datetime

class TelemetryEvent(BaseModel):
    site_id: str
    device_type: str
    device_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metrics: Dict[str, float] | None = None

class UserMetric(BaseModel):
    site_id: str
    session_id: str
    user_id: str
    latency_ms: float | None = None
    cpu_pct: float | None = None
    mem_pct: float | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ImageEmbedding(BaseModel):
    image_id: str
    embedding: List[float]
    metadata: Dict[str, Any] | None = None

class ImageSearchRequest(BaseModel):
    query_embedding: List[float]
    top_k: int = 5

class TopIPsQuery(BaseModel):
    status_code: str = "400"
    top_n: int = 10
