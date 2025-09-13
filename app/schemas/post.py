from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.auth import UserPublic
from app.schemas.tag import TagPublic
from app.schemas.category import CategoryPublic


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    content: str = Field(min_length=1)
    images: Optional[List[str]] = None
    video: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None


class PostCreate(PostBase):
    tags: Optional[List[str]] = Field(None, description="List of tag names")


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    content: Optional[str] = Field(None, min_length=1)
    images: Optional[List[str]] = None
    video: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None
    tags: Optional[List[str]] = Field(None, description="List of tag names")


class PostPublic(PostBase):
    id: int
    author_id: int
    author: UserPublic
    category: Optional[CategoryPublic] = None
    tags: List[TagPublic] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PostList(BaseModel):
    posts: List[PostPublic]
    total: int
    skip: int
    limit: int
