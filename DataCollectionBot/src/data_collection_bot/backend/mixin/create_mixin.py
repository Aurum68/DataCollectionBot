from logging import Logger
from typing import TypeVar, Generic, Type, Any

from pydantic import BaseModel

from src.data_collection_bot.backend.models.identified_base import IdentifiedBase
from src.data_collection_bot.backend.repository.base_repository import BaseRepository

TRepo = TypeVar('TRepo', bound=BaseRepository)# mkinit TRepo:noexport

TModel = TypeVar('TModel', bound=IdentifiedBase)# mkinit TModel:noexport

T_Cr_DTO = TypeVar('T_Cr_DTO', bound=BaseModel)# mkinit T_Cr_DTO:noexport



class CreateMixin(Generic[TModel, TRepo, T_Cr_DTO]):
    repository: TRepo
    model: Type[TModel]
    logger: Logger


    def _prepare_create_data(self, item: T_Cr_DTO) -> dict[str, Any]:
        return item.model_dump()


    async def create(self, item: T_Cr_DTO) -> TModel | None:
        if self.model is None:
            self.logger.error("model not implemented", exc_info=True)
            raise NotImplementedError("model not implemented")
        try:
            data = self._prepare_create_data(item)
            new_item: TModel = self.model(**data)
            return await self.repository.save(new_item)
        except Exception as e:
            self.logger.error(e, exc_info=True)
            return None
# mkinit CreateMixin:inherit