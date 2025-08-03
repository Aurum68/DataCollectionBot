from src.data_collection_bot.backend.dto import CreateUserDTO, UpdateUserDTO
from src.data_collection_bot.backend.models import User
from src.data_collection_bot.backend.repository import UserRepository
from src.data_collection_bot.backend.service import BaseServiceUpdating


class UserService(BaseServiceUpdating[
                    User,
                    UserRepository,
                    CreateUserDTO,
                    UpdateUserDTO
                ]):

    def __init__(self, repository: UserRepository):
        super().__init__(User, repository)


    async def get_user_by_telegram_id(self, telegram_id: int) -> User:
        return await self.repository.get_user_by_telegram_id(telegram_id)


    async def get_user_by_username(self, username: str) -> User:
        return await self.repository.get_user_by_username(username)


    async def get_user_by_invite_id(self, invite_id: int) -> User:
        return await self.repository.get_user_by_invite_id(invite_id)