from typing import Annotated

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from core.db import AsyncSessionLocal, get_db
from repo.posts import PostRepo
from services.posts import PostService
from services.users import UserServise
from repo.users import RepoUser

DB_DEPS = Annotated[AsyncSessionLocal, Depends(get_db)]


def get_post_service(session: AsyncSession = Depends(get_db)) -> PostService:
    return PostService(PostRepo(session))

def get_user_service(session: AsyncSession = Depends(get_db)) -> UserServise:
    return UserServise(RepoUser)
