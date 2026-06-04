from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Insert, Update, Delete

from core.models import Post, User

class PostRepo:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = self.session

    async def create(
            self,
            user_id: int,
            title: str,
            body: str | None = None
            ) -> Post:
        post = Post(user_id=user_id, title=title, body=body)
        self.session.add(post)
        await self.session.flush()
        # await self.session.commit()
        return post
    
    async def get_posts(self) -> list[Post]:
        stmt = select(Post)
        posts = await self.session.execute(stmt).scalars().all()
        return posts
    
    async def get_posts_by_user(self, user_id: int) -> list[Post]:
        stmt = select(Post).where(Post.user_id == user_id)
        posts = await self.session.execute(stmt).scalars().all()
        return posts
    
    async def update_post(
            self,
            post_id: int,
            title: str | None=None,
            body: str | None=None
            ) -> Post | None:
        stmt = select(Post).where(Post.id == post_id)
        res = await self.session.execute(stmt)
        post = res.scalar_one_or_none()
        if post is None:
            return None
        
        if title is not None:
            post.title = title
        
        if body is not None:
            post.body = body

        
        await self.session.flush()
        # await self.session.commit()
        return post
    
    async def delete_post(self, post_id: int) -> bool:
        post = await self.session.get(Post, post_id)
        if post is None:
            return False
        
        await self.session.delete(post)
        return True