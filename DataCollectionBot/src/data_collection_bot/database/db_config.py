import asyncio
import logging
import time

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from src.data_collection_bot.config import MYSQL_USERNAME, MYSQL_DATABASE, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, \
    MAX_DB_CONN_RETRIES, RETRY_DB_CONN_DELAY


DATABASE_URL =f'mysql+aiomysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'


async def create_engine_with_retry() -> AsyncEngine:
    for attempt in range(MAX_DB_CONN_RETRIES):
        try:
            engine = create_async_engine(DATABASE_URL, echo=True, pool_recycle=3600)
            await check_connection(engine)
            logging.info("Установлено соединение с MySQL")
            return engine
        except OperationalError:
            logging.warning(f"MySQL недоступен, попытка {attempt+1}/{MAX_DB_CONN_RETRIES}, "
                            f"повторю через {RETRY_DB_CONN_DELAY} сек...")
            time.sleep(RETRY_DB_CONN_DELAY)
    raise RuntimeError("Не удалось подключиться к MySQL после всех попыток!")


async def check_connection(engine: AsyncEngine):
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True