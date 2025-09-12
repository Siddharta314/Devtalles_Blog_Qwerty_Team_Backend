from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, Boolean

from app.models.like import Like
from app.models.post import Post


class LikeService:
    def __init__(self, db: Session):
        self.db = db

    def create_like(self, user_id: int, post_id: int) -> Like:
        """Create a like for a post. Validates post exists and prevents duplicates."""
        post = (
            self.db.query(Post)
            .filter(Post.id == post_id, Post.deleted_at.is_(None))
            .first()
        )
        if not post:
            raise ValueError("Post not found or has been deleted")

        existing_like = self.get_like(user_id, post_id)
        if existing_like:
            raise ValueError("User has already liked this post")

        like = Like(user_id=user_id, post_id=post_id)
        self.db.add(like)
        self.db.commit()
        self.db.refresh(like)
        return like

    def remove_like(self, user_id: int, post_id: int) -> bool:
        """Remove a like. Returns True if like was removed, False if it didn't exist."""
        like = self.get_like(user_id, post_id)
        if not like:
            return False

        self.db.delete(like)
        self.db.commit()
        return True

    def get_like(self, user_id: int, post_id: int) -> Optional[Like]:
        """Get a specific like by user_id and post_id."""
        return (
            self.db.query(Like)
            .filter(and_(Like.user_id == user_id, Like.post_id == post_id))
            .first()
        )

    def has_user_liked_post(self, user_id: int, post_id: int) -> bool:
        """Check if a user has liked a specific post."""
        return self.get_like(user_id, post_id) is not None

    def get_post_likes_count(self, post_id: int) -> int:
        """Get the total number of likes for a post."""
        return self.db.query(Like).filter(Like.post_id == post_id).count()

    def get_post_likes(self, post_id: int) -> List[Like]:
        """Get all likes for a specific post."""
        return self.db.query(Like).filter(Like.post_id == post_id).all()

    def get_user_liked_posts(self, user_id: int) -> List[Like]:
        """Get all posts liked by a specific user."""
        return self.db.query(Like).filter(Like.user_id == user_id).all()

    def toggle_like(self, user_id: int, post_id: int) -> tuple[bool, Like | None]:
        """
        Toggle like status for a post.
        Returns (is_liked, like_object) where:
        - is_liked: True if like was added, False if removed
        - like_object: Like instance if added, None if removed
        """
        existing_like = self.get_like(user_id, post_id)

        if existing_like:
            self.db.delete(existing_like)
            self.db.commit()
            return False, None
        else:
            try:
                like = self.create_like(user_id, post_id)
                return True, like
            except ValueError:
                raise

    def get_posts_with_like_stats(self, user_id: Optional[int] = None) -> List[dict]:
        """Get posts with like statistics and user's like status."""
        user_like_col = (
            func.max((Like.user_id == user_id).cast(Boolean))
            if user_id
            else func.cast(False, Boolean)  # type: ignore
        ).label("user_has_liked")
        query = (
            self.db.query(
                Post.id.label("post_id"),
                func.count(Like.user_id).label("likes_count"),
                user_like_col,
            )
            .outerjoin(Like, Post.id == Like.post_id)
            .filter(Post.deleted_at.is_(None))
            .group_by(Post.id)
        )
        # Postgres
        # query = (
        #     self.db.query(
        #         Post.id.label("post_id"),
        #         func.count(Like.user_id).label("likes_count"),
        #         func.bool_or(Like.user_id == user_id).label("user_has_liked")
        #         if user_id
        #         else func.cast(False, Boolean).label("user_has_liked"),
        #     )
        #     .outerjoin(Like, Post.id == Like.post_id)
        #     .filter(Post.deleted_at.is_(None))
        #     .group_by(Post.id)
        # )

        return [
            {
                "post_id": row.post_id,
                "likes_count": row.likes_count,
                "user_has_liked": row.user_has_liked if user_id else False,
            }
            for row in query.all()
        ]
