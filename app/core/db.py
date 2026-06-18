from typing import Annotated, AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from fastapi import Depends

from config import settings
 

DATABASE_URL = settings.DATABASE_URL
 

engine = create_async_engine(
    DATABASE_URL,
    echo=True,                                 # логировать SQL (убрать на проде)
)


AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Используй через Depends(get_db) в роутах.
    Сессия открывается и закрывается на каждый запрос.
    Commit обычно делается на уровне service.
    """
    async with AsyncSessionLocal() as session:
        yield session
