import sqlalchemy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.data_collection_bot.backend.models.users.user import User
from src.data_collection_bot.backend.repository.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)


    async def get_by_id(self, item_id: int) -> User:
        result = await self.session.execute(
            select(self.model)
            .where(self.model.id == item_id))
        return result.scalars().first()


    async def get_user_by_telegram_id(self, telegram_id: int) -> User:
         result = await self.session.execute(
             select(self.model)
             .where(self.model.telegram_id == telegram_id))
         return result.scalars().first()


    async def get_user_by_username(self, username: str) -> User:
        if username is None:
            self.logger.warning("Username is none")
            raise ValueError("Username is None")
        result = await self.session.execute(
            select(self.model)
            .where(self.model.username == username))
        return result.scalars().first()


    async def get_user_by_email(self, email: str) -> User:
        if email is None:
            self.logger.warning("Email is none")
            raise ValueError("Email is None")
        result = await self.session.execute(
            select(self.model)
            .where(self.model.email == email)
        )
        return result.scalars().first()