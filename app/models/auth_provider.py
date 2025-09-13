from sqlalchemy import Integer, String, Enum as SQLEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db import Base
from app.models import TimestampMixin


class ProviderType(enum.Enum):
    DISCORD = "discord"


class AuthProvider(TimestampMixin, Base):
    __tablename__ = "auth_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    provider: Mapped[ProviderType] = mapped_column(
        SQLEnum(ProviderType), nullable=False
    )
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False)
    access_token: Mapped[str] = mapped_column(String(512), nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(String(512), nullable=True)

    user = relationship("User", back_populates="auth_provider")

    # Constraint: Un provider_id solo puede estar asociado a un provider
    __table_args__ = (
        UniqueConstraint("provider", "provider_id", name="unique_provider_account"),
    )
