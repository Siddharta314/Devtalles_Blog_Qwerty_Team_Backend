from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import UserRole, UserPosition
from app.models.auth_provider import ProviderType


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    lastname: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserPublic(BaseModel):
    id: int
    name: str
    lastname: str
    email: EmailStr
    role: UserRole
    image: Optional[str] = None
    description: Optional[str] = None
    position: Optional[UserPosition] = None
    stack: Optional[str] = None
    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenData(BaseModel):
    sub: str  # user_id
    email: str
    role: UserRole
    auth_provider: Optional[ProviderType] = None


# Schemas específicos para Discord OAuth2
class DiscordUserInfo(BaseModel):
    """Información del usuario de Discord"""

    id: str
    username: str
    global_name: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None


class AuthProviderPublic(BaseModel):
    """Información pública del proveedor de autenticación"""

    provider: ProviderType
    provider_id: str
    model_config = {"from_attributes": True}


class UserAuthProviderResponse(BaseModel):
    """Respuesta del proveedor de autenticación de un usuario"""

    user_id: int
    provider: str  # "discord", "google", etc. o "local"
    provider_id: Optional[str] = None  # Solo para proveedores sociales


class LoginResponse(BaseModel):
    user: UserPublic
    access_token: str
    token_type: str = "bearer"
    auth_provider: Optional[ProviderType] = None
