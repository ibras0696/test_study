from fastapi import APIRouter, HTTPException, Header, Cookie
from starlette import status

router = APIRouter(prefix="/users", tags=["users"])


# Получить всех пользователей

# Получить пользователя по айди

# Добвить пользователя

# Обновить даныне пользователя

# Удалить пользователя


# @router.get("/user/{id}", status_code=status.HTTP_200_OK)
# async def get_id(id: int) -> dict[str, int]:
#     return {'ok': id}


# @router.post("/user/{id}", status_code=status.HTTP_201_CREATED)
# async def get_id(id: int) -> dict[str, int]:
#     return {'ok': id}


# @router.get("/me", status_code=status.HTTP_200_OK)
# async def me(user_agent: str | None = Header(default=None)):
#     return {"user_agent": user_agent}

# @router.get("/session")
# async def session(session_id: str | None = Cookie(default=None)):
#     return {"session_id": session_id}