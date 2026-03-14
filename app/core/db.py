from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from app.core.models import Base

DATABASE_URL = "sqlite+aiosqlite:///./data.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession
)


async def get_session() -> AsyncSession:
    """
        Создает и возвращает AsyncSession.

        В реальном приложении часто используется как dependency/provider.
    """
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """
    Создает все таблицы из metadata.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)