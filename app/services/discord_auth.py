import httpx
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.models.auth_provider import AuthProvider, ProviderType


class DiscordAuthService:
    """Servicio para manejar autenticación con Discord OAuth2"""

    DISCORD_API_BASE = "https://discord.com/api/v10"
    DISCORD_OAUTH_BASE = "https://discord.com/api/oauth2"

    def __init__(self, db: Session):
        self.db = db

    def get_authorization_url(self) -> str:
        """Genera la URL de autorización de Discord"""
        params = {
            "client_id": settings.DISCORD_CLIENT_ID,
            "redirect_uri": settings.DISCORD_REDIRECT_URI,
            "response_type": "code",
            "scope": "identify email",
        }
        return f"{self.DISCORD_OAUTH_BASE}/authorize?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Intercambia el código de autorización por tokens de acceso"""
        data = {
            "client_id": settings.DISCORD_CLIENT_ID,
            "client_secret": settings.DISCORD_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.DISCORD_REDIRECT_URI,
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.DISCORD_OAUTH_BASE}/token", data=data, headers=headers
            )

            if response.status_code != 200:
                return None

            return response.json()

    async def get_discord_user(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Obtiene la información del usuario desde Discord API"""
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.DISCORD_API_BASE}/users/@me", headers=headers
            )

            if response.status_code != 200:
                return None

            return response.json()

    def find_user_by_discord_id(self, discord_id: str) -> Optional[User]:
        """Busca un usuario por su ID de Discord"""
        auth_provider = (
            self.db.query(AuthProvider)
            .filter(
                AuthProvider.provider == ProviderType.DISCORD,
                AuthProvider.provider_id == discord_id,
            )
            .first()
        )
        return auth_provider.user if auth_provider else None

    def find_user_by_email(self, email: str) -> Optional[User]:
        """Busca un usuario por email"""
        return self.db.query(User).filter(User.email == email).first()

    def create_discord_user(
        self,
        discord_data: Dict[str, Any],
        access_token: str,
        refresh_token: Optional[str] = None,
    ) -> User:
        """Crea un nuevo usuario con autenticación Discord"""
        # Extraer datos de Discord
        discord_id = discord_data["id"]
        username = discord_data.get("username", "Discord User")
        global_name = discord_data.get("global_name", username)
        email = discord_data.get("email", "")
        avatar = discord_data.get("avatar")

        # Construir URL del avatar si existe
        avatar_url = None
        if avatar:
            avatar_url = f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar}.png"

        # Separar nombre y apellido (Discord no tiene lastname)
        name_parts = global_name.split(" ", 1)
        name = name_parts[0]
        lastname = name_parts[1] if len(name_parts) > 1 else ""

        # Debug info (solo en desarrollo)
        from app.core.config import settings as _settings
        if _settings.DEBUG:
            print(
                "[DiscordAuth] Creating user:",
                {
                    "discord_id": discord_id,
                    "email": email,
                    "username": username,
                    "global_name": global_name,
                    "avatar_url": avatar_url,
                },
            )

        # Crear usuario social
        user = User.create_social(
            name=name, lastname=lastname, email=email, image=avatar_url
        )

        self.db.add(user)
        self.db.flush()  # Para obtener el ID del usuario

        # Crear registro de auth_provider
        auth_provider = AuthProvider(
            user_id=user.id,
            provider=ProviderType.DISCORD,
            provider_id=discord_id,
            access_token=access_token,
            refresh_token=refresh_token,
        )

        self.db.add(auth_provider)
        self.db.commit()
        self.db.refresh(user)

        return user

    def link_discord_to_existing_user(
        self,
        user: User,
        discord_id: str,
        access_token: str,
        refresh_token: Optional[str] = None,
    ) -> User:
        """Vincula una cuenta Discord a un usuario existente (por email)."""
        existing_provider = (
            self.db.query(AuthProvider)
            .filter(AuthProvider.user_id == user.id)
            .first()
        )

        if existing_provider:
            # Ya hay un proveedor asociado: actualizar tokens si es DISCORD
            if existing_provider.provider != ProviderType.DISCORD:
                # En este proyecto solo hay DISCORD como provider, pero por seguridad
                existing_provider.provider = ProviderType.DISCORD
            existing_provider.provider_id = discord_id
            existing_provider.access_token = access_token
            if refresh_token:
                existing_provider.refresh_token = refresh_token
        else:
            auth_provider = AuthProvider(
                user_id=user.id,
                provider=ProviderType.DISCORD,
                provider_id=discord_id,
                access_token=access_token,
                refresh_token=refresh_token,
            )
            self.db.add(auth_provider)

        self.db.commit()
        self.db.refresh(user)
        return user

    def update_discord_tokens(
        self, user: User, access_token: str, refresh_token: Optional[str] = None
    ) -> None:
        """Actualiza los tokens de Discord de un usuario existente"""
        if user.auth_provider and user.auth_provider.provider == ProviderType.DISCORD:
            user.auth_provider.access_token = access_token
            if refresh_token:
                user.auth_provider.refresh_token = refresh_token
            self.db.commit()

    async def authenticate_with_discord(self, code: str) -> Optional[User]:
        """
        Proceso completo de autenticación con Discord
        1. Intercambia code por tokens
        2. Obtiene datos del usuario
        3. Busca o crea el usuario
        4. Retorna el usuario autenticado
        """
        # Obtener tokens
        token_data = await self.exchange_code_for_token(code)
        if not token_data:
            return None

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")

        if not access_token:
            return None

        # Obtener datos del usuario
        discord_user = await self.get_discord_user(access_token)
        if not discord_user:
            return None

        discord_id = discord_user["id"]
        email = discord_user.get("email")

        # Fallback: si no hay email de Discord, generar uno sintético estable
        if not email:
            email = f"discord_{discord_id}@discord.local"
            # Mutar el payload para que los siguientes pasos usen este email
            discord_user["email"] = email

        # Buscar usuario existente por Discord ID
        existing_user = self.find_user_by_discord_id(discord_id)

        if existing_user:
            # Usuario ya existe, actualizar tokens
            self.update_discord_tokens(existing_user, access_token, refresh_token)
            return existing_user

        # Verificar si ya existe un usuario con ese email
        if email:
            email_user = self.find_user_by_email(email)
            if email_user:
                # Según configuración, vincular o rechazar
                if settings.ALLOW_SOCIAL_LINK_BY_EMAIL:
                    return self.link_discord_to_existing_user(
                        email_user, discord_id, access_token, refresh_token
                    )
                else:
                    # Rechazar el intento para evitar colisión de email
                    raise ValueError(f"User with email {email} already exists")

        # Crear nuevo usuario
        return self.create_discord_user(discord_user, access_token, refresh_token)
