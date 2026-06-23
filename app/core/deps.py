from typing import Annotated

from fastapi import Cookie, Depends, HTTPException
from jose import JWTError
from starlette import status

from sqlalchemy.ext.asyncio import AsyncSession

from core.auth_cookies import ACCESS_COOKIE_NAME
from core.db import get_db
from core.models.user import User
from core.security import decode_token
from repo.auth import AuthRepo
from repo.posts import PostRepo
from repo.users import UserRepo
from services.auth import AuthService
from services.posts import PostService
from services.users import UserServise

DB_DEPS = Annotated[AsyncSession, Depends(get_db)]


def get_post_service(session: AsyncSession = Depends(get_db)) -> PostService:
    return PostService(PostRepo(session))


def get_user_service(session: AsyncSession = Depends(get_db)) -> UserServise:
    return UserServise(UserRepo(session))


def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepo(session), AuthRepo(session))


async def get_current_user(
    access_token: str | None = Cookie(default=None, alias=ACCESS_COOKIE_NAME),
    session: AsyncSession = Depends(get_db),
) -> User:
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="access token missing",
        )

    try:
        payload = decode_token(access_token, expected_type="access")
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid access token",
        )

    user = await UserRepo(session).get_user_by_id(id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user not found",
        )

    return user
