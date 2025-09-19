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


# Schemas para NextAuth Discord custom flow
class NextAuthToken(BaseModel):
    """Token de NextAuth con datos del usuario"""

    name: str
    email: str
    picture: Optional[str] = None
    sub: str  # Discord user ID


class NextAuthAccount(BaseModel):
    """Account de NextAuth con datos del proveedor"""

    provider: str
    providerAccountId: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[int] = None


class DiscordCustomLoginRequest(BaseModel):
    """Request para el endpoint custom de Discord login"""

    token: NextAuthToken
    account: NextAuthAccount


class DiscordCustomUserResponse(BaseModel):
    """Response para el endpoint custom de Discord user"""

    id: int
    name: str
    email: str
    image: Optional[str] = None
    role: UserRole
    auth_provider_id: Optional[int] = None
    model_config = {"from_attributes": True}
