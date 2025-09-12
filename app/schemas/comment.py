from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.auth import UserPublic


class CommentBase(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class CommentCreate(CommentBase):
    post_id: int


class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=2000)


class CommentPublic(CommentBase):
    id: int
    post_id: int
    author_id: int
    author: UserPublic
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CommentList(BaseModel):
    comments: List[CommentPublic]
    total: int
    skip: int
    limit: int
