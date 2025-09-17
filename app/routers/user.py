from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.auth import UserPublic
from app.services.user import UserService

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get("/{user_id}", response_model=UserPublic)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)) -> UserPublic:
    """Obtener información pública de un usuario por su ID"""
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    return UserPublic.model_validate(user)
