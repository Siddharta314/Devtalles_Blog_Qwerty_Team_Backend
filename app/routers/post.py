from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies.auth import (
    get_current_user,
    get_token_data,
    get_current_admin_user,
)
from app.models.user import UserRole
from app.schemas.auth import UserPublic, TokenData
from app.schemas.post import PostCreate, PostUpdate, PostPublic, PostList
from app.services.post import PostService


post_router = APIRouter(prefix="/posts", tags=["Posts"])


@post_router.post("/", response_model=PostPublic, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: PostCreate,
    current_user: UserPublic = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PostPublic:
    """Create a new post. Requires authentication."""
    post_service = PostService(db)

    post = post_service.create_post(
        title=post_data.title,
        description=post_data.description,
        author_id=current_user.id,
        images=post_data.images,
        video=post_data.video,
    )

    return PostPublic.model_validate(post)


@post_router.get("/", response_model=PostList)
def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    author_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_admin_user),
) -> PostList:
    """Get posts with pagination and optional author filter."""
    post_service = PostService(db)

    posts = post_service.get_posts(skip=skip, limit=limit, author_id=author_id)

    total = post_service.count_posts(author_id=author_id)
    return PostList(
        posts=[PostPublic.model_validate(post) for post in posts],
        total=total,
        skip=skip,
        limit=limit,
    )


@post_router.put("/{post_id}", response_model=PostPublic)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: UserPublic = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PostPublic:
    """Update a post. Only author or admin can update."""
    post_service = PostService(db)

    existing_post = post_service.get_post_by_id(post_id)
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if (
        existing_post.author_id != current_user.id
        and current_user.role != UserRole.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )

    updated_post = post_service.update_post(
        post_id=post_id,
        title=post_data.title,
        description=post_data.description,
        images=post_data.images,
        video=post_data.video,
    )

    return PostPublic.model_validate(updated_post)


@post_router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    current_user: UserPublic = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a post. Only author or admin can delete."""
    post_service = PostService(db)

    existing_post = post_service.get_post_by_id(post_id)
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if (
        existing_post.author_id != current_user.id
        and current_user.role != UserRole.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post",
        )

    success = post_service.delete_post(post_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete post",
        )


@post_router.get("/author/{author_id}", response_model=list[PostPublic])
def get_posts_by_author(
    author_id: int,
    db: Session = Depends(get_db),
) -> list[PostPublic]:
    """Get all posts by a specific author."""
    post_service = PostService(db)

    posts = post_service.get_posts_by_author(author_id)

    return [PostPublic.model_validate(post) for post in posts]


@post_router.get("/me/posts", response_model=list[PostPublic])
def get_my_posts(
    token_data: TokenData = Depends(get_token_data),
    db: Session = Depends(get_db),
) -> list[PostPublic]:
    """Get current user's posts using token data (faster)."""
    post_service = PostService(db)

    posts = post_service.get_posts_by_author(int(token_data.sub))

    return [PostPublic.model_validate(post) for post in posts]


@post_router.get("/{post_id}", response_model=PostPublic)
def get_post(post_id: int, db: Session = Depends(get_db)) -> PostPublic:
    """Get a specific post by ID."""
    post_service = PostService(db)

    post = post_service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    return PostPublic.model_validate(post)
