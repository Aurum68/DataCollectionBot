from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.data_collection_bot.backend.models import User
from src.data_collection_bot.backend.repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)


    async def get_all(self):
        result = await self.session.execute(
            select(self.model)
            .options(
                selectinload(self.model.role)
            )
        )
        return result.scalars().all()


    async def get_by_id(self, item_id: int) -> User:
        result = await self.session.execute(
            select(self.model)
                .options(
                    selectinload(User.role)
                )
            .where(self.model.id == item_id))
        return result.scalars().first()


    async def get_user_by_telegram_id(self, telegram_id: int) -> User:
         result = await self.session.execute(
             select(self.model)
             .options(
                 selectinload(User.role)
             )
             .where(self.model.telegram_id == telegram_id))
         return result.scalars().first()


    async def get_user_by_username(self, username: str) -> User:
        if username is None:
            self.logger.warning("Username is none")
            raise ValueError("Username is None")
        result = await self.session.execute(
            select(self.model)
            .options(
                selectinload(User.role)
            )
            .where(self.model.username == username))
        return result.scalars().first()


    async def get_user_by_invite_id(self, invite_id: int) -> User:
        result = await self.session.execute(
            select(self.model)
            .options(
                selectinload(User.role)
            )
            .where(self.model.invite_id == invite_id))
        return result.scalars().first()