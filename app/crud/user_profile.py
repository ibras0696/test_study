from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_profile import UserProfile
from models.user import User


async def create_profile(session: AsyncSession, user_id: int, bio: str, avatar_url: str) -> UserProfile | bool:
    us = await session.execute(select(User).where(User.id == user_id))
    if not us.scalar_one_or_none():
        print('Пользователь уже есть')
        return False

    profile = UserProfile(user_id=user_id, bio=bio, avatar_url=avatar_url)
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile
