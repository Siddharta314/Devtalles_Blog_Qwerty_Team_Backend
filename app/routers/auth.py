from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserPublic,
)
from app.services.user import UserService
from app.services.discord_auth import DiscordAuthService
from app.models.auth_provider import ProviderType
from app.utils.jwt import create_access_token


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

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
        }
    )

    return LoginResponse(
        user=UserPublic.model_validate(user),
        access_token=access_token,
        token_type="bearer",
        auth_provider=None,
    )


# Discord OAuth2 Endpoints
@auth_router.get("/discord/login")
def discord_login(db: Session = Depends(get_db)):
    """Redirige al usuario a Discord para autenticación OAuth2"""
    discord_service = DiscordAuthService(db)
    authorization_url = discord_service.get_authorization_url()
    return RedirectResponse(url=authorization_url)


@auth_router.get("/discord/callback", response_model=LoginResponse)
async def discord_callback(
    code: str, state: str | None = None, db: Session = Depends(get_db)
) -> LoginResponse:
    """
    Callback de Discord OAuth2
    Procesa el código de autorización y autentica al usuario
    """
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code is required",
        )

    discord_service = DiscordAuthService(db)

    try:
        # Autenticar con Discord
        user = await discord_service.authenticate_with_discord(code)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Discord authentication failed",
            )

        # Crear JWT con información del usuario
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value,
                "auth_provider": ProviderType.DISCORD.value,
            }
        )

        return LoginResponse(
            user=UserPublic.model_validate(user),
            access_token=access_token,
            token_type="bearer",
            auth_provider=ProviderType.DISCORD,
        )

    except HTTPException:
        # Propagar HTTPException generadas explícitamente (como 401)
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication process failed",
        )
