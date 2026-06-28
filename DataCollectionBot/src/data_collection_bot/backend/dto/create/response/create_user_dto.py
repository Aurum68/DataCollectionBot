from pydantic import BaseModel

class CreateUserDTO(BaseModel):
    id: int