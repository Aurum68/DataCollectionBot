from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreateInviteDTO(BaseModel):
    token: str
    role_id: int
    expires_at: Optional[datetime] = None