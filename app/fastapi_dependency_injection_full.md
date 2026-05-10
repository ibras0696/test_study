# FastAPI Dependency Injection: Полный Разбор

## 0. Что такое DI в FastAPI

Dependency Injection в FastAPI:

* выносит повторяющуюся логику из endpoint;
* делает код модульным;
* упрощает тестирование;
* централизует авторизацию, доступы, настройки и сессии БД.

Базовый механизм: `Depends(...)`.

---

## 1. `Depends()`

Простой пример зависимости-функции:

```python
from fastapi import Depends, FastAPI

app = FastAPI()


def get_page_size() -> int:
    return 20


@app.get("/users")
async def list_users(page_size: int = Depends(get_page_size)):
    return {"page_size": page_size}
```

---

## 2. `Annotated[..., Depends()]`

Современный и более читаемый стиль:

```python
from typing import Annotated
from fastapi import Depends


def get_limit() -> int:
    return 50


LimitDep = Annotated[int, Depends(get_limit)]


@app.get("/items")
async def items(limit: LimitDep):
    return {"limit": limit}
```

Плюс: зависимость можно переиспользовать через alias.

---

## 3. Функции как зависимости

Это основной и самый частый вариант.

```python
from fastapi import Header, HTTPException


def verify_api_key(x_api_key: str | None = Header(default=None)) -> str:
    if x_api_key != "secret-key":
        raise HTTPException(status_code=401, detail="invalid api key")
    return x_api_key


@app.get("/protected")
async def protected(_: str = Depends(verify_api_key)):
    return {"ok": True}
```

---

## 4. Классы как зависимости

Подходит для конфигурируемого поведения.

```python
from fastapi import Query


class Pagination:
    def __init__(self, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
        self.limit = limit
        self.offset = offset


@app.get("/products")
async def products(p: Pagination = Depends()):
    return {"limit": p.limit, "offset": p.offset}
```

---

## 5. Sub-dependencies

Зависимость может зависеть от другой зависимости.

```python
def get_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="missing auth header")
    return authorization


def get_current_user(token: str = Depends(get_token)) -> dict:
    # здесь может быть decode JWT
    return {"id": 1, "role": "admin"}


@app.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return user
```

---

## 6. `yield` dependencies

`yield`-зависимости нужны для ресурсов с lifecycle:

* DB session;
* подключение к брокеру;
* временные файлы;
* внешние клиенты.

```python
from collections.abc import Generator


def get_resource() -> Generator[str, None, None]:
    resource = "opened"
    try:
        yield resource
    finally:
        # cleanup
        pass
```

---

## 7. DB session dependency

Типовой пример для SQLAlchemy async:

```python
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = "sqlite+aiosqlite:///./data.db"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
```

В роуте:

```python
from typing import Annotated

DbDep = Annotated[AsyncSession, Depends(get_db)]


@app.get("/users")
async def users(db: DbDep):
    ...
```

---

## 8. Auth dependency

Отдельная зависимость для текущего пользователя:

```python
def get_current_user(token: str = Depends(get_token)) -> dict:
    # validate token + load user
    return {"id": 1, "role": "user"}
```

Плюсы:

* единый вход для auth логики;
* меньше копипаста в endpoints;
* проще менять провайдера токенов.

---

## 9. Permission dependency

Права лучше оформлять зависимостью-фабрикой.

```python
from fastapi import HTTPException


def require_role(required_role: str):
    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] != required_role:
            raise HTTPException(status_code=403, detail="forbidden")
        return user
    return checker


@app.delete("/admin/users/{user_id}")
async def admin_delete_user(
    user_id: int,
    _: dict = Depends(require_role("admin")),
):
    return {"deleted": user_id}
```

---

## 10. Settings dependency

Настройки через Pydantic Settings и зависимость.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    app_name: str = "My API"
    debug: bool = False
    jwt_secret: str


def get_settings() -> Settings:
    return Settings()
```

Использование:

```python
@app.get("/info")
async def info(settings: Settings = Depends(get_settings)):
    return {"app_name": settings.app_name, "debug": settings.debug}
```

---

## 11. `dependency_overrides` для тестов

Позволяет подменять зависимости в тестах:

```python
from fastapi.testclient import TestClient


def override_get_current_user():
    return {"id": 999, "role": "admin"}


app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)
response = client.get("/me")
assert response.status_code == 200
assert response.json()["id"] == 999

app.dependency_overrides.clear()
```

Это ключевой механизм для:

* unit/integration тестов;
* отключения внешних сервисов;
* стабилизации тестового окружения.

---

## 12. Практический mini-stack

Ниже короткая схема, как обычно строят DI-слой:

1. `get_settings` -> конфиг;
2. `get_db` -> сессия БД;
3. `get_token` -> токен из header;
4. `get_current_user` -> пользователь;
5. `require_role("admin")` -> проверка прав;
6. endpoint вызывает сервис.

---

## 13. Антипаттерны

1. Писать auth/permission логику в каждом endpoint.
2. Создавать DB session вручную в каждом роуте.
3. Не использовать `yield` для lifecycle-ресурсов.
4. Смешивать зависимости API-слоя и бизнес-логики без границ.
5. Не чистить `dependency_overrides` после теста.

---

## 14. Итог

Dependency Injection в FastAPI:

* уменьшает дублирование;
* делает архитектуру модульной;
* обеспечивает строгий контроль доступа;
* сильно упрощает тестирование через overrides.

Минимум для production:

1. `get_db` (yield);
2. `get_current_user`;
3. `require_role`;
4. `get_settings`;
5. `dependency_overrides` в тестах.
