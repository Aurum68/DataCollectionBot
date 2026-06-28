from fastapi import APIRouter, Depends, HTTPException

from src.data_collection_bot.api.deps import Services
from src.data_collection_bot.backend.dto.create.request.create_user_dto import CreateUserDTO as RequestCreateUserDto
from src.data_collection_bot.backend.dto.create.response.create_user_dto import CreateUserDTO as ResponseCreateUserDto

api_router = APIRouter()

@api_router.post('/register', response_model=ResponseCreateUserDto)
async def register(
        user: RequestCreateUserDto,
        services: Services = Depends(Services),
        
):
    if user.email is None and user.password is None:
        raise HTTPException(status_code=401)

    user_service = services.user_service

    return await user_service.create(user)