from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies.auth import get_current_admin_user
from app.schemas.auth import UserPublic
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryPublic,
    CategoryWithStats,
    CategoryList,
)
from app.services.category import CategoryService


category_router = APIRouter(prefix="/categories", tags=["Categories"])


@category_router.post(
    "/", response_model=CategoryPublic, status_code=status.HTTP_201_CREATED
)
def create_category(
    category_data: CategoryCreate,
    admin: UserPublic = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> CategoryPublic:
    """Create a new category. Admin only."""
    category_service = CategoryService(db)

    try:
        category = category_service.create_category(
            name=category_data.name,
            description=category_data.description,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return CategoryPublic.model_validate(category)


@category_router.get("/", response_model=CategoryList)
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> CategoryList:
    """Get all categories with pagination. Public endpoint."""
    category_service = CategoryService(db)

    categories = category_service.get_categories(skip=skip, limit=limit)
    total = category_service.count_categories()

    return CategoryList(
        categories=[CategoryPublic.model_validate(cat) for cat in categories],
        total=total,
    )


@category_router.get("/stats", response_model=list[CategoryWithStats])
def get_categories_with_stats(
    admin: UserPublic = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> list[CategoryWithStats]:
    """Get categories with post count statistics. Admin only."""
    category_service = CategoryService(db)

    categories_stats = category_service.get_categories_with_stats()

    return [CategoryWithStats.model_validate(cat) for cat in categories_stats]


@category_router.get("/{category_id}", response_model=CategoryPublic)
def get_category(
    category_id: int,
    admin: UserPublic = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> CategoryPublic:
    """Get a specific category by ID. Admin only."""
    category_service = CategoryService(db)

    category = category_service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    return CategoryPublic.model_validate(category)


@category_router.put("/{category_id}", response_model=CategoryPublic)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    admin: UserPublic = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> CategoryPublic:
    """Update a category. Admin only."""
    category_service = CategoryService(db)

    try:
        updated_category = category_service.update_category(
            category_id=category_id,
            name=category_data.name,
            description=category_data.description,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    if not updated_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    return CategoryPublic.model_validate(updated_category)


@category_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    admin: UserPublic = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a category. Admin only. Posts will have category set to NULL."""
    category_service = CategoryService(db)

    success = category_service.delete_category(category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
