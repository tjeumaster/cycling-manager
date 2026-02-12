from typing import AsyncGenerator
from asyncpg import Pool, create_pool, Connection
from loguru import logger
from config import settings

class Database:
    def __init__(self, dsn: str):
        self.pool: Pool | None = None
        self.dsn: str = dsn
        
    async def connect(self):
        try:
            self.pool = await create_pool(self.dsn)
            logger.info("Database connection pool created successfully.")
            
        except Exception as e:
            logger.error(f"Error connecting to the database: {e}")
            raise e
        
    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed successfully.")
            
            
    async def get_connection(self) -> AsyncGenerator[Connection, None]:
        if not self.pool:
            raise Exception("Database connection pool is not initialized.")
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                yield conn
                     
dsn = settings.PGS_DSN
db = Database(dsn)