from typing import TypeVar, Generic

from src.data_collection_bot.backend.models import IdentifiedBase
from src.data_collection_bot.backend.repository import BaseRepository

TRepo = TypeVar('TRepo', bound=BaseRepository)
# mkinit TRepo:noexport
TModel = TypeVar('TModel', bound=IdentifiedBase)
# mkinit TModel:noexport


class DeleteMixin(Generic[TModel, TRepo]):
    repository: TRepo


    async def delete(self, item: TModel) -> None:
        try:
            await self.repository.delete(item)
        except Exception as e:
            self.logger.error(e, exc_info=True)
# mkinit DeleteMixin:inherit