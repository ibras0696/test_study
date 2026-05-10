from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.user_profile import UserProfile
from models.post import Post


async def get_users_profiles_posts(session: AsyncSession):
    stmt = (
        select(User, UserProfile, Post)
        .join(User.profile)   # users -> user_profiles
        .join(User.posts)     # users -> posts
        
    )

    result = await session.execute(stmt)
    rows = result.all()

    data = []
    for user, profile, post in rows:
        data.append(
            {
                "user_id": user.id,
                "username": user.username,
                "profile": {
                    "id": profile.id,
                    "bio": profile.bio,
                    "avatar_url": profile.avatar_url,
                },
                "post": {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,
                },
            }
        )
    return data


