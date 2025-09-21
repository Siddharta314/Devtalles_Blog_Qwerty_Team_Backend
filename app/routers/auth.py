from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserPublic,
    UserAuthProviderResponse,
    DiscordCustomLoginRequest,
    DiscordCustomUserResponse,
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


@auth_router.get("/provider/{user_id}", response_model=UserAuthProviderResponse)
def get_user_auth_provider(
    user_id: int, db: Session = Depends(get_db)
) -> UserAuthProviderResponse:
    """Obtener el proveedor de autenticación de un usuario"""
    user_service = UserService(db)

    # Verificar que el usuario existe
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    # Buscar el proveedor de autenticación
    auth_provider = user_service.get_user_auth_provider(user_id)

    if auth_provider:
        # Usuario registrado con proveedor social
        return UserAuthProviderResponse(
            user_id=user_id,
            provider=auth_provider.provider.value,
            provider_id=auth_provider.provider_id,
        )
    else:
        # Usuario registrado con email/password
        return UserAuthProviderResponse(user_id=user_id, provider="local")


# Endpoints personalizados para NextAuth Discord flow
@auth_router.post("/discord/custom-login", response_model=LoginResponse)
def discord_custom_login(
    request: DiscordCustomLoginRequest, db: Session = Depends(get_db)
) -> LoginResponse:
    """
    Endpoint personalizado para NextAuth Discord flow.
    Recibe token y account directamente del frontend.
    """
    user_service = UserService(db)

    try:
        # Crear o actualizar usuario Discord
        user, auth_provider = user_service.create_or_update_discord_user(
            name=request.token.name,
            email=request.token.email,
            image=request.token.picture,
            provider_id=request.account.providerAccountId,
            access_token=request.account.access_token,
            refresh_token=request.account.refresh_token,
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

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al procesar login de Discord: {str(e)}",
        )


@auth_router.get(
    "/discord/custom-user/{user_id}", response_model=DiscordCustomUserResponse
)
def get_discord_custom_user(
    user_id: int, db: Session = Depends(get_db)
) -> DiscordCustomUserResponse:
    """
    Obtener datos del usuario con auth_provider_id para NextAuth.
    """
    user_service = UserService(db)

    # Verificar que el usuario existe
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    # Obtener auth_provider
    auth_provider = user_service.get_user_auth_provider(user_id)
    auth_provider_id = auth_provider.id if auth_provider else None

    return DiscordCustomUserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        image=user.image,
        role=user.role,
        auth_provider_id=auth_provider_id,
    )
