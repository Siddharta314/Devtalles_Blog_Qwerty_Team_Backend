from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.tag import Tag
from app.models.post import Post


class TagService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_tag(self, name: str) -> Tag:
        """Get existing tag or create new one if it doesn't exist."""
        normalized_name = name.strip().lower()

        if not normalized_name:
            raise ValueError("Tag name cannot be empty")

        if len(normalized_name) > 50:
            raise ValueError("Tag name cannot exceed 50 characters")

        existing_tag = (
            self.db.query(Tag)
            .filter(Tag.name == normalized_name, Tag.deleted_at.is_(None))
            .first()
        )

        if existing_tag:
            return existing_tag

        new_tag = Tag(name=normalized_name)
        self.db.add(new_tag)
        self.db.flush()  # Get ID without committing
        return new_tag

    def get_or_create_tags(self, tag_names: List[str]) -> List[Tag]:
        """Get or create multiple tags."""
        tags = []
        for name in tag_names:
            try:
                tag = self.get_or_create_tag(name)
                tags.append(tag)
            except ValueError:
                continue
        return tags

    def get_tag_by_id(self, tag_id: int) -> Optional[Tag]:
        """Get a tag by ID."""
        return (
            self.db.query(Tag)
            .filter(Tag.id == tag_id, Tag.deleted_at.is_(None))
            .first()
        )

    def get_tag_by_name(self, name: str) -> Optional[Tag]:
        """Get a tag by name."""
        normalized_name = name.strip().lower()
        return (
            self.db.query(Tag)
            .filter(Tag.name == normalized_name, Tag.deleted_at.is_(None))
            .first()
        )

    def get_all_tags(self, skip: int = 0, limit: int = 100) -> List[Tag]:
        """Get all tags with pagination."""
        return (
            self.db.query(Tag)
            .filter(Tag.deleted_at.is_(None))
            .order_by(Tag.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_tags(self) -> int:
        """Count total tags."""
        return self.db.query(Tag).filter(Tag.deleted_at.is_(None)).count()

    def get_tags_with_stats(self) -> List[dict]:
        """Get tags with post count statistics."""
        from app.models.tag import post_tags

        query = (
            self.db.query(
                Tag.id,
                Tag.name,
                Tag.created_at,
                Tag.updated_at,
                func.count(post_tags.c.post_id).label("posts_count"),
            )
            .outerjoin(post_tags, Tag.id == post_tags.c.tag_id)
            .outerjoin(Post, post_tags.c.post_id == Post.id)
            .filter(Tag.deleted_at.is_(None))
            .filter(Post.deleted_at.is_(None))
            .group_by(Tag.id)
            .order_by(Tag.name)
        )

        return [
            {
                "id": row.id,
                "name": row.name,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "posts_count": row.posts_count,
            }
            for row in query.all()
        ]

    def update_tag(self, tag_id: int, name: str) -> Optional[Tag]:
        """Update a tag name."""
        tag = self.get_tag_by_id(tag_id)
        if not tag:
            return None

        normalized_name = name.strip().lower()

        if not normalized_name:
            raise ValueError("Tag name cannot be empty")

        if len(normalized_name) > 50:
            raise ValueError("Tag name cannot exceed 50 characters")

        existing = (
            self.db.query(Tag)
            .filter(
                Tag.name == normalized_name, Tag.id != tag_id, Tag.deleted_at.is_(None)
            )
            .first()
        )

        if existing:
            raise ValueError("Tag with this name already exists")

        tag.name = normalized_name
        self.db.commit()
        return tag

    def delete_tag(self, tag_id: int) -> bool:
        """Soft delete a tag."""
        tag = self.get_tag_by_id(tag_id)
        if not tag:
            return False

        tag.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        return True

    def get_popular_tags(self, limit: int = 10) -> List[dict]:
        """Get most popular tags by post count."""
        from app.models.tag import post_tags

        query = (
            self.db.query(
                Tag.id,
                Tag.name,
                func.count(post_tags.c.post_id).label("posts_count"),
            )
            .join(post_tags, Tag.id == post_tags.c.tag_id)
            .join(Post, post_tags.c.post_id == Post.id)
            .filter(Tag.deleted_at.is_(None))
            .filter(Post.deleted_at.is_(None))
            .group_by(Tag.id)
            .order_by(func.count(post_tags.c.post_id).desc())
            .limit(limit)
        )

        return [
            {
                "id": row.id,
                "name": row.name,
                "posts_count": row.posts_count,
            }
            for row in query.all()
        ]
