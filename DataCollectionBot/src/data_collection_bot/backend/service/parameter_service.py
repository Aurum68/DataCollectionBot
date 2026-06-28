from src.data_collection_bot.backend.dto.create.request.create_parameter_dto import CreateParameterDTO
from src.data_collection_bot.backend.dto.update.update_parameter_dto import UpdateParameterDTO
from src.data_collection_bot.backend.models.parameter import Parameter
from src.data_collection_bot.backend.repository.parameter_repository import ParameterRepository
from src.data_collection_bot.backend.service.base_service_updating import BaseServiceUpdating


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