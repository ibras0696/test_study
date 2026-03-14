Да. Ниже — **базовая, но уже правильная** настройка **SQLAlchemy 2.x async + SQLite + aiosqlite** со структурой проекта, моделями через `Mapped[...]`, созданием таблиц и полным CRUD с рабочими примерами.

SQLAlchemy для async использует `create_async_engine()` и `AsyncSession`/`async_sessionmaker`, а модели в 2.x-стиле рекомендуется описывать через `Mapped[...]` и `mapped_column()`. `mapped_column()` принимает обычные аргументы `Column`, плюс ORM-специфичные параметры. Также `AsyncSession` нельзя шарить между параллельными задачами: одна сессия = одна единица работы/транзакция. ([docs.sqlalchemy.org][1])

---

# 1. Что ставить

```bash
pip install "sqlalchemy>=2.0" aiosqlite
```

SQLite для async-подключения используется через URL вида `sqlite+aiosqlite:///...`. SQLAlchemy поддерживает async dialect для `aiosqlite`. ([docs.sqlalchemy.org][1])

---

# 2. Структура проекта

Я дам **минимально нормальную** структуру, не хаос в одном файле:

```tree
app/
├── core/
│   ├── db.py
│   └── models.py
├── models/
│   ├── user.py
│   └── post.py
├── crud/
│   ├── user.py
│   └── post.py
├── schemas/
│   └── notes.txt
└── main.py
```

Для учебного старта можно и проще, но уже с разделением:

* `core/db.py` — engine, sessionmaker, init_db
* `core/models.py` — Base
* `models/` — ORM-модели
* `crud/` — запросы к БД
* `main.py` — запуск сценария

---

# 3. Базовое подключение

## `app/core/models.py`

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей."""
    pass
```

`DeclarativeBase` — рекомендуемый современный способ задать базу для declarative ORM-моделей. ([docs.sqlalchemy.org][2])

---

## `app/core/db.py`

```python
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.models import Base

DATABASE_URL = "sqlite+aiosqlite:///./app.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Показывать SQL в консоли
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
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
```

Почему так:

* `create_async_engine(...)` — async engine
* `async_sessionmaker(...)` — фабрика async-сессий
* `expire_on_commit=False` — после `commit()` объект не “протухает”, и ты можешь читать его поля без лишнего рефреша в типичном CRUD-сценарии
* `Base.metadata.create_all` вызывается через `run_sync(...)`, потому что metadata-операции синхронные по своей природе, а SQLAlchemy оборачивает их корректно в async flow ([docs.sqlalchemy.org][1])

---

# 4. Модели: типы данных, параметры колонок, Mapped

Сначала покажу **все базовые вещи на реальных моделях**.

## `app/models/user.py`

```python
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base


class User(Base):
    """Пользователь системы."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    full_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    age: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    posts: Mapped[list["Post"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username!r})"
```

---

## `app/models/post.py`

```python
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base


class Post(Base):
    """Пост пользователя."""

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    views: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    published: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    author: Mapped["User"] = relationship(
        back_populates="posts",
    )

    def __repr__(self) -> str:
        return f"Post(id={self.id}, title={self.title!r})"
```

---

## Импорт моделей в одном месте

Чтобы `create_all()` увидел все таблицы, модели должны быть импортированы до вызова `init_db()`.

Можно сделать так в `app/models/__init__.py`:

```python
from app.models.post import Post
from app.models.user import User

__all__ = ("User", "Post")
```

---

# 5. Что такое `Mapped[...]` и `mapped_column(...)`

Это современный typed ORM-стиль SQLAlchemy 2.x. Именно он сейчас является нормальным базовым стилем для declarative ORM. ([docs.sqlalchemy.org][3])

Примеры:

```python
id: Mapped[int]
name: Mapped[str]
age: Mapped[int | None]
```

Это означает:

* `Mapped[int]` — ORM-атрибут, который на Python-уровне будет `int`
* `Mapped[str]` — строка
* `Mapped[Optional[int]]` / `Mapped[int | None]` — nullable-поле

---

# 6. Основные типы данных

Вот базовые типы, которые ты чаще всего будешь использовать:

```python
from sqlalchemy import (
    Integer,
    String,
    Text,
    Boolean,
    Float,
    Numeric,
    Date,
    DateTime,
    Time,
    LargeBinary,
    ForeignKey,
)
```

Примеры:

```python
age: Mapped[int] = mapped_column(Integer)
name: Mapped[str] = mapped_column(String(100))
description: Mapped[str] = mapped_column(Text)
is_active: Mapped[bool] = mapped_column(Boolean, default=True)
price: Mapped[float] = mapped_column(Float)
created_at: Mapped[datetime] = mapped_column(DateTime)
user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
```

Типы колонок и декларативная конфигурация через `mapped_column()` официально описаны в ORM Declarative/Table Configuration и Mapping Table Columns. ([docs.sqlalchemy.org][3])

---

# 7. Основные параметры `mapped_column(...)`

Вот самые важные параметры, которые реально надо знать:

```python
mapped_column(
    Integer,                 # тип
    primary_key=True,        # первичный ключ
    autoincrement=True,      # автоинкремент
    nullable=False,          # NOT NULL
    unique=True,             # UNIQUE
    index=True,              # индекс
    default=0,               # Python-side default
    server_default="0",      # DB-side default
)
```

Практический разбор:

```python
id: Mapped[int] = mapped_column(primary_key=True)
```

* первичный ключ

```python
email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
```

* уникальный email
* нельзя `NULL`

```python
is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
```

* если ты создашь объект без `is_active`, по умолчанию будет `True`

```python
created_at: Mapped[datetime] = mapped_column(
    DateTime,
    server_default=func.now(),
    nullable=False,
)
```

* значение выставит сама БД при вставке

```python
author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
```

* внешний ключ на `users.id`

`mapped_column()` принимает аргументы `Column`, а имя колонки обычно можно не указывать явно — оно берется из имени атрибута класса. ([docs.sqlalchemy.org][3])

---

# 8. Создание таблиц

## `app/main.py`

```python
import asyncio

from app.core.db import init_db
import app.models  # Важно: импортируем модели, чтобы metadata их увидела


async def main() -> None:
    await init_db()
    print("Таблицы созданы.")


if __name__ == "__main__":
    asyncio.run(main())
```

Запуск:

```bash
python -m app.main
```

Это создаст файл `app.db` и таблицы `users`, `posts`.

---

# 9. CRUD для User

## `app/crud/user.py`

```python
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


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
```

`select()`, `update()`, `delete()`, `session.execute()`, `scalars()`, `scalar_one_or_none()` — это стандартный 2.x-стиль работы через ORM/Core API. ([docs.sqlalchemy.org][1])

---

# 10. CRUD для Post

## `app/crud/post.py`

```python
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.post import Post


async def create_post(
    session: AsyncSession,
    title: str,
    content: str,
    author_id: int,
    published: bool = False,
) -> Post:
    """
    Создает пост.
    """
    post = Post(
        title=title,
        content=content,
        author_id=author_id,
        published=published,
    )
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post


async def get_post_by_id(
    session: AsyncSession,
    post_id: int,
) -> Post | None:
    """
    Возвращает пост по ID.
    """
    result = await session.execute(
        select(Post).where(Post.id == post_id)
    )
    return result.scalar_one_or_none()


async def get_posts_with_authors(
    session: AsyncSession,
) -> list[Post]:
    """
    Возвращает посты вместе с авторами.
    """
    result = await session.execute(
        select(Post)
        .options(selectinload(Post.author))
        .order_by(Post.id)
    )
    return list(result.scalars().all())


async def increment_post_views(
    session: AsyncSession,
    post_id: int,
) -> None:
    """
    Увеличивает счетчик просмотров.
    """
    await session.execute(
        update(Post)
        .where(Post.id == post_id)
        .values(views=Post.views + 1)
    )
    await session.commit()


async def publish_post(
    session: AsyncSession,
    post_id: int,
) -> Post | None:
    """
    Публикует пост.
    """
    post = await get_post_by_id(session, post_id)
    if post is None:
        return None

    post.published = True
    await session.commit()
    await session.refresh(post)
    return post
```

Для работы со связанными объектами SQLAlchemy рекомендует использовать relationship и такие стратегии загрузки, как `selectinload`, когда нужно подгружать связи явно и предсказуемо. ([docs.sqlalchemy.org][4])

---

# 11. Реальный сценарий использования

Теперь покажу, как это реально запускается.

## `app/main.py`

```python
import asyncio

import app.models  # noqa: F401
from app.core.db import AsyncSessionLocal, init_db
from app.crud.post import (
    create_post,
    get_post_by_id,
    get_posts_with_authors,
    increment_post_views,
    publish_post,
)
from app.crud.user import (
    create_user,
    delete_user,
    get_all_users,
    get_user_by_id,
    get_user_by_username,
    update_user_age_via_sql,
    update_user_email,
)


async def demo_users() -> None:
    """
    Демонстрация CRUD для пользователей.
    """
    async with AsyncSessionLocal() as session:
        user1 = await create_user(
            session=session,
            username="ibra",
            email="ibra@example.com",
            full_name="Ibragim",
            age=23,
        )
        print("Создан user1:", user1)

        user2 = await create_user(
            session=session,
            username="amir",
            email="amir@example.com",
            full_name="Amirkhan",
            age=25,
        )
        print("Создан user2:", user2)

        found_by_id = await get_user_by_id(session, user1.id)
        print("Поиск по id:", found_by_id)

        found_by_username = await get_user_by_username(session, "amir")
        print("Поиск по username:", found_by_username)

        all_users = await get_all_users(session)
        print("Все пользователи:", all_users)

        updated_user = await update_user_email(
            session=session,
            user_id=user1.id,
            new_email="new_ibra@example.com",
        )
        print("Email обновлен:", updated_user)

        await update_user_age_via_sql(
            session=session,
            user_id=user2.id,
            new_age=30,
        )
        refreshed_user2 = await get_user_by_id(session, user2.id)
        print("Age обновлен через update():", refreshed_user2)

        deleted = await delete_user(session, user2.id)
        print("Пользователь удален:", deleted)

        remaining_users = await get_all_users(session)
        print("Остались пользователи:", remaining_users)


async def demo_posts() -> None:
    """
    Демонстрация CRUD для постов.
    """
    async with AsyncSessionLocal() as session:
        author = await get_user_by_username(session, "ibra")
        if author is None:
            print("Автор не найден.")
            return

        post1 = await create_post(
            session=session,
            title="Первый пост",
            content="Это содержимое первого поста.",
            author_id=author.id,
        )
        print("Создан post1:", post1)

        post2 = await create_post(
            session=session,
            title="Второй пост",
            content="Это содержимое второго поста.",
            author_id=author.id,
            published=True,
        )
        print("Создан post2:", post2)

        one_post = await get_post_by_id(session, post1.id)
        print("Пост по ID:", one_post)

        await increment_post_views(session, post1.id)
        await increment_post_views(session, post1.id)
        updated_post = await get_post_by_id(session, post1.id)
        print("Просмотры после увеличения:", updated_post)

        published_post = await publish_post(session, post1.id)
        print("Пост опубликован:", published_post)

        posts = await get_posts_with_authors(session)
        for post in posts:
            print(
                f"Post id={post.id}, title={post.title}, "
                f"author={post.author.username}, published={post.published}, views={post.views}"
            )


async def main() -> None:
    """
    Точка входа.
    """
    await init_db()

    print("\n=== USERS DEMO ===")
    await demo_users()

    print("\n=== POSTS DEMO ===")
    await demo_posts()


if __name__ == "__main__":
    asyncio.run(main())
```

---

# 12. Какие CRUD-операции ты здесь уже увидел

По факту здесь уже показаны основные запросы, которые нужны на старте:

## Create

```python
session.add(obj)
await session.commit()
await session.refresh(obj)
```

## Read one

```python
result = await session.execute(select(User).where(User.id == user_id))
user = result.scalar_one_or_none()
```

## Read many

```python
result = await session.execute(select(User).order_by(User.id))
users = result.scalars().all()
```

## Update через ORM

```python
user.email = "new@example.com"
await session.commit()
await session.refresh(user)
```

## Update через SQL expression

```python
await session.execute(
    update(User).where(User.id == user_id).values(age=30)
)
await session.commit()
```

## Delete через ORM

```python
await session.delete(user)
await session.commit()
```

## Delete через SQL expression

```python
await session.execute(
    delete(User).where(User.id == user_id)
)
await session.commit()
```

Это и есть базовый боевой фундамент для SQLAlchemy 2.x. Управление транзакцией и работа через `Session/AsyncSession` — официально рекомендуемый публичный ORM API. ([docs.sqlalchemy.org][5])

---

# 13. Полезные замечания, чтобы не делать мусор

## 1) Не шарь одну `AsyncSession` между несколькими async-задачами

Плохая практика:

```python
# Нельзя так
session = AsyncSessionLocal()
await asyncio.gather(
    some_query(session),
    another_query(session),
)
```

Одна сессия = одна транзакционная единица работы. SQLAlchemy прямо предупреждает, что `Session`/`AsyncSession` — stateful объект и не должен использоваться конкурентно без аккуратной синхронизации. ([docs.sqlalchemy.org][5])

---

## 2) `create_all()` — только для учебы и локального старта

Для реального проекта потом переходишь на **Alembic**, а не живешь на `create_all()`. Это я отдельно тебе потом могу дать.

---

## 3) Для чтения связей лучше не надеяться на “магическую” lazy-загрузку

В async-коде лучше явно загружать связи через `selectinload`, иначе словишь путаницу и лишние запросы. Базовые relationship-паттерны и eager loading стратегии описаны в ORM docs. ([docs.sqlalchemy.org][4])

---

# 14. Полный минимальный набор файлов сразу

Ниже — компактный вариант, если хочешь быстро скопировать.

## `app/core/models.py`

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

## `app/core/db.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.models import Base

DATABASE_URL = "sqlite+aiosqlite:///./app.db"

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

## `app/models/user.py`

```python
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    posts: Mapped[list["Post"]] = relationship(back_populates="author")
```

## `app/models/post.py`

```python
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    published: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    author: Mapped["User"] = relationship(back_populates="posts")
```

## `app/models/__init__.py`

```python
from app.models.post import Post
from app.models.user import User
```

## `app/main.py`

```python
import asyncio

import app.models
from sqlalchemy import select

from app.core.db import AsyncSessionLocal, init_db
from app.models.user import User


async def main() -> None:
    await init_db()

    async with AsyncSessionLocal() as session:
        user = User(
            username="ibra",
            email="ibra@example.com",
            full_name="Ibragim",
            age=23,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        result = await session.execute(select(User))
        users = result.scalars().all()

        print("Users:", users)


if __name__ == "__main__":
    asyncio.run(main())
```

---

# 15. Итог

Тебе для старта надо запомнить 6 вещей:

1. `create_async_engine("sqlite+aiosqlite:///./app.db")`
2. `async_sessionmaker(...)`
3. `Base(DeclarativeBase)`
4. модели через `Mapped[...]` + `mapped_column(...)`
5. таблицы через `await conn.run_sync(Base.metadata.create_all)`
6. CRUD через `select / update / delete / session.add / commit / refresh`

Это уже не “игрушка”, а нормальная учебно-боевая база.

Следующим сообщением я могу собрать тебе **вторую часть**:
**relations 1:N, N:M, фильтрация, сортировка, pagination, joins, aggregate-запросы, exists, count, update many, delete many, transaction rollback, integrity errors** — тоже на `sqlite+aiosqlite`, в таком же стиле.

[1]: https://docs.sqlalchemy.org/en/latest/orm/extensions/asyncio.html?utm_source=chatgpt.com "Asynchronous I/O (asyncio) — SQLAlchemy 2.1 ..."
[2]: https://docs.sqlalchemy.org/en/latest/orm/mapping_styles.html?utm_source=chatgpt.com "ORM Mapped Class Overview"
[3]: https://docs.sqlalchemy.org/20/orm/declarative_tables.html?utm_source=chatgpt.com "Table Configuration with Declarative — SQLAlchemy 2.0 ..."
[4]: https://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html?utm_source=chatgpt.com "Basic Relationship Patterns"
[5]: https://docs.sqlalchemy.org/en/latest/orm/session_basics.html?utm_source=chatgpt.com "Session Basics — SQLAlchemy 2.1 Documentation"
