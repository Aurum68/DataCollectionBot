from pydantic import BaseModel

from src.data_collection_bot.backend.utils.roles_enum import Roles


class CreateRoleDTO(BaseModel):
    name: str