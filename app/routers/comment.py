from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies.auth import get_current_user, get_token_data
from app.models.user import UserRole
from app.schemas.auth import UserPublic, TokenData
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentPublic,
    CommentList,
)
from app.services.comment import CommentService


comment_router = APIRouter(prefix="/comments", tags=["Comments"])


@comment_router.post(
    "/", response_model=CommentPublic, status_code=status.HTTP_201_CREATED
)
def create_comment(
    comment_data: CommentCreate,
    current_user: UserPublic = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CommentPublic:
    comment_service = CommentService(db)

    try:
        comment = comment_service.create_comment(
            post_id=comment_data.post_id,
            author_id=current_user.id,
            content=comment_data.content,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return CommentPublic.model_validate(comment)


@comment_router.get("/post/{post_id}", response_model=CommentList)
def get_comments_by_post(
    post_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> CommentList:
    """Get comments for a specific post with pagination."""
    comment_service = CommentService(db)

    comments = comment_service.get_comments_by_post(
        post_id=post_id, skip=skip, limit=limit
    )
    total = comment_service.count_comments_by_post(post_id)

    return CommentList(
        comments=[CommentPublic.model_validate(comment) for comment in comments],
        total=total,
        skip=skip,
        limit=limit,
    )


@comment_router.put("/{comment_id}", response_model=CommentPublic)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: UserPublic = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CommentPublic:
    """Update a comment. Only author or admin can update."""
    comment_service = CommentService(db)

    try:
        updated_comment = comment_service.update_comment(
            comment_id=comment_id,
            user_id=current_user.id,
            is_admin=current_user.role == UserRole.ADMIN,
            content=comment_data.content,
        )
    except ValueError as e:
        if "Not authorized" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    return CommentPublic.model_validate(updated_comment)


@comment_router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    current_user: UserPublic = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a comment. Only author or admin can delete."""
    comment_service = CommentService(db)

    try:
        comment_service.delete_comment(
            comment_id=comment_id,
            user_id=current_user.id,
            is_admin=current_user.role == UserRole.ADMIN,
        )

    except ValueError as e:
        if "Not authorized" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )


@comment_router.get("/me/comments", response_model=list[CommentPublic])
def get_my_comments(
    token_data: TokenData = Depends(get_token_data),
    db: Session = Depends(get_db),
) -> list[CommentPublic]:
    """Get current user's comments using token data (faster)."""
    comment_service = CommentService(db)

    comments = comment_service.get_comments_by_author(int(token_data.sub))

    return [CommentPublic.model_validate(comment) for comment in comments]


@comment_router.get("/{comment_id}", response_model=CommentPublic)
def get_comment(comment_id: int, db: Session = Depends(get_db)) -> CommentPublic:
    """Get a specific comment by ID."""
    comment_service = CommentService(db)

    comment = comment_service.get_comment_by_id(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    return CommentPublic.model_validate(comment)
