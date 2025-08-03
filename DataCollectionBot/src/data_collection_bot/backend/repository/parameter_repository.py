from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.data_collection_bot.backend.models import Parameter
from src.data_collection_bot.backend.repository import BaseRepository


class ParameterRepository(BaseRepository[Parameter]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Parameter)


    async def get_by_id(self, item_id: int) -> Parameter:
        result = await self.session.execute(
            select(Parameter)
            .options(selectinload(Parameter.roles))
            .where(Parameter.id == item_id)
        )
        return result.scalars().first()


    async def get_by_name(self, name: str) -> Parameter:
        result = await self.session.execute(
            select(Parameter)
            .options(selectinload(Parameter.roles))
            .where(Parameter.name == name)
        )
        return result.scalars().first()