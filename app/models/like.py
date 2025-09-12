from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (PrimaryKeyConstraint("user_id", "post_id"),)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"), nullable=False, index=True
    )

    user = relationship("User", back_populates="likes", lazy="joined")
    post = relationship("Post", back_populates="likes", lazy="joined")
