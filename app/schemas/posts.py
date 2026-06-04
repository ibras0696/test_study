from datetime import datetime

from pydantic import BaseModel, Field


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str | None = Field(default=None, min_length=1, max_length=200)


class PostCreate(PostBase):
    user_id: int


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    body: str | None = Field(default=None, min_length=1, max_length=200)


class PostRead(PostBase):
    post_id: int
    user_id: int
    published: bool
    created_at: datetime