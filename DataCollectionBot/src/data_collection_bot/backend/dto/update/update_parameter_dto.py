from typing import Optional

from pydantic import BaseModel


class UpdateParameterDTO(BaseModel):
    name: Optional[str] = None
    rule: Optional[str] = None
    norm_row: Optional[str] = None
    choice: Optional[str] = None
    instruction: Optional[str] = None
