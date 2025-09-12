from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.auth import UserPublic


# Import here to avoid circular imports
class CategoryPublic(BaseModel):
    id: int
    name: str
    description: Optional[str]


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    images: Optional[List[str]] = None
    video: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    images: Optional[List[str]] = None
    video: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None


class PostPublic(PostBase):
    id: int
    author_id: int
    author: UserPublic
    category: Optional[CategoryPublic] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PostList(BaseModel):
    posts: List[PostPublic]
    total: int
    skip: int
    limit: int
