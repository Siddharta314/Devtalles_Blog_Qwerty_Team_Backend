from fastapi import APIRouter
from .auth import auth_router
from .post import post_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(post_router)

__all__ = ["api_router"]
