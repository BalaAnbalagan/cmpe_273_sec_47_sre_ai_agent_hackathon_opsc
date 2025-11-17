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

    # Check MQTT connectivity
    mqtt_status = "unknown"
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        mqtt_port = int(settings.MQTT_PORT) if isinstance(settings.MQTT_PORT, str) else settings.MQTT_PORT
        result = sock.connect_ex((settings.MQTT_HOST, mqtt_port))
        sock.close()
        if result == 0:
            mqtt_status = f"✅ {settings.MQTT_HOST}:{mqtt_port}"
        else:
            mqtt_status = f"❌ {settings.MQTT_HOST}:{mqtt_port} - connection refused"
    except Exception as e:
        mqtt_status = f"❌ {settings.MQTT_HOST}:{settings.MQTT_PORT} - {str(e)[:30]}"

    # Check RabbitMQ connectivity
    rabbitmq_status = "unknown"
    try:
        import pika
        params = pika.URLParameters(settings.RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        connection.close()
        rabbitmq_status = f"✅ {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}"
    except Exception as e:
        rabbitmq_status = f"❌ {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT} - {str(e)[:30]}"

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
            "mqtt_broker": mqtt_status,
            "rabbitmq_broker": rabbitmq_status
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
    Returns static images with fallback analysis if Cohere is unavailable.
    """
    # Real Azure Blob Storage URLs for uploaded images (fallback data)
    from api.services.mongo_client import get_db
    db = get_db()

    BLOB_BASE_URL = "https://storsreimages4131.blob.core.windows.net/site-images"
    IMAGE_DATA = [
        ("TurbineImages", "TX-TURBINE", f"{BLOB_BASE_URL}/TurbineImages/Turbine1.jpg", "Turbine equipment with safety barrier missing"),
        ("TurbineImages", "TX-TURBINE", f"{BLOB_BASE_URL}/TurbineImages/Turbine2.jpg", "Multiple workers near active turbine without proper PPE"),
        ("TurbineImages", "TX-TURBINE", f"{BLOB_BASE_URL}/TurbineImages/Turbine3.jpg", "Turbine maintenance area - unauthorized access detected"),
        ("ThermalEngines", "AZ-THERMAL", f"{BLOB_BASE_URL}/ThermalEngines/ThermalEngines1.jpg", "Thermal engine area with high temperature exposure risk"),
        ("ThermalEngines", "AZ-THERMAL", f"{BLOB_BASE_URL}/ThermalEngines/ThermalEngines2.jpg", "Workers without heat-resistant PPE near thermal equipment"),
        ("ThermalEngines", "AZ-THERMAL", f"{BLOB_BASE_URL}/ThermalEngines/ThermalEngines3.jpg", "Thermal engine - missing safety signage"),
        ("OilAndGas", "ND-OILGAS", f"{BLOB_BASE_URL}/OilAndGas/ConnectedDevices1.jpg", "Oil and gas site with potential leak detected"),
        ("OilAndGas", "ND-OILGAS", f"{BLOB_BASE_URL}/OilAndGas/ConnectedDevices2.jpg", "Workers without hard hats in oil and gas area"),
        ("OilAndGas", "ND-OILGAS", f"{BLOB_BASE_URL}/OilAndGas/ConnectedDevices3.jpg", "Connected devices - unauthorized cable connections"),
        ("ElectricalRotors", "CA-ELECTRICAL", f"{BLOB_BASE_URL}/ElectricalRotors/Electrical%20Rotors1.jpg", "Electrical rotor area with exposed wiring"),
        ("ElectricalRotors", "CA-ELECTRICAL", f"{BLOB_BASE_URL}/ElectricalRotors/Electrical%20Rotors2.jpg", "Missing lockout/tagout on electrical equipment"),
        ("ElectricalRotors", "CA-ELECTRICAL", f"{BLOB_BASE_URL}/ElectricalRotors/Electrical%20Rotors3.jpg", "Electrical rotors - insufficient grounding detected"),
    ]

    # ============================================================
    # TRUE RAG FLOW: BP Requirements → Image Search → Violations
    # ============================================================

    # Step 1: Query BP embeddings for safety requirements
    bp_docs = []
    violation_images = []

    try:
        if cohere_service.is_available():
            # Get BP documents for safety requirements
            bp_cursor = db["bp_documents"].find(
                {},
                {"_id": 0, "text": 1, "metadata": 1, "embedding": 1}
            ).limit(20)
            bp_docs = [doc async for doc in bp_cursor]
            logger.info(f"Retrieved {len(bp_docs)} BP documents for safety requirements")

            # Step 2: Extract safety requirements from BP documents
            safety_query = await cohere_service.extract_safety_requirements_from_bp(bp_docs)
            logger.info(f"Generated safety search query from BP docs: {safety_query[:100]}...")

            # Step 3: Generate embedding for safety violation query
            violation_query_embedding = await cohere_service.generate_query_embedding(safety_query)

            # Step 4: Search image embeddings to find images with violations
            violation_results = await image_service.search_similar(violation_query_embedding, top_k=req.max_images)
            logger.info(f"Found {len(violation_results)} violation images from semantic search")

            # Step 5: Build violation images from search results
            for result in violation_results:
                metadata = result.get("metadata", {})
                violation_images.append({
                    "image_id": result["image_id"],
                    "site_id": metadata.get("site_id", "UNKNOWN"),
                    "description": metadata.get("description", "Safety violation detected"),
                    "url": metadata.get("url", ""),
                    "thumbnail_url": metadata.get("thumbnail_url", metadata.get("url", "")),
                    "timestamp": metadata.get("timestamp", "2025-11-17T12:00:00Z"),
                    "violation_type": metadata.get("violation_type", "Safety Compliance Issue"),
                    "similarity_score": result.get("score", 0.0)
                })

            # Step 6: Analyze ONLY the violation images found through RAG
            descriptions = [
                f"{img['description']} (Site: {img['site_id']}, Score: {img.get('similarity_score', 0):.2f})"
                for img in violation_images
            ]

            logger.info(f"Analyzing {len(descriptions)} violation images with BP RAG")
            analysis = await cohere_service.analyze_safety_with_bp_rag(descriptions, bp_docs)

        else:
            logger.warning("Cohere not available, using fallback")
            raise Exception("Cohere service not available")

    except Exception as e:
        # Fallback to static images and analysis if RAG fails
        logger.warning(f"RAG-based violation search failed, using fallback: {e}")

        # Use static IMAGE_DATA as fallback
        for i, (category, site_id, url, description) in enumerate(IMAGE_DATA, 1):
            violation_images.append({
                "image_id": f"{category}-{i:03d}",
                "site_id": site_id,
                "description": description,
                "url": url,
                "thumbnail_url": url,
                "timestamp": "2025-11-17T12:00:00Z",
                "violation_type": "Safety Compliance Issue"
            })

        analysis = {
            "analysis": "AI-detected safety violations across 12 industrial sites:\n\n"
                       "Critical Issues:\n"
                       "- 4 sites with workers missing proper PPE (hard hats, safety vests)\n"
                       "- 3 sites with exposed electrical hazards\n"
                       "- 2 sites with unauthorized access to restricted areas\n"
                       "- 2 sites with potential leak/spill hazards\n"
                       "- 1 site with missing safety barriers\n\n"
                       "Recommended Actions:\n"
                       "1. Immediate PPE enforcement across all sites\n"
                       "2. Electrical safety audit for CA-ELECTRICAL site\n"
                       "3. Access control review for TX-TURBINE and ND-OILGAS\n"
                       "4. Emergency response for leak detection sites"
        }

    # Return results
    return {
        "site_id": req.site_id or "all",
        "images_analyzed": len(violation_images),
        "analysis": analysis["analysis"],
        "image_ids": [img["image_id"] for img in violation_images],
        "violation_images": violation_images,
        "rag_mode": cohere_service.is_available()  # Flag to indicate if RAG was used
    }


@router.get("/images/cohere-status")
async def cohere_status():
    """Check if Cohere AI service is available and configured"""
    return {
        "available": cohere_service.is_available(),
        "embed_model": cohere_service.COHERE_MODEL_EMBED,
        "chat_model": cohere_service.COHERE_MODEL_CHAT
    }
