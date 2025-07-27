import certifi
from pymongo import AsyncMongoClient
from core.config import settings
    
_MONGO: AsyncMongoClient | None = None


async def get_client() -> AsyncMongoClient:
    """Return a singleton AsyncMongoClient."""
    global _MONGO
    if _MONGO is None:
        _MONGO = AsyncMongoClient(
            settings.MONGO_URI,
            tz_aware=True,    
            tlsCAFile=certifi.where()           
        )
    return _MONGO


async def get_db():
    client = await get_client()
    return client[settings.DATABASE_NAME]


async def close_client() -> None:
    """Close the global connection pool on shutdown."""
    if _MONGO is not None:
        await _MONGO.close()