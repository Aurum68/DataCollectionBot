from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import declarative_base, DeclarativeBase

from src.data_collection_bot.config import DATABASE_URL


Engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=Engine, class_=AsyncSession, expire_on_commit=False)


def get_engine() -> AsyncEngine:
    return Engine


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True