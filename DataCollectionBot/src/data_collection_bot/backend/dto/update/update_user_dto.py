from typing import Optional

from pydantic import BaseModel

class UpdateUserDTO(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role_id: Optional[int] = None