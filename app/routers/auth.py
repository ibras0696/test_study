from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from jose import JWTError
from starlette import status

from core.auth_cookies import clear_auth_cookies, set_auth_cookies
from core.deps import get_auth_service, get_current_user
from core.security import decode_token
from core.models.user import User
from schemas.auth import AuthStatus, LoginRequest, RegisterRequest
from schemas.users import UserRead
from services.auth import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> UserRead:
    try:
        return await service.register(
            name=payload.name,
            email=payload.email,
            password=payload.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post("/login", response_model=AuthStatus)
async def login(
    payload: LoginRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> AuthStatus:
    try:
        tokens = await service.login(email=payload.email, password=payload.password)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid email or password",
        )

    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)

    return AuthStatus(status="ok")


@router.post("/refresh", response_model=AuthStatus)
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    service: AuthService = Depends(get_auth_service),
) -> AuthStatus:
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="refresh token missing",
        )

    try:
        payload = decode_token(refresh_token, expected_type="refresh")
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid refresh token",
        )

    try:
        tokens = await service.refresh(user_id=user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user not found",
        )

    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)

    return AuthStatus(status="ok")


@router.post("/logout", response_model=AuthStatus)
async def logout(response: Response) -> AuthStatus:
    clear_auth_cookies(response)
    return AuthStatus(status="ok")


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return current_user
