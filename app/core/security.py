from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any
from uuid import uuid4

import bcrypt
from jose import JWTError, jwt

from config import settings


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        raise ValueError("password cannot be longer than 72 bytes")

    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > 72:
        return False

    try:
        return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))
    except ValueError:
        return False


def create_token(user_id: int, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    # JWT не шифрует payload, поэтому кладём только безопасный минимум.
    payload = {
        # ID пользователя, для которого выпущен токен.
        "sub": str(user_id),
        # access или refresh, чтобы не использовать один тип вместо другого.
        "type": token_type,
        # Кто выпустил токен.
        "iss": settings.JWT_ISSUER,
        # Для кого предназначен токен.
        "aud": settings.JWT_AUDIENCE,
        # Когда токен был выпущен.
        "iat": int(now.timestamp()),
        # Когда токен истекает.
        "exp": int(expire.timestamp()),
        # Уникальный ID токена, пригодится для revoke/blacklist.
        "jti": str(uuid4()),
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: int) -> str:
    return create_token(
        user_id=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: int) -> str:
    return create_token(
        user_id=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    # decode проверяет подпись, exp, audience и issuer.
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        audience=settings.JWT_AUDIENCE,
        issuer=settings.JWT_ISSUER,
    )

    # Access и refresh нельзя использовать вместо друг друга.
    if payload.get("type") != expected_type:
        raise JWTError("invalid token type")

    return payload


def hash_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()
