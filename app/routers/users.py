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
#
#
# @router.post("/user/{id}", status_code=status.HTTP_201_CREATED)
# async def get_id(id: int) -> dict[str, int]:
#     return {'ok': id}
#
#
# @router.get("/me", status_code=status.HTTP_200_OK)
# async def me(user_agent: str | None = Header(default=None)):
#     return {"user_agent": user_agent}
#
# @router.get("/session")
# async def session(session_id: str | None = Cookie(default=None)):
#     return {"session_id": session_id}




@router.get("/", status_code=status.HTTP_200_OK)
async def get_users():
    pass


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(user_id: int):
    pass


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(payload: dict):
    pass


@router.patch("/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(user_id: int, payload: dict):
    pass


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    pass



@router.patch("/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(user_id: int, payload: dict, new_email):





