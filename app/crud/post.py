from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.post import Post


async def create_user_posts(session: AsyncSession, author_id: int, title: str, content: str):
    post = Post(
        title=title,
        author_id=author_id,
        content=content
    )
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post


async def get_post_by_id(session: AsyncSession, post_id: int) -> Post | None:
    result = await session.execute(select(Post).where(Post.id == post_id))

    return result.scalar_one_or_none()


async def update_content_user(session: AsyncSession, new_content: str, post_id) -> Post | None:
    post = await get_post_by_id(session, post_id)
    if post is None:
        return None

    post.content = new_content
    await session.commit()
    await session.refresh(post)
    return post


async def post_delete(session: AsyncSession, post_id: int) -> None:
    await session.execute(delete(Post).where(Post.id == post_id))
    await session.commit()
