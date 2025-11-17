from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime

class TelemetryEvent(BaseModel):
    site_id: str
    device_type: str
    device_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metrics: Optional[Dict[str, float]] = None

class UserMetric(BaseModel):
    site_id: str
    session_id: str
    user_id: str
    latency_ms: Optional[float] = None
    cpu_pct: Optional[float] = None
    mem_pct: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ImageEmbedding(BaseModel):
    image_id: str
    embedding: List[float]
    metadata: Optional[Dict[str, Any]] = None

class ImageSearchRequest(BaseModel):
    query_embedding: List[float]
    top_k: int = 5

class TopIPsQuery(BaseModel):
    status_code: str = "400"
    top_n: int = 10

class ImageDescriptionRequest(BaseModel):
    """Request to generate embedding for an image description"""
    image_id: str
    description: str
    metadata: Optional[Dict[str, Any]] = None

class NaturalLanguageSearchRequest(BaseModel):
    """Request for natural language image search"""
    query: str
    top_k: int = 5

class ChatWithImagesRequest(BaseModel):
    """Request for RAG-based chat about images"""
    query: str
    image_ids: Optional[List[str]] = None  # If None, use top search results
    max_results: int = 10

class SafetyAnalysisRequest(BaseModel):
    """Request for safety compliance analysis"""
    site_id: Optional[str] = None  # Analyze specific site or all sites
    max_images: int = 20
    custom_query: Optional[str] = None  # Custom safety query (overrides BP-based search)
