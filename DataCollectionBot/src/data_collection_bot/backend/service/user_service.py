from typing import Any

from src.data_collection_bot.backend.dto.create.request.create_user_dto import CreateUserDTO
from src.data_collection_bot.backend.dto.update.update_user_dto import UpdateUserDTO
from src.data_collection_bot.backend.models.users.user import User
from src.data_collection_bot.backend.repository.user_repository import UserRepository
from src.data_collection_bot.backend.service.base_service_updating import BaseServiceUpdating
from src.data_collection_bot.backend.utils.security import hash_password


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


    def _prepare_create_data(self, item: CreateUserDTO) -> dict[str, Any]:
        if item.telegram_id is None and (item.email is None or item.password is None):
            raise ValueError("Отсутствуют идентификаторы. Для бота должен быть telegram_id; для внешних клиентов - email + password")

        data = item.model_dump(exclude={'password'}, exclude_none=True)

        if item.telegram_id is not None:
            return data

        password = item.password
        if password is None or len(password) == 0:
            raise ValueError("Password is required")

        data['password'] = hash_password(password)

        return data
