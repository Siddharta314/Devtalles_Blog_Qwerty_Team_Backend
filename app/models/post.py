from sqlalchemy import ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.db import Base
from app.models import TimestampMixin


class Post(TimestampMixin, Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    images: Mapped[list[str]] = mapped_column(JSON, nullable=False, server_default="[]")
    video: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )

    author = relationship(
        "User",
        back_populates="posts",
        lazy="joined",
    )
    category = relationship(
        "Category",
        back_populates="posts",
        lazy="joined",
    )
    comments = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    likes = relationship(
        "Like",
        back_populates="post",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    tags = relationship(
        "Tag",
        secondary="post_tags",
        back_populates="posts",
        lazy="selectin",
    )
