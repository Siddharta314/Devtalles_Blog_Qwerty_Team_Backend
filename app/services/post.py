from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.post import Post


class PostService:
    def __init__(self, db: Session):
        self.db = db

    def create_post(
        self,
        title: str,
        description: str,
        author_id: int,
        images: Optional[List[str]] = None,
        video: Optional[str] = None,
    ) -> Post:
        post = Post(
            title=title,
            description=description,
            author_id=author_id,
            images=images or [],
            video=video,
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        return (
            self.db.query(Post)
            .filter(Post.id == post_id, Post.deleted_at.is_(None))
            .first()
        )

    def get_posts(
        self, skip: int = 0, limit: int = 10, author_id: Optional[int] = None
    ) -> List[Post]:
        """Get posts with pagination and optional author filter."""
        query = self.db.query(Post).filter(Post.deleted_at.is_(None))

        if author_id is not None:
            query = query.filter(Post.author_id == author_id)

        return query.order_by(desc(Post.created_at)).offset(skip).limit(limit).all()

    def update_post(
        self,
        post_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        images: Optional[List[str]] = None,
        video: Optional[str] = None,
    ) -> Optional[Post]:
        """Update an existing post."""
        post = self.get_post_by_id(post_id)
        if not post:
            return None

        if title is not None:
            post.title = title
        if description is not None:
            post.description = description
        if images is not None:
            post.images = images
        if video is not None:
            post.video = video

        self.db.commit()
        self.db.refresh(post)
        return post

    def delete_post(self, post_id: int) -> bool:
        """Soft delete a post."""
        post = self.get_post_by_id(post_id)
        if not post:
            return False

        post.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        return True

    def get_posts_by_author(self, author_id: int) -> List[Post]:
        """Get all posts by a specific author."""
        return (
            self.db.query(Post)
            .filter(Post.author_id == author_id, Post.deleted_at.is_(None))
            .order_by(desc(Post.created_at))
            .all()
        )

    def count_posts(self, author_id: Optional[int] = None) -> int:
        query = self.db.query(Post).filter(Post.deleted_at.is_(None))
        if author_id is not None:
            query = query.filter(Post.author_id == author_id)
        return query.count()
