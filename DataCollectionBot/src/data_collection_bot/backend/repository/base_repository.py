import logging
from typing import TypeVar, Generic

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data_collection_bot.backend.models.identified_base import IdentifiedBase

T = TypeVar('T', bound=IdentifiedBase)


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)


    async def get_all(self) -> list[T]:
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())


    async def get_by_id(self, item_id: int) -> T:
        result = await self.session.execute(select(self.model).where(self.model.id == item_id))
        return result.scalars().first()


    async def save(self, item: T) -> T:
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item


    async def delete(self, item: T) -> None:
        await self.session.delete(item)
        await self.session.flush()