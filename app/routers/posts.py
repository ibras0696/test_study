from fastapi import APIRouter
from starlette import status

from schemas.posts import PostCreate, PostRead, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


# Получить все посты
@router.get("/", status_code=status.HTTP_200_OK, response_model=list[PostRead])
async def get_posts() -> list[PostRead]:
    pass


# Получить все посты одного пользователя
@router.get(
    "/user/{user_id}", status_code=status.HTTP_200_OK, response_model=list[PostRead]
)
async def get_posts_by_user(user_id: int) -> list[PostRead]:
    pass


# Получить пост по айди определенного пользователя
@router.get("/{post_id}", status_code=status.HTTP_200_OK, response_model=PostRead)
async def get_post(post_id: int) -> PostRead:
    pass


# Добавить пост
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostRead)
async def create_post(payload: PostCreate) -> PostRead:
    pass


# Обновить пост данные
@router.patch("/{post_id}", status_code=status.HTTP_200_OK, response_model=PostRead)
async def update_post(post_id: int, payload: PostUpdate):
    pass


# Удалить пост
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def post_delete(post_id: int):
    pass
