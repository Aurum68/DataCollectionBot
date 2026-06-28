from typing import AsyncGenerator, AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from fastapi import Request, Depends

from src.data_collection_bot.backend.repository.user_repository import UserRepository
from src.data_collection_bot.backend.service.user_service import UserService


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    sessionmaker: async_sessionmaker[AsyncSession] = request.app.state.sessionmaker
    async with sessionmaker() as session:
        yield session


class SQLAlchemyUoW:
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self._sessionmaker = sessionmaker
        self.session: AsyncSession | None = None


    async def __aenter__(self):
        self.session = self._sessionmaker()
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                await self.session.commit()
            else:
                await self.session.rollback()
        finally:
            await self.session.close()


async def get_uow(request: Request) -> AsyncIterator[SQLAlchemyUoW]:
    async with SQLAlchemyUoW(sessionmaker=request.app.state.sessionmaker) as uow:
        yield uow


class Services:
    def __init__(self, uow: SQLAlchemyUoW = Depends(get_uow)):
        user_repository = UserRepository(uow.session)
        self.user_service = UserService(user_repository)
