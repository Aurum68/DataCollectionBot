from typing import Type
import logging

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import DeclarativeBase


class DBManager:
    def __init__(self, engine: AsyncEngine, base: Type[DeclarativeBase]):
        self.engine = engine
        self.Base = base
        self.logger = logging.getLogger(self.__class__.__name__)


    async def db_init(self):
        self.logger.info("Initializing database")
        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.create_all)
        self.logger.info("Database initialized")


    async def db_dispose(self):
        self.logger.info("Dispose of database")
        await self.engine.dispose()
        self.logger.info("Database disposed")


    async def db_clear(self):
        self.logger.info("Clearing database")
        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.drop_all)
        self.logger.info("Database cleared")