from typing import Optional, List

from pydantic import BaseModel

class CreateParameterDTO(BaseModel):
    name: str
    rule: str
    norm_row: str
    choice: Optional[str] = None
    instruction: Optional[str] = None
