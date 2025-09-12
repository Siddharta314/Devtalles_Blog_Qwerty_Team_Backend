from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.category import Category
from app.models.post import Post


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def create_category(self, name: str, description: Optional[str] = None) -> Category:
        """Create a new category."""
        # Check if category name already exists
        existing = self.get_category_by_name(name)
        if existing:
            raise ValueError("Category with this name already exists")

        category = Category(name=name, description=description)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Get a category by ID."""
        return (
            self.db.query(Category)
            .filter(Category.id == category_id, Category.deleted_at.is_(None))
            .first()
        )

    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Get a category by name."""
        return (
            self.db.query(Category)
            .filter(Category.name == name, Category.deleted_at.is_(None))
            .first()
        )

    def get_categories(self, skip: int = 0, limit: int = 100) -> List[Category]:
        """Get all categories with pagination."""
        return (
            self.db.query(Category)
            .filter(Category.deleted_at.is_(None))
            .order_by(Category.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_categories(self) -> int:
        """Count total categories."""
        return self.db.query(Category).filter(Category.deleted_at.is_(None)).count()

    def update_category(
        self,
        category_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Category]:
        """Update an existing category."""
        category = self.get_category_by_id(category_id)
        if not category:
            return None

        # Check name uniqueness if name is being updated
        if name and name != category.name:
            existing = self.get_category_by_name(name)
            if existing:
                raise ValueError("Category with this name already exists")

        if name is not None:
            category.name = name
        if description is not None:
            category.description = description

        self.db.commit()
        self.db.refresh(category)
        return category

    def delete_category(self, category_id: int) -> bool:
        """Soft delete a category. Posts will have category_id set to NULL."""
        category = self.get_category_by_id(category_id)
        if not category:
            return False

        # sin check hacemos que el post tenga categoria null
        # posts_count = (
        #     self.db.query(Post)
        #     .filter(Post.category_id == category_id, Post.deleted_at.is_(None))
        #     .count()
        # )
        # if posts_count > 0:
        #     raise ValueError(f"Cannot delete category with {posts_count} posts")

        category.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        return True

    def get_categories_with_stats(self) -> List[dict]:
        """Get categories with post count statistics."""
        query = (
            self.db.query(
                Category.id,
                Category.name,
                Category.description,
                Category.created_at,
                Category.updated_at,
                func.count(Post.id).label("posts_count"),
            )
            .outerjoin(Post, Category.id == Post.category_id)
            .filter(Category.deleted_at.is_(None))
            .filter(Post.deleted_at.is_(None))
            .group_by(Category.id)
            .order_by(Category.name)
        )

        return [
            {
                "id": row.id,
                "name": row.name,
                "description": row.description,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "posts_count": row.posts_count,
            }
            for row in query.all()
        ]

    def get_posts_by_category(self, category_id: int) -> List[Post]:
        """Get all posts in a specific category."""
        return (
            self.db.query(Post)
            .filter(
                Post.category_id == category_id,
                Post.deleted_at.is_(None),
            )
            .order_by(Post.created_at.desc())
            .all()
        )
