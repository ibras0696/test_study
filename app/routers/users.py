from fastapi import APIRouter, HTTPException, Header, Cookie
from starlette import status
router = APIRouter(prefix="/users", tags=["users"])
from schemas.users import UserCreate,UserEmail,UserName
from core.db import DB_DEPS
from repo.users import RepoUser
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
async def get_users(session:DB_DEPS):
    repo=RepoUser(session=session)
    result=repo.get_users()

    return result
    
    


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(user_id: int,session: DB_DEPS):
    repo=RepoUser(session=session)
    user=repo.get_user_by_id(id=user_id)

    return user

    


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(payload:UserCreate,session: DB_DEPS):
    repo=RepoUser(session=session)

    user=await repo.user_create(
        name=payload.name,email=payload.email,
        hashed_password=payload.password)
    
    await session.commit()
    return {"status":"ок","user_id":user.id}



@router.patch("/{user_id}/name", status_code=status.HTTP_200_OK)
async def update_user_name(user_id: int, payload: UserName,session:DB_DEPS):
    repo=RepoUser(session=session)

    user=await repo.update_name(
        id=user_id,
        new_name=payload.name)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found")
    
    await session.commit()

    return {"status":"ok","user_id":user.id}

    


 
@router.patch("/{user_id}", status_code=status.HTTP_200_OK)
async def update_user_email(user_id: int, payload: UserEmail,session:DB_DEPS):
    repo=RepoUser(session=session)

    user=await repo.update_email(
        id=user_id,
        new_email=payload.email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            ,detail="user not found",
                )
    

    await session.commit()

    return {"status":"ok","usr_id":user.id}






@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int,session:DB_DEPS):
    repo=RepoUser(session=session)

    fuckin_del=await repo.user_delete(id=user_id)
    if not fuckin_del:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found")
    
    
    await session.commit()









