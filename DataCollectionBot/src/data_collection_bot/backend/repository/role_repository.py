from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.data_collection_bot.backend.models import Role
from src.data_collection_bot.backend.repository import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Role)


    async def get_by_id(self, item_id: int) -> Role:
        result = await self.session.execute(
            select(Role)
            .options(
                selectinload(Role.parameters),
                selectinload(Role.users)
            )
            .where(Role.id == item_id))
        return result.scalars().first()


    async def get_role_by_name(self, name: str) -> Role:
        result = await self.session.execute(
            select(self.model)
            .options(
                selectinload(Role.parameters),
            )
            .where(self.model.name == name))
        return result.scalars().first()