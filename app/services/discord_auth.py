import httpx
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.models.auth_provider import AuthProvider, ProviderType
from app.services.user import UserService


class DiscordAuthService:
    """Servicio para manejar autenticación con Discord OAuth2"""

    DISCORD_API_BASE = "https://discord.com/api/v10"
    DISCORD_OAUTH_BASE = "https://discord.com/api/oauth2"

    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

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
        """Obtiene los datos del usuario de Discord"""
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.DISCORD_API_BASE}/users/@me", headers=headers
            )

            if response.status_code != 200:
                return None

            return response.json()

    def find_user_by_discord_id(self, discord_id: str) -> Optional[User]:
        """Busca un usuario por su Discord ID"""
        return self.user_service.get_user_by_provider(ProviderType.DISCORD, discord_id)

    def find_user_by_email(self, email: str) -> Optional[User]:
        """Busca un usuario por su email"""
        return self.user_service.get_user_by_email(email)

    def create_discord_user(
        self,
        discord_user: Dict[str, Any],
        access_token: str,
        refresh_token: Optional[str],
    ) -> User:
        """Crea un nuevo usuario Discord"""
        # Construir nombre completo
        username = discord_user.get("username", "DiscordUser")
        global_name = discord_user.get("global_name")
        display_name = global_name or username

        # Obtener avatar
        avatar_hash = discord_user.get("avatar")
        image_url = None
        if avatar_hash:
            image_url = f"https://cdn.discordapp.com/avatars/{discord_user['id']}/{avatar_hash}.png"

        # Crear usuario usando el método unificado
        user, auth_provider = self.user_service.create_or_update_discord_user(
            name=display_name,
            email=discord_user["email"],
            image=image_url,
            provider_id=discord_user["id"],
            access_token=access_token,
            refresh_token=refresh_token,
        )

        return user

    def update_discord_tokens(
        self, user: User, access_token: str, refresh_token: Optional[str]
    ) -> None:
        """Actualiza los tokens de Discord para un usuario existente"""
        if user.auth_provider:
            user.auth_provider.access_token = access_token
            user.auth_provider.refresh_token = refresh_token
            self.db.commit()
            self.db.refresh(user.auth_provider)

    def link_discord_to_existing_user(
        self,
        user: User,
        discord_id: str,
        access_token: str,
        refresh_token: Optional[str],
    ) -> User:
        """Vincula una cuenta Discord a un usuario existente"""
        # Crear AuthProvider para el usuario existente
        auth_provider = AuthProvider(
            user_id=user.id,
            provider=ProviderType.DISCORD,
            provider_id=discord_id,
            access_token=access_token,
            refresh_token=refresh_token,
        )
        self.db.add(auth_provider)
        self.db.commit()
        self.db.refresh(auth_provider)

        return user

    async def authenticate_with_discord(self, code: str) -> Optional[User]:
        """
        Proceso completo de autenticación con Discord
        1. Intercambia code por tokens
        2. Obtiene datos del usuario
        3. Busca o crea el usuario usando el método unificado
        4. Retorna el usuario autenticado
        """
        # [P1] Inicio del flujo con el code recibido
        if settings.DEBUG:
            print(
                "[DiscordAuth][P1] Callback recibido",
                {
                    "code_prefix": (code[:8] + "...") if code else None,
                    "redirect_uri": settings.DISCORD_REDIRECT_URI,
                },
            )

        # Obtener tokens
        token_data = await self.exchange_code_for_token(code)
        if settings.DEBUG:
            print(
                "[DiscordAuth][P2] Intercambio de token",
                {
                    "success": token_data is not None,
                    "has_access_token": bool(
                        token_data and token_data.get("access_token")
                    ),
                    "has_refresh_token": bool(
                        token_data and token_data.get("refresh_token")
                    ),
                },
            )
        if not token_data:
            return None

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")

        if not access_token:
            return None

        # Obtener datos del usuario
        discord_user = await self.get_discord_user(access_token)
        if settings.DEBUG:
            print(
                "[DiscordAuth][P3] Datos de usuario",
                {
                    "success": discord_user is not None,
                    "id": discord_user.get("id") if discord_user else None,
                    "email_present": bool(discord_user and discord_user.get("email")),
                },
            )
        if not discord_user:
            return None

        discord_id = discord_user["id"]
        email = discord_user.get("email")

        # Fallback: si no hay email de Discord, generar uno sintético estable
        if not email:
            email = f"discord_{discord_id}@discord.local"
            # Mutar el payload para que los siguientes pasos usen este email
            discord_user["email"] = email

        # Construir nombre completo
        username = discord_user.get("username", "DiscordUser")
        global_name = discord_user.get("global_name")
        display_name = global_name or username

        # Obtener avatar
        avatar_hash = discord_user.get("avatar")
        image_url = None
        if avatar_hash:
            image_url = f"https://cdn.discordapp.com/avatars/{discord_user['id']}/{avatar_hash}.png"

        # Usar el método unificado para crear/actualizar usuario
        try:
            user, auth_provider = self.user_service.create_or_update_discord_user(
                name=display_name,
                email=email,
                image=image_url,
                provider_id=discord_id,
                access_token=access_token,
                refresh_token=refresh_token,
            )

            if settings.DEBUG:
                print(
                    "[DiscordAuth][P4] Usuario procesado",
                    {
                        "user_id": user.id,
                        "email": user.email,
                        "auth_provider_id": auth_provider.id,
                    },
                )

            return user

        except Exception as e:
            if settings.DEBUG:
                print("[DiscordAuth][ERROR] Error en autenticación", {"error": str(e)})
            raise e
