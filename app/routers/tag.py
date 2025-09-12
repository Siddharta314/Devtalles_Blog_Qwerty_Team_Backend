from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies.auth import get_current_admin_user
from app.schemas.auth import UserPublic
from app.schemas.tag import (
    TagCreate,
    TagUpdate,
    TagPublic,
    TagWithStats,
    TagList,
    PopularTag,
)
from app.services.tag import TagService


tag_router = APIRouter(prefix="/tags", tags=["Tags"])


@tag_router.post("/", response_model=TagPublic, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag_data: TagCreate,
    admin: UserPublic = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> TagPublic:
    """Create a new tag. Admin only."""
    tag_service = TagService(db)

    try:
        tag = tag_service.get_or_create_tag(tag_data.name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return TagPublic.model_validate(tag)


@tag_router.get("/", response_model=TagList)
def get_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> TagList:
    """Get all tags with pagination. Public endpoint."""
    tag_service = TagService(db)

    tags = tag_service.get_all_tags(skip=skip, limit=limit)
    total = tag_service.count_tags()

    return TagList(
        tags=[TagPublic.model_validate(tag) for tag in tags],
        total=total,
    )


@tag_router.get("/popular", response_model=list[PopularTag])
def get_popular_tags(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[PopularTag]:
    """Get most popular tags by post count. Public endpoint."""
    tag_service = TagService(db)

    popular_tags = tag_service.get_popular_tags(limit=limit)

    return [PopularTag.model_validate(tag) for tag in popular_tags]


@tag_router.get("/stats", response_model=list[TagWithStats])
def get_tags_with_stats(
    admin: UserPublic = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> list[TagWithStats]:
    """Get tags with post count statistics. Admin only."""
    tag_service = TagService(db)

    tags_stats = tag_service.get_tags_with_stats()

    return [TagWithStats.model_validate(tag) for tag in tags_stats]


@tag_router.get("/{tag_id}", response_model=TagPublic)
def get_tag(
    tag_id: int,
    admin: UserPublic = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> TagPublic:
    """Get a specific tag by ID. Admin only."""
    tag_service = TagService(db)

    tag = tag_service.get_tag_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )

    return TagPublic.model_validate(tag)


@tag_router.put("/{tag_id}", response_model=TagPublic)
def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    admin: UserPublic = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> TagPublic:
    """Update a tag. Admin only."""
    tag_service = TagService(db)

    try:
        updated_tag = tag_service.update_tag(tag_id, tag_data.name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    if not updated_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )

    return TagPublic.model_validate(updated_tag)


@tag_router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    admin: UserPublic = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a tag. Admin only. Posts will lose this tag."""
    tag_service = TagService(db)

    success = tag_service.delete_tag(tag_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
