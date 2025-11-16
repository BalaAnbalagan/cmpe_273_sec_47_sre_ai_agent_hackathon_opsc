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
from fastapi.responses import ORJSONResponse
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware
import sys

from api.core.config import settings
from api.services.redis_client import close_redis
from api.services.mongo_client import close_mongo
from api.routers.sre import router as sre_router

origins = [
    "http://localhost:3000",   # Next.js dev
    "http://127.0.0.1:3000",
    # add prod frontend URL later (e.g. https://your-app.com)
]

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
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
