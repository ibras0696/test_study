from core.models import Post

from repo.posts import PostRepo
from repo.users import UserRepo


class PostService:
    def __init__(self, repo: PostRepo):
        self.repo: PostRepo = repo
        

    async def create_post(
        self, user_id: int, title: str, body: str | None = None
    ) -> Post:
        user_repo = UserRepo(session=self.repo.session)
        user = await user_repo.get_user_by_id(user_id)
        
        if user is None:
            raise ValueError("user not found")
        
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title is empty")
        
        post = await self.repo.create(user_id=user_id, title=title, body=body)
        await self.repo.session.commit()
        return post
    
    
    async def get_post_by_id(self, post_id: int) -> Post | None:
        return await self.repo.get_post_by_id(post_id=post_id)
    
    
    async def get_posts(self) -> list[Post]:
        return await self.repo.get_posts()


    async def get_posts_by_user(self, user_id: int) -> list[Post]:
        return await self.repo.get_posts_by_user(user_id=user_id)

    async def update_post(
        self, post_id: int, title: str | None = None, body: str | None = None
    ) -> Post | None:
        if not isinstance(post_id, int):
            raise TypeError("post_id is int")
        if title is not None and not isinstance(title, str):
            raise TypeError("title is str or None")
        if body is not None and not isinstance(body, str):
            raise TypeError("body is str or None")

        post = await self.repo.update_post(post_id=post_id, title=title, body=body)
        if post is None:
            return None
        await self.repo.session.commit()
        return post

    async def delete_post(self, post_id: int) -> bool:
        if not isinstance(post_id, int):
            raise TypeError("post_id is int")
        deleted = await self.repo.delete_post(post_id=post_id)
        if not deleted:
            return False
        await self.repo.session.commit()
        return True
