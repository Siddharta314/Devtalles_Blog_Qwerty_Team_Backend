from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.comment import Comment
from app.models.post import Post


class CommentService:
    def __init__(self, db: Session):
        self.db = db

    def create_comment(self, post_id: int, author_id: int, content: str) -> Comment:
        post = (
            self.db.query(Post)
            .filter(Post.id == post_id, Post.deleted_at.is_(None))
            .first()
        )
        if not post:
            raise ValueError("Post not found or has been deleted")

        comment = Comment(
            content=content,
            author_id=author_id,
            post_id=post_id,
        )
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def get_comment_by_id(self, comment_id: int) -> Optional[Comment]:
        return (
            self.db.query(Comment)
            .filter(Comment.id == comment_id, Comment.deleted_at.is_(None))
            .first()
        )

    def get_comments_by_post(
        self, post_id: int, skip: int = 0, limit: int = 10
    ) -> List[Comment]:
        return (
            self.db.query(Comment)
            .filter(Comment.post_id == post_id, Comment.deleted_at.is_(None))
            .order_by(desc(Comment.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_comments_by_post(self, post_id: int) -> int:
        return (
            self.db.query(Comment)
            .filter(Comment.post_id == post_id, Comment.deleted_at.is_(None))
            .count()
        )

    def get_comments_by_author(self, author_id: int) -> List[Comment]:
        return (
            self.db.query(Comment)
            .filter(Comment.author_id == author_id, Comment.deleted_at.is_(None))
            .order_by(desc(Comment.created_at))
            .all()
        )

    def update_comment(
        self,
        comment_id: int,
        user_id: int,
        is_admin: bool,
        content: str,
    ) -> Comment:
        comment = self.get_comment_by_id(comment_id)
        if not comment:
            raise ValueError("Comment not found")

        if not self.can_modify_comment(comment, user_id, is_admin):
            raise ValueError("Not authorized to update this comment")

        comment.content = content
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def delete_comment(self, comment_id: int, user_id: int, is_admin: bool) -> bool:
        """Soft delete a comment."""
        comment = self.get_comment_by_id(comment_id)
        if not comment:
            raise ValueError("Comment not found")

        if not self.can_modify_comment(comment, user_id, is_admin):
            raise ValueError("Not authorized to delete this comment")

        comment.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        return True

    def can_modify_comment(
        self, comment: Comment, user_id: int, is_admin: bool
    ) -> bool:
        return comment.author_id == user_id or is_admin
