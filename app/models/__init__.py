from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, declared_attr


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )

    @declared_attr.directive
    def __mapper_args__(cls):
        return {"eager_defaults": True}


# Importar todos los modelos para que Alembic los detecte
from .user import User
from .auth_provider import AuthProvider
from .post import Post
from .category import Category
from .tag import Tag
from .comment import Comment
from .like import Like
