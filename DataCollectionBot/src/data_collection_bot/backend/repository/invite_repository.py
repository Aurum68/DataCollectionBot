from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.data_collection_bot.backend.models import Invite
from src.data_collection_bot.backend.repository import BaseRepository


class InviteRepository(BaseRepository[Invite]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Invite)


    async def get_by_id(self, item_id: int) -> Invite:
        result = await self.session.execute(
            select(Invite)
            .options(
                selectinload(Invite.user)
            )
            .where(Invite.id == item_id))
        return result.scalars().first()


    async def get_invite_by_token(self, token: str) -> Invite:
        result = await self.session.execute(select(self.model).where(self.model.token == token))
        return result.scalars().first()