from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from backend.api.services.redis_client import close_redis
from backend.api.services.mongo_client import close_mongo
from backend.api.routers.sre import router as sre_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Could warm caches/indexes here if needed
    yield
    # graceful shutdown
    await close_redis()
    await close_mongo()

app = FastAPI(title="SRE Hackathon API", default_response_class=ORJSONResponse, lifespan=lifespan)
app.include_router(sre_router)
