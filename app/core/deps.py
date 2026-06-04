from typing import Annotated

from fastapi import Depends

from core.db import AsyncSessionLocal, get_db
from repo.posts import PostRepo
from services.posts import PostService

DB_DEPS = Annotated[AsyncSessionLocal, Depends(get_db)]


def get_post_service(session: DB_DEPS) -> PostService:
    repo = PostRepo(session=session)
    return PostService(repo=repo)
