from typing import Optional

from pydantic import BaseModel

from src.data_collection_bot.backend.utils.roles_enum import PatientCategoryEnum


class UpdateRoleDTO(BaseModel):
    name: Optional[str] = None