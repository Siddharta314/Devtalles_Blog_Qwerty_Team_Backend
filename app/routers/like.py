from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies.auth import get_current_user, get_token_data
from app.schemas.auth import UserPublic, TokenData
from app.schemas.like import LikeCreate, LikePublic, LikeStats, PostLikesList
from app.services.like import LikeService


like_router = APIRouter(prefix="/likes", tags=["Likes"])


@like_router.post("/", response_model=LikePublic, status_code=status.HTTP_201_CREATED)
def create_like(
    like_data: LikeCreate,
    current_user: UserPublic = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LikePublic:
    """Like a post. Requires authentication."""
    like_service = LikeService(db)

    try:
        like = like_service.create_like(
            user_id=current_user.id,
            post_id=like_data.post_id,
        )
    except ValueError as e:
        if "already liked" in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return LikePublic.model_validate(like)


@like_router.delete("/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_like(
    post_id: int,
    current_user: UserPublic = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Remove like from a post. Requires authentication."""
    like_service = LikeService(db)

    success = like_service.remove_like(current_user.id, post_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Like not found"
        )


@like_router.post("/toggle", response_model=dict)
def toggle_like(
    like_data: LikeCreate,
    current_user: UserPublic = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Toggle like status for a post. Returns the new status."""
    like_service = LikeService(db)

    try:
        is_liked, like_obj = like_service.toggle_like(
            current_user.id, like_data.post_id
        )

        return {
            "is_liked": is_liked,
            "post_id": like_data.post_id,
            "user_id": current_user.id,
            "like": LikePublic.model_validate(like_obj) if like_obj else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@like_router.get("/post/{post_id}/stats", response_model=LikeStats)
def get_post_like_stats(
    post_id: int,
    token_data: TokenData = Depends(get_token_data),
    db: Session = Depends(get_db),
) -> LikeStats:
    """Get like statistics for a post including current user's like status."""
    like_service = LikeService(db)

    likes_count = like_service.get_post_likes_count(post_id)
    user_has_liked = like_service.has_user_liked_post(int(token_data.sub), post_id)

    return LikeStats(
        post_id=post_id,
        likes_count=likes_count,
        user_has_liked=user_has_liked,
    )


@like_router.get("/post/{post_id}", response_model=PostLikesList)
def get_post_likes(
    post_id: int,
    db: Session = Depends(get_db),
) -> PostLikesList:
    """Get all likes for a specific post."""
    like_service = LikeService(db)

    likes = like_service.get_post_likes(post_id)
    likes_count = len(likes)

    return PostLikesList(
        post_id=post_id,
        likes_count=likes_count,
        likes=[LikePublic.model_validate(like) for like in likes],
    )


@like_router.get("/me/posts", response_model=list[LikePublic])
def get_my_liked_posts(
    token_data: TokenData = Depends(get_token_data),
    db: Session = Depends(get_db),
) -> list[LikePublic]:
    """Get all posts liked by current user using token data (faster)."""
    like_service = LikeService(db)

    likes = like_service.get_user_liked_posts(int(token_data.sub))

    return [LikePublic.model_validate(like) for like in likes]


@like_router.get("/check/{post_id}", response_model=dict)
def check_user_liked_post(
    post_id: int,
    token_data: TokenData = Depends(get_token_data),
    db: Session = Depends(get_db),
) -> dict:
    """Check if current user has liked a specific post."""
    like_service = LikeService(db)

    has_liked = like_service.has_user_liked_post(int(token_data.sub), post_id)

    return {
        "post_id": post_id,
        "user_id": int(token_data.sub),
        "has_liked": has_liked,
    }
