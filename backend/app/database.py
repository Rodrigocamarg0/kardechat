"""Conexão com MongoDB."""

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient | None = None


async def connect_db() -> None:
    global client
    client = AsyncIOMotorClient(settings.mongo_uri)


async def close_db() -> None:
    global client
    if client:
        client.close()


def get_db():
    return client[settings.db_name]
