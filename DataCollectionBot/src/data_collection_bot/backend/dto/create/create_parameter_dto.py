from typing import Optional, List

from pydantic import BaseModel

class CreateParameterDTO(BaseModel):
    name: str
    rule: str
    norm_raw: str
    choice: Optional[str] = None
