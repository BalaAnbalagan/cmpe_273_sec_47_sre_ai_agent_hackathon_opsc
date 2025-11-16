from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from backend.api.core.config import settings

_mongo_client: AsyncIOMotorClient | None = None

def get_mongo_client() -> AsyncIOMotorClient:
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(settings.MONGO_URL, uuidRepresentation="standard")
    return _mongo_client

def get_db() -> AsyncIOMotorDatabase:
    return get_mongo_client()[settings.MONGO_DB]

async def close_mongo():
    global _mongo_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
