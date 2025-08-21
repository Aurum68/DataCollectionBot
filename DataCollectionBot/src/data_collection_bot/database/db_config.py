from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from src.data_collection_bot.config import MYSQL_USERNAME, MYSQL_DATABASE, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT


DATABASE_URL =f'mysql+aiomysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
print(DATABASE_URL)

Engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=Engine, class_=AsyncSession, expire_on_commit=False)


def get_engine() -> AsyncEngine:
    return Engine


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True