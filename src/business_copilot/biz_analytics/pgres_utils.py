import os
import asyncpg  # type: ignore
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
POSTGRES_URI = os.environ.get("DATABASE")


_connection_pool = None

async def get_connection_pool():
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = await asyncpg.create_pool(dsn=POSTGRES_URI) # type: ignore
    return _connection_pool
