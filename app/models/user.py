from passlib.context import CryptContext
from sqlalchemy import Integer, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db import Base
from app.models import TimestampMixin


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"


class UserPosition(enum.Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    FULLSTACK = "fullstack"
    DEVOPS = "devops"
    MOBILE = "mobile"
    DATA = "data"
    DESIGN = "design"
    OTHER = "other"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    lastname: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str | None] = mapped_column(String(512), nullable=True)
    image: Mapped[str | None] = mapped_column(String(512), nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    position: Mapped[UserPosition | None] = mapped_column(
        SQLEnum(UserPosition), nullable=True
    )
    stack: Mapped[str | None] = mapped_column(String(200), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), default=UserRole.USER, nullable=False
    )

    posts = relationship(
        "Post",
        back_populates="author",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    comments = relationship(
        "Comment",
        back_populates="author",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    likes = relationship(
        "Like",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    auth_provider = relationship(
        "AuthProvider",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        self.hashed_password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        if not self.hashed_password:
            return False
        return pwd_context.verify(password, self.hashed_password)

    @property
    def full_name(self) -> str:
        return f"{self.name} {self.lastname}"

    @property
    def is_local_user(self) -> bool:
        return self.hashed_password is not None

    @property
    def is_social_user(self) -> bool:
        return self.auth_provider is not None

    @classmethod
    def create_local(
        cls, name: str, lastname: str, email: str, password: str
    ) -> "User":
        user = cls(name=name, lastname=lastname, email=email)
        user.set_password(password)
        return user

    @classmethod
    def create_social(
        cls, name: str, lastname: str, email: str, image: str | None = None
    ) -> "User":
        return cls(
            name=name, lastname=lastname, email=email, image=image, hashed_password=None
        )
