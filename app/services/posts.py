from core.models import Post
from repo.posts import PostRepo

class PostService:

    def __init__(self, repo: PostRepo):
        self.repo: PostRepo = repo
    
    async def create_post(
            self,
            user_id: int,
            title: str,
            body: str | None=None
    ) -> Post:
        if not title.strip():
            raise ValueError("title is empty")
        post = await self.repo.create(user_id=user_id, title=title, body=body)
        await self.repo.session.commit()
        return post
    
    async def get_posts(self) -> list[Post]:
        await self.repo.g