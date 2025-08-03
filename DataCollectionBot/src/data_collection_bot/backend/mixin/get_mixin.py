from typing import TypeVar, Generic

from src.data_collection_bot.backend.models import IdentifiedBase
from src.data_collection_bot.backend.repository import BaseRepository

TRepo = TypeVar('TRepo', bound=BaseRepository)
# mkinit TRepo:noexport
TModel = TypeVar('TModel', bound=IdentifiedBase)
# mkinit TModel:noexport


class GetMixin(Generic[TModel, TRepo]):
    repository: TRepo


    async def get_all(self) -> list[TModel]:
        return await self.repository.get_all()


    async def get_by_id(self, item_id: int) -> TModel:
        return await self.repository.get_by_id(item_id)
# mkinit GetMixin:inherit