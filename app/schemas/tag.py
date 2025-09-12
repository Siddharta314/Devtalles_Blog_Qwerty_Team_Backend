from datetime import datetime
from pydantic import BaseModel, Field


class TagBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    pass


class TagPublic(TagBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TagWithStats(TagPublic):
    posts_count: int


class TagList(BaseModel):
    tags: list[TagPublic]
    total: int


class PopularTag(BaseModel):
    id: int
    name: str
    posts_count: int
