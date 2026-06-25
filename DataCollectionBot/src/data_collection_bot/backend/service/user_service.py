from src.data_collection_bot.backend.dto.create.create_user_dto import CreateUserDTO
from src.data_collection_bot.backend.dto.update.update_user_dto import UpdateUserDTO
from src.data_collection_bot.backend.models.users.user import User
from src.data_collection_bot.backend.repository.user_repository import UserRepository
from src.data_collection_bot.backend.service.base_service_updating import BaseServiceUpdating


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