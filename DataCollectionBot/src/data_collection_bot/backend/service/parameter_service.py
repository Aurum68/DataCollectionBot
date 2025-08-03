from typing import Type

from src.data_collection_bot.backend.dto import CreateParameterDTO, UpdateParameterDTO
from src.data_collection_bot.backend.models import Parameter
from src.data_collection_bot.backend.repository import ParameterRepository
from src.data_collection_bot.backend.service import BaseServiceUpdating


class ParameterService(BaseServiceUpdating[
                           Parameter,
                           ParameterRepository,
                           CreateParameterDTO,
                           UpdateParameterDTO
                       ]):
    model = Parameter

    def __init__(self, repository: ParameterRepository):
        super().__init__(Parameter, repository)


    async def get_parameter_by_name(self, name: str) -> Parameter:
        return await self.repository.get_by_name(name)