from fastapi import APIRouter

from .users.router import api_router as user_router

api_router = APIRouter(prefix='/api/v1')
api_router.include_router(user_router, prefix='/auth')

@api_router.get("/health")
async def health():
    return {"status": "ok"}