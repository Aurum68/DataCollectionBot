from pydantic import BaseModel

class CreateRecordDTO(BaseModel):
    user_id: int
    data: dict