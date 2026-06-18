from dataclasses import dataclass

from core.models.user import User
from core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from repo.users import UserRepo


@dataclass(frozen=True)
class AuthTokens:
    access_token: str
    refresh_token: str


class AuthService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def register(self, name: str, email: str, password: str) -> User:
        existing_user = await self.user_repo.get_user_by_email(email=email)
        if existing_user is not None:
            raise ValueError("email already registered")

        user = await self.user_repo.user_create(
            name=name,
            email=email,
            hashed_password=hash_password(password),
        )
        await self.user_repo.session.commit()
        return user

    async def login(self, email: str, password: str) -> AuthTokens:
        user = await self.user_repo.get_user_by_email(email=email)
        if user is None or not verify_password(password, user.hashed_password):
            raise ValueError("invalid email or password")

        return self._create_tokens(user_id=user.id)

    async def refresh(self, user_id: int) -> AuthTokens:
        user = await self.user_repo.get_user_by_id(id=user_id)
        if user is None:
            raise ValueError("user not found")

        return self._create_tokens(user_id=user.id)

    def _create_tokens(self, user_id: int) -> AuthTokens:
        return AuthTokens(
            access_token=create_access_token(user_id=user_id),
            refresh_token=create_refresh_token(user_id=user_id),
        )
