from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest, UserPublic
from app.services.user import UserService


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserPublic:
    user_service = UserService(db)

    if user_service.get_user_by_email(payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = user_service.create_user(
        name=payload.name,
        lastname=payload.lastname,
        email=payload.email,
        password=payload.password,
    )
    return UserPublic.model_validate(user)


@auth_router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user_service = UserService(db)
    user = user_service.authenticate_user(payload.email, payload.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    return LoginResponse(
        message="Login successful",
        user=UserPublic.model_validate(user),
    )
