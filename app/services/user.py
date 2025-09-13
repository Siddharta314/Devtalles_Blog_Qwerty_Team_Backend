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
