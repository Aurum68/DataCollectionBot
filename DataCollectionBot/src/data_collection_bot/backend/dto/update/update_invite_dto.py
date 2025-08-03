from typing import Optional

from pydantic import BaseModel


class UpdateInviteDTO(BaseModel):
    is_used: Optional[bool] = False