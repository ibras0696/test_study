from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from schemas.posts import PostCreate, PostRead, PostUpdate

from core.deps import get_post_service
from services.posts import PostService

router = APIRouter(prefix="/posts", tags=["posts"])


# Получить все посты
@router.get(
    "/", 
    status_code=status.HTTP_200_OK, 
    response_model=list[PostRead]
)
async def get_posts(
    service: PostService = Depends(get_post_service)) -> list[PostRead]:
    posts = await service.get_posts()
    return posts


# Получить все посты одного пользователя
@router.get(
    "/user/{user_id}", 
    status_code=status.HTTP_200_OK, 
    response_model=list[PostRead]
)
async def get_posts_by_user(
    user_id: int,
    service: PostService = Depends(get_post_service)
) -> list[PostRead]:
    posts = await service.get_posts_by_user(user_id=user_id)
    if posts is None:
        return []
    return posts


# Получить пост по айди определенного пользователя
@router.get(
    "/{post_id}", 
    status_code=status.HTTP_200_OK, 
    response_model=PostRead
)
async def get_post_by_id(
    post_id: int,
    service: PostService = Depends(get_post_service)
) -> PostRead:
    post = await service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="post not found")
    return post

# Добавить пост
@router.post(
    "/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=PostRead
)
async def create_post(
    payload: PostCreate,
    service: PostService = Depends(get_post_service)
) -> PostRead:
    post = await service.create_post(
        user_id=payload.user_id,
        title=payload.title,
        body=payload.body
        )
    return post
    


# Обновить пост данные
@router.patch("/{post_id}", status_code=status.HTTP_200_OK, response_model=PostRead)
async def update_post(post_id: int, payload: PostUpdate):
    pass


# Удалить пост
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def post_delete(post_id: int):
    pass
