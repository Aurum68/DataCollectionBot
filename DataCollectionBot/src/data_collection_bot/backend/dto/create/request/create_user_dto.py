from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class CreateUserDTO(BaseModel):
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None