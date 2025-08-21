from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class CreateUserDTO(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birthday: Optional[datetime] = None
    pseudonym: Optional[str] = None
    role_id: int
    invite_id: Optional[int] = None
