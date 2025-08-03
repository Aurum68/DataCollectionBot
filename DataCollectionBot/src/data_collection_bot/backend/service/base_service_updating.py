import logging
from typing import TypeVar, Type, Generic

from pydantic import BaseModel

from src.data_collection_bot.backend.mixin import GetMixin, CreateMixin, UpdateMixin, DeleteMixin
from src.data_collection_bot.backend.models import IdentifiedBase
from src.data_collection_bot.backend.repository import BaseRepository

TR = TypeVar('TR', bound=BaseRepository)
TM = TypeVar('TM', bound=IdentifiedBase)
T_C_DTO = TypeVar('T_C_DTO', bound=BaseModel)
T_U_DTO = TypeVar('T_U_DTO', bound=BaseModel)


class BaseServiceUpdating(
    GetMixin[TM, TR],
    CreateMixin[TM, TR, T_C_DTO],
    UpdateMixin[TM, TR, T_U_DTO],
    DeleteMixin[TM, TR],
    Generic[TM, TR, T_C_DTO, T_U_DTO]
):
    def __init__(self, model: Type[TM], repository: TR):
        self.repository = repository
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)









