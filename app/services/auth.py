from dataclasses import dataclass
from datetime import datetime, timezone

from jose import JWTError

from core.models.user import User
from core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from repo.auth import AuthRepo
from repo.users import UserRepo


@dataclass(frozen=True)
class AuthTokens:
    access_token: str
    refresh_token: str


class AuthService:
    def __init__(self, user_repo: UserRepo, auth_repo: AuthRepo):
        self.user_repo = user_repo
        self.auth_repo = auth_repo

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

        tokens = await self._create_tokens(user_id=user.id)
        await self.user_repo.session.commit()
        return tokens

    async def refresh(self, refresh_token: str) -> AuthTokens:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
            user_id = int(payload["sub"])
        except (JWTError, KeyError, ValueError):
            raise ValueError("invalid refresh token")

        saved_refresh_token = await self.auth_repo.get_active_refresh_token(refresh_token)
        if saved_refresh_token is None:
            raise ValueError("invalid refresh token")

        user = await self.user_repo.get_user_by_id(id=user_id)
        if user is None:
            raise ValueError("user not found")

        await self.auth_repo.revoke_refresh_token(saved_refresh_token)
        tokens = await self._create_tokens(user_id=user.id)
        await self.user_repo.session.commit()
        return tokens

    async def logout(self, refresh_token: str | None) -> None:
        if refresh_token is None:
            return

        saved_refresh_token = await self.auth_repo.get_active_refresh_token(refresh_token)
        if saved_refresh_token is None:
            return

        await self.auth_repo.revoke_refresh_token(saved_refresh_token)
        await self.user_repo.session.commit()

    async def _create_tokens(self, user_id: int) -> AuthTokens:
        access_token = create_access_token(user_id=user_id)
        refresh_token = create_refresh_token(user_id=user_id)
        refresh_payload = decode_token(refresh_token, expected_type="refresh")

        await self.auth_repo.create_refresh_token(
            user_id=user_id,
            token=refresh_token,
            jti=refresh_payload["jti"],
            expires_at=datetime.fromtimestamp(
                int(refresh_payload["exp"]),
                tz=timezone.utc,
            ),
        )

        return AuthTokens(
            access_token=access_token,
            refresh_token=refresh_token,
        )
