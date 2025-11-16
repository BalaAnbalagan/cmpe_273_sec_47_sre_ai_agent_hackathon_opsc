from fastapi import APIRouter
from typing import Dict, Any
from backend.api.models.schemas import TelemetryEvent, UserMetric, ImageSearchRequest, TopIPsQuery, ImageEmbedding
from backend.api.services import telemetry_service, user_service, image_service, log_service

router = APIRouter(prefix="/sre", tags=["sre"])

@router.post("/devices/ingest")
async def ingest_device(evt: TelemetryEvent) -> Dict[str, Any]:
    await telemetry_service.ingest_telemetry(evt)
    return {"ok": True}

@router.get("/active-devices")
async def get_active_devices(site_id: str | None = None, limit: int = 20):
    return await telemetry_service.get_active_devices(site_id=site_id, limit=limit)

@router.post("/users/ingest")
async def ingest_user(m: UserMetric):
    await user_service.ingest_user_metric(m)
    return {"ok": True}

@router.get("/active-users")
async def active_users(site_id: str, limit: int = 50):
    return await user_service.get_active_users(site_id, limit)

@router.post("/images/upsert")
async def upsert_image_embedding(body: ImageEmbedding):
    await image_service.upsert_embedding(body)
    return {"ok": True}

@router.post("/images/search")
async def search_images(body: ImageSearchRequest):
    results = await image_service.search_similar(body.query_embedding, body.top_k)
    return {"results": results}

@router.post("/logs/ingest-line")
async def ingest_log_line(line: str):
    await log_service.ingest_log_line(line)
    return {"ok": True}

@router.post("/logs/top-ips")
async def top_ips(q: TopIPsQuery):
    return {"status": q.status_code, "top": await log_service.top_error_ips(q.status_code, q.top_n)}
