from logging import Logger
from typing import TypeVar, Generic, Type

from pydantic import BaseModel

from src.data_collection_bot.backend.models import IdentifiedBase
from src.data_collection_bot.backend.repository import BaseRepository

TRepo = TypeVar('TRepo', bound=BaseRepository)# mkinit TRepo:noexport

TModel = TypeVar('TModel', bound=IdentifiedBase)# mkinit TModel:noexport

T_Cr_DTO = TypeVar('T_Cr_DTO', bound=BaseModel)# mkinit T_Cr_DTO:noexport



class CreateMixin(Generic[TModel, TRepo, T_Cr_DTO]):
    repository: TRepo
    model: Type[TModel]
    logger: Logger


    async def create(self, item: T_Cr_DTO) -> TModel | None:
        if self.model is None:
            self.logger.error("model not implemented", exc_info=True)
            raise NotImplementedError("model not implemented")
        try:
            new_item: TModel = self.model(**item.model_dump())
            return await self.repository.save(new_item)
        except Exception as e:
            self.logger.error(e, exc_info=True)
            return None
# mkinit CreateMixin:inherit