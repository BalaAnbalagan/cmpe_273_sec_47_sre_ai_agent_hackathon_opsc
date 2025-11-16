"""
FastAPI application entry point for SRE Hackathon backend.
Handles:
- Azure Key Vault (via UMI)
- Redis
- MongoDB
- Cohere
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from loguru import logger
import sys

from api.core.config import settings
from api.services.redis_client import close_redis
from api.services.mongo_client import close_mongo
from api.routers.sre import router as sre_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting SRE Hackathon API")

    try:
        ok = await settings.load_from_keyvault()
        logger.info(f"Key Vault Loaded: {ok}")
    except Exception as e:
        logger.error(f"Key Vault failed: {e}")

    app.state.settings = settings
    yield

    await close_redis()
    await close_mongo()
    logger.info("🛑 Shutdown complete.")


app = FastAPI(
    title="SRE Hackathon API",
    version=settings.DEPLOYMENT_VERSION,
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo - change in production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sre_router)


@app.get("/")
async def root():
    return {"status": "running", "version": settings.DEPLOYMENT_VERSION}


@app.get("/health")
async def health():
    return {"status": "healthy"}
