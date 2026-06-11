from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from core.deps import get_user_service
from schemas.users import (
    UserCreate,
    UserEmail,
    UserName,
    UserPassword,
    UserRead,
)
from services.users import UserServise


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_users(
    service: UserServise = Depends(get_user_service),
) -> list[UserRead]:
    users = await service.get_users()
    return users


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: int,
    service: UserServise = Depends(get_user_service),
) -> UserRead | None:
    user = await service.get_user(user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )

    return user


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    service: UserServise = Depends(get_user_service),
):
    user = await service.create_user(
        name=payload.name,
        email=payload.email,
        hashed_password=payload.hashed_password,
    )

    return user


@router.patch("/{user_id}/name", status_code=status.HTTP_200_OK)
async def update_name_user(
    user_id: int,
    payload: UserName,
    service: UserServise = Depends(get_user_service),
):
    user = await service.update_name(user_id=user_id, new_name=payload.name)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )

    return user


@router.patch("/{user_id}/email", status_code=status.HTTP_200_OK)
async def update_email(
    user_id: int,
    payload: UserEmail,
    service: UserServise = Depends(get_user_service),
):
    user = await service.update_email(user_id=user_id, new_email=payload.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )

    return user


@router.patch("/{user_id}/password", status_code=status.HTTP_200_OK)
async def update_password(
    user_id: int,
    payload: UserPassword,
    service: UserServise = Depends(get_user_service),
):
    user = await service.update_password(
        user_id=user_id,
        new_password=payload.new_password,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )

    return {"status": "ok"}


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    service: UserServise = Depends(get_user_service),
):
    user = await service.user_delete(user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )

    return {"status": "ok"}
