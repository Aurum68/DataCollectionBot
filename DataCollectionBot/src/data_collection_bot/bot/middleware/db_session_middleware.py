from typing import Callable, Dict, Any, Awaitable

import sqlalchemy
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.data_collection_bot import UserRepository, RoleRepository, ParameterRepository, RecordRepository, \
    InviteRepository, UserService, RoleService, RecordService, InviteService, ParameterService


class DBSessionMiddleware(BaseMiddleware):
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self.sessionmaker = sessionmaker


    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]
                       ) -> Any:
        async with self.sessionmaker() as session:
            user_repo: UserRepository = UserRepository(session)
            role_repo: RoleRepository = RoleRepository(session)
            parameter_repo: ParameterRepository = ParameterRepository(session)
            record_repo: RecordRepository = RecordRepository(session)
            invite_repo: InviteRepository = InviteRepository(session)

            data['user_service'] = UserService(user_repo)
            data['role_service'] = RoleService(role_repo, parameter_repo)
            data['parameter_service'] = ParameterService(parameter_repo)
            data['record_service'] = RecordService(record_repo)
            data['invite_service'] = InviteService(invite_repo)
            data['db_session'] = session

            return await handler(event, data)
