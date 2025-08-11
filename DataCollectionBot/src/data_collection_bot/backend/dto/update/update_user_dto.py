from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class UpdateUserDTO(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birthday: Optional[datetime] = None
    role_id: Optional[int] = None