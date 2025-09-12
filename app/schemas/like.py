from pydantic import BaseModel

from app.schemas.auth import UserPublic


class LikeCreate(BaseModel):
    post_id: int


class LikePublic(BaseModel):
    user_id: int
    post_id: int
    user: UserPublic

    model_config = {"from_attributes": True}


class LikeStats(BaseModel):
    post_id: int
    likes_count: int
    user_has_liked: bool


class PostLikesList(BaseModel):
    post_id: int
    likes_count: int
    likes: list[LikePublic]
