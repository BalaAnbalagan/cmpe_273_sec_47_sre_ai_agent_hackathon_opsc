from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
from api.models.schemas import (
    TelemetryEvent, UserMetric, ImageSearchRequest, TopIPsQuery, ImageEmbedding,
    ImageDescriptionRequest, NaturalLanguageSearchRequest, ChatWithImagesRequest,
    SafetyAnalysisRequest
)
from api.services import telemetry_service, user_service, image_service, log_service, cohere_service
from api.core.keyvault import is_key_vault_available

router = APIRouter(prefix="/sre", tags=["sre"])


# ============================================================================
# DEPLOYMENT & SYSTEM STATUS ENDPOINTS
# ============================================================================

@router.get("/deployment-version")
async def get_deployment_version(request: Request):
    """
    Get current deployment version and metadata.

    Returns deployment information including version, region, and zone.
    """
    settings = request.app.state.settings
    return {
        "version": settings.DEPLOYMENT_VERSION,
        "region": settings.REGION_NAME,
        "active_zone": settings.ACTIVE_REGION,
        "environment": settings.ENVIRONMENT
    }


@router.get("/status")
async def get_system_status(request: Request):
    """
    Get comprehensive system status including Azure service connectivity.

    Returns health status of:
    - Application deployment
    - Redis cache
    - Cosmos DB (MongoDB)
    - Cohere AI
    - Azure Key Vault
    - MQTT broker
    - RabbitMQ broker
    """
    settings = request.app.state.settings

    # Check Key Vault availability
    kv_available = is_key_vault_available()

    # Check Redis connectivity
    redis_status = "unknown"
    try:
        from api.services.redis_client import get_redis
        redis = await get_redis()
        await redis.ping()
        redis_status = "✅ connected"
    except Exception as e:
        redis_status = f"❌ error: {str(e)[:50]}"

    # Check MongoDB connectivity
    mongo_status = "unknown"
    try:
        from api.services.mongo_client import get_db
        db = get_db()
        await db.command("ping")
        mongo_status = "✅ connected"
    except Exception as e:
        mongo_status = f"❌ error: {str(e)[:50]}"

    return {
        "deployment": {
            "status": "running",
            "version": settings.DEPLOYMENT_VERSION,
            "region": settings.REGION_NAME,
            "zone": settings.ACTIVE_REGION,
            "environment": settings.ENVIRONMENT
        },
        "azure_services": {
            "key_vault": "✅ available" if kv_available else "❌ unavailable",
            "redis_cache": redis_status,
            "cosmos_db": mongo_status,
            "cohere_api": "✅ configured" if settings.COHERE_API_KEY else "❌ not configured",
            "mqtt_broker": f"{settings.MQTT_HOST}:{settings.MQTT_PORT}",
            "rabbitmq_broker": f"{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}"
        },
        "configuration": {
            "use_key_vault": settings.USE_KEY_VAULT,
            "storage_account": settings.AZURE_STORAGE_ACCOUNT,
            "blob_container": settings.BLOB_CONTAINER_IMAGES
        }
    }


# ============================================================================
# DEVICE TELEMETRY ENDPOINTS
# ============================================================================

@router.post("/devices/ingest")
async def ingest_device(evt: TelemetryEvent) -> Dict[str, Any]:
    await telemetry_service.ingest_telemetry(evt)
    return {"ok": True}

@router.get("/active-devices")
async def get_active_devices(site_id: str | None = None, limit: int = 20):
    return await telemetry_service.get_active_devices(site_id=site_id, limit=limit)


# ============================================================================
# USER METRICS ENDPOINTS
# ============================================================================

@router.post("/users/ingest")
async def ingest_user(m: UserMetric):
    await user_service.ingest_user_metric(m)
    return {"ok": True}

@router.get("/active-users")
async def active_users(site_id: str, limit: int = 50):
    return await user_service.get_active_users(site_id, limit)


# ============================================================================
# IMAGE EMBEDDING ENDPOINTS (Basic)
# ============================================================================

@router.post("/images/upsert")
async def upsert_image_embedding(body: ImageEmbedding):
    await image_service.upsert_embedding(body)
    return {"ok": True}

@router.post("/images/search")
async def search_images(body: ImageSearchRequest):
    results = await image_service.search_similar(body.query_embedding, body.top_k)
    return {"results": results}


# ============================================================================
# LOG ANALYSIS ENDPOINTS
# ============================================================================

@router.post("/logs/ingest-line")
async def ingest_log_line(line: str):
    await log_service.ingest_log_line(line)
    return {"ok": True}

@router.post("/logs/top-ips")
async def top_ips(q: TopIPsQuery):
    return {"status": q.status_code, "top": await log_service.top_error_ips(q.status_code, q.top_n)}


# ============================================================================
# COHERE AI-POWERED IMAGE INTELLIGENCE ENDPOINTS
# ============================================================================

@router.post("/images/embed-description")
async def embed_image_description(req: ImageDescriptionRequest):
    """
    Generate and store embedding for an image description using Cohere.
    Use this after uploading images to Azure Blob Storage.
    """
    if not cohere_service.is_available():
        raise HTTPException(status_code=503, detail="Cohere service not configured")

    # Generate embedding from description and metadata
    embedding = await cohere_service.generate_image_description_embedding(
        req.description,
        req.metadata
    )

    # Store in database
    await image_service.upsert_embedding({
        "image_id": req.image_id,
        "embedding": embedding,
        "metadata": req.metadata or {}
    })

    return {"ok": True, "image_id": req.image_id, "embedding_dims": len(embedding)}


@router.post("/images/search-nl")
async def natural_language_search(req: NaturalLanguageSearchRequest):
    """
    Search images using natural language queries.
    Examples:
    - "Show turbine sites with workers without hard hats"
    - "Find sites with high safety compliance"
    - "Images with electrical equipment issues"
    """
    if not cohere_service.is_available():
        raise HTTPException(status_code=503, detail="Cohere service not configured")

    # Generate query embedding
    query_embedding = await cohere_service.generate_query_embedding(req.query)

    # Search similar images
    results = await image_service.search_similar(query_embedding, req.top_k)

    return {
        "query": req.query,
        "results": results,
        "count": len(results)
    }


@router.post("/images/chat")
async def chat_with_images(req: ChatWithImagesRequest):
    """
    RAG-based chat about site images.
    Ask questions and get AI-powered answers with citations.

    Examples:
    - "What safety violations can you identify?"
    - "Which sites have the most workers?"
    - "Describe the equipment condition at ND-RAVEN"
    """
    if not cohere_service.is_available():
        raise HTTPException(status_code=503, detail="Cohere service not configured")

    # If specific image IDs provided, fetch them
    if req.image_ids:
        from api.services.mongo_client import get_db
        db = get_db()
        cursor = db["image_embeddings"].find(
            {"image_id": {"$in": req.image_ids}},
            {"_id": 0, "image_id": 1, "metadata": 1}
        )
        context_docs = [doc async for doc in cursor]
    else:
        # Otherwise, search for relevant images first
        query_embedding = await cohere_service.generate_query_embedding(req.query)
        context_docs = await image_service.search_similar(query_embedding, req.max_results)

    # Generate RAG response
    response = await cohere_service.chat_with_context(req.query, context_docs)

    return {
        "query": req.query,
        "answer": response["answer"],
        "citations": response["citations"],
        "context_images": len(context_docs)
    }


@router.post("/images/safety-analysis")
async def analyze_safety(req: SafetyAnalysisRequest):
    """
    AI-powered safety compliance analysis for site images.
    Identifies violations, risks, and provides recommendations.
    """
    if not cohere_service.is_available():
        raise HTTPException(status_code=503, detail="Cohere service not configured")

    # Fetch image descriptions
    from api.services.mongo_client import get_db
    db = get_db()

    query = {}
    if req.site_id:
        query["metadata.site_id"] = req.site_id

    cursor = db["image_embeddings"].find(
        query,
        {"_id": 0, "image_id": 1, "metadata": 1}
    ).limit(req.max_images)

    images = [doc async for doc in cursor]

    if not images:
        return {"error": "No images found", "site_id": req.site_id}

    # Extract descriptions for analysis
    descriptions = [
        f"{img.get('metadata', {}).get('description', img['image_id'])} (Site: {img.get('metadata', {}).get('site_id', 'N/A')})"
        for img in images
    ]

    # Run AI safety analysis
    analysis = await cohere_service.analyze_safety_compliance(descriptions)

    return {
        "site_id": req.site_id or "all",
        "images_analyzed": len(images),
        "analysis": analysis["analysis"],
        "image_ids": [img["image_id"] for img in images]
    }


@router.get("/images/cohere-status")
async def cohere_status():
    """Check if Cohere AI service is available and configured"""
    return {
        "available": cohere_service.is_available(),
        "embed_model": cohere_service.COHERE_MODEL_EMBED,
        "chat_model": cohere_service.COHERE_MODEL_CHAT
    }
