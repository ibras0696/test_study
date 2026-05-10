from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.user_profile import UserProfile
from models.post import Post


async def seed_test_data(session: AsyncSession) -> None:
    # user 1
    u1 = await session.scalar(select(User).where(User.username == "ibra"))
    if u1 is None:
        u1 = User(
            username="ibra",
            email="ibra@example.com",
            full_name="Ibragim A",
            age=21,
            is_active=True,
        )
        session.add(u1)
        await session.flush()

    u1_profile = await session.scalar(
        select(UserProfile).where(UserProfile.user_id == u1.id)
    )
    if u1_profile is None:
        session.add(
            UserProfile(
                user_id=u1.id,
                bio="Backend dev",
                avatar_url="https://example.com/a1.png",
            )
        )

    u1_post = await session.scalar(
        select(Post).where(Post.author_id == u1.id).limit(1)
    )
    if u1_post is None:
        session.add(
            Post(
                author_id=u1.id,
                title="First post",
                content="Hello from user 1",
                views=10,
                published=True,
            )
        )

    # user 2
    u2 = await session.scalar(select(User).where(User.username == "amir"))
    if u2 is None:
        u2 = User(
            username="amir",
            email="amir@example.com",
            full_name="Amir B",
            age=25,
            is_active=True,
        )
        session.add(u2)
        await session.flush()

    u2_profile = await session.scalar(
        select(UserProfile).where(UserProfile.user_id == u2.id)
    )
    if u2_profile is None:
        session.add(
            UserProfile(
                user_id=u2.id,
                bio="Python fan",
                avatar_url="https://example.com/a2.png",
            )
        )

    u2_post = await session.scalar(
        select(Post).where(Post.author_id == u2.id).limit(1)
    )
    if u2_post is None:
        session.add(
            Post(
                author_id=u2.id,
                title="Second post",
                content="Hello from user 2",
                views=3,
                published=False,
            )
        )

    await session.commit()
