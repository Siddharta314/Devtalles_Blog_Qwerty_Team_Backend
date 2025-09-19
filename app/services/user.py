from sqlalchemy.orm import Session
from typing import Optional

from app.models.user import User
from app.models.auth_provider import AuthProvider, ProviderType


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, name: str, lastname: str, email: str, password: str) -> User:
        user = User.create_local(
            name=name,
            lastname=lastname,
            email=email,
            password=password,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(email)
        if user is None or not user.verify_password(password):
            return None
        return user

    def create_social_user(
        self, name: str, lastname: str, email: str, image: Optional[str] = None
    ) -> User:
        """Crear usuario para autenticación social"""
        user = User.create_social(
            name=name, lastname=lastname, email=email, image=image
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_provider(
        self, provider: ProviderType, provider_id: str
    ) -> Optional[User]:
        """Buscar usuario por proveedor social"""
        auth_provider = (
            self.db.query(AuthProvider)
            .filter(
                AuthProvider.provider == provider,
                AuthProvider.provider_id == provider_id,
            )
            .first()
        )
        return auth_provider.user if auth_provider else None

    def user_has_social_auth(self, user: User) -> bool:
        """Verificar si un usuario tiene autenticación social"""
        return user.auth_provider is not None

    def get_user_auth_provider_type(self, user: User) -> Optional[ProviderType]:
        """Obtener el tipo de proveedor de autenticación del usuario"""
        if user.auth_provider:
            return user.auth_provider.provider
        return None

    def get_user_auth_provider(self, user_id: int) -> Optional[AuthProvider]:
        """Obtener el proveedor de autenticación de un usuario por su ID"""
        return (
            self.db.query(AuthProvider).filter(AuthProvider.user_id == user_id).first()
        )

    def create_or_update_discord_user(
        self,
        name: str,
        email: str,
        image: Optional[str],
        provider_id: str,
        access_token: str,
        refresh_token: Optional[str] = None,
    ) -> tuple[User, AuthProvider]:
        """
        Crear o actualizar usuario Discord para NextAuth custom flow.
        Retorna (user, auth_provider)
        """
        try:
            # Buscar usuario existente por email
            user = self.get_user_by_email(email)

            if user:
                # Usuario existe, verificar si ya tiene auth_provider
                auth_provider = self.get_user_auth_provider(user.id)

                if auth_provider:
                    # Actualizar tokens y provider_id existentes
                    auth_provider.access_token = access_token
                    auth_provider.refresh_token = refresh_token
                    auth_provider.provider_id = (
                        provider_id  # Actualizar también provider_id
                    )
                else:
                    # Crear nuevo auth_provider para usuario existente
                    auth_provider = AuthProvider(
                        user_id=user.id,
                        provider=ProviderType.DISCORD,
                        provider_id=provider_id,
                        access_token=access_token,
                        refresh_token=refresh_token,
                    )
                    self.db.add(auth_provider)
            else:
                # Crear nuevo usuario social
                # Dividir name en name y lastname de forma segura
                try:
                    name_parts = name.strip().split(" ", 1)
                    first_name = name_parts[0] if name_parts[0] else "Usuario"
                    last_name = (
                        name_parts[1] if len(name_parts) > 1 and name_parts[1] else ""
                    )
                except (IndexError, AttributeError):
                    # Fallback si hay algún problema con el name
                    first_name = name.strip() if name else "Usuario"
                    last_name = ""

                user = User.create_social(
                    name=first_name, lastname=last_name, email=email, image=image
                )
                self.db.add(user)
                self.db.flush()  # Para obtener el ID

                # Crear auth_provider
                auth_provider = AuthProvider(
                    user_id=user.id,
                    provider=ProviderType.DISCORD,
                    provider_id=provider_id,
                    access_token=access_token,
                    refresh_token=refresh_token,
                )
                self.db.add(auth_provider)

            # Commit de toda la transacción
            self.db.commit()
            self.db.refresh(user)
            self.db.refresh(auth_provider)

            return user, auth_provider

        except Exception as e:
            self.db.rollback()
            raise e
