from src.data_collection_bot.backend.dto import CreateRoleDTO, UpdateRoleDTO
from src.data_collection_bot.backend.models import Role, Parameter
from src.data_collection_bot.backend.repository import RoleRepository, ParameterRepository
from src.data_collection_bot.backend.service import BaseServiceUpdating


class RoleService(BaseServiceUpdating[
    Role,
    RoleRepository,
    CreateRoleDTO,
    UpdateRoleDTO,
                  ]):
    def __init__(self, repository: RoleRepository, parameter_repository: ParameterRepository):
        super().__init__(Role, repository)
        self.parameter_repository = parameter_repository


    async def get_role_by_name(self, name: str) -> Role:
        return await self.repository.get_role_by_name(name)


    async def add_parameter_to_role(self, role_id: int, parameter_id: int) -> Role:
        role: Role = await self.repository.get_by_id(role_id)
        parameter: Parameter = await self.parameter_repository.get_by_id(parameter_id)

        role.parameters.append(parameter)
        return await self.repository.save(role)


    async def remove_parameter_from_role(self, role_id: int, parameter_id: int) -> Role:
        role: Role = await self.repository.get_by_id(role_id)
        parameter: Parameter = await self.parameter_repository.get_by_id(parameter_id)
        role.parameters.remove(parameter)
        return await self.repository.save(role)