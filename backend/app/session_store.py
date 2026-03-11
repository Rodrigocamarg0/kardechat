"""Session storage com MongoDB para o agente Kardechat.

O AsyncMongoDb é sensível ao event loop — criá-lo no nível de módulo
pode causar problemas quando o uvicorn troca de loop na inicialização.
Solução: factory function que cria a instância sob demanda, sempre
dentro do event loop correto. O Motor detecta automaticamente o loop
atual quando AsyncIOMotorClient é instanciado dentro de uma coroutine.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from agno.db.mongo.async_mongo import AsyncMongoDb

from app.config import settings


def make_agent_storage() -> AsyncMongoDb:
    """
    Cria uma nova instância de AsyncMongoDb com um Motor client fresco.
    Deve ser chamada dentro de uma coroutine (event loop ativo).
    """
    motor_client = AsyncIOMotorClient(settings.mongo_uri)
    return AsyncMongoDb(
        db_client=motor_client,
        db_name=settings.db_name,
        session_collection="agno_sessions",
    )
