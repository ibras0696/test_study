from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


async def create_user(
        session: AsyncSession,
        username: str,
        email: str,
        full_name: str | None = None,
        age: int | None = None,
) -> User:
    """
    Создает пользователя.
    """
    # Проверка существования username или email
    existing_user = await session.execute(
        select(User).where(
            (User.username == username) | (User.email == email)
        )
    )
    user = existing_user.scalar_one_or_none()
    if user is not None:
        return user

    user = User(
        username=username,
        email=email,
        full_name=full_name,
        age=age,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user_by_id(
        session: AsyncSession,
        user_id: int,
) -> User | None:
    """
    Возвращает пользователя по ID.
    """
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_username(
        session: AsyncSession,
        username: str,
) -> User | None:
    """
    Возвращает пользователя по username.
    """
    result = await session.execute(
        select(User).where(User.username == username)
    )
    return result.scalar_one_or_none()


async def get_all_users(session: AsyncSession) -> list[User]:
    """
    Возвращает всех пользователей.
    """
    result = await session.execute(
        select(User).order_by(User.id)
    )
    return list(result.scalars().all())


async def update_user_email(
        session: AsyncSession,
        user_id: int,
        new_email: str,
) -> User | None:
    """
    Обновляет email пользователя ORM-способом.
    """
    user = await get_user_by_id(session, user_id)
    if user is None:
        return None

    user.email = new_email
    await session.commit()
    await session.refresh(user)
    return user


async def update_user_age_via_sql(
        session: AsyncSession,
        user_id: int,
        new_age: int,
) -> None:
    """
    Обновляет age через SQLAlchemy update().
    """
    await session.execute(
        update(User)
        .where(User.id == user_id)
        .values(age=new_age)
    )
    await session.commit()


async def delete_user(
        session: AsyncSession,
        user_id: int,
) -> bool:
    """
    Удаляет пользователя ORM-способом.
    """
    user = await get_user_by_id(session, user_id)
    if user is None:
        return False

    await session.delete(user)
    await session.commit()
    return True


async def delete_user_via_sql(
        session: AsyncSession,
        user_id: int,
) -> None:
    """
    Удаляет пользователя через delete().
    """
    await session.execute(
        delete(User).where(User.id == user_id)
    )
    await session.commit()
