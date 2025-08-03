from logging import Logger
from typing import TypeVar, Generic, Type

from pydantic import BaseModel

from src.data_collection_bot.backend.models import IdentifiedBase
from src.data_collection_bot.backend.repository import BaseRepository

TRepo = TypeVar('TRepo', bound=BaseRepository)
# mkinit TRepo:noexport
TModel = TypeVar('TModel', bound=IdentifiedBase)
# mkinit TModel:noexport
T_Up_DTO = TypeVar('T_Up_DTO', bound=BaseModel)
# mkinit T_Up_DTO:noexport



class UpdateMixin(Generic[TModel, TRepo, T_Up_DTO]):
    repository: TRepo
    model: Type[TModel]
    logger: Logger

    async def update(self, item_id: int, item: T_Up_DTO) -> TModel | None:
        if self.model is None:
            raise NotImplementedError("model not implemented")

        item_to_update: TModel = await self.repository.get_by_id(item_id)
        if item_to_update is None:
            self.logger.error(f"item {item_id} not found", exc_info=True)
            raise Exception(f"{self.model.__name__} with id {item_id} not found")

        update_data = item.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if key == "id":
                continue
            setattr(item_to_update, key, value)

        return await self.repository.save(item_to_update)
# mkinit UpdateMixin:inherit
