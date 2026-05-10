# FastAPI: Config / Settings Полный Разбор

## 0. Цель

Материал покрывает:

* Pydantic Settings;
* `.env`;
* env variables;
* secrets;
* local/dev/prod configs;
* `DEBUG`;
* `CORS_ORIGINS`;
* `DATABASE_URL`;
* `REDIS_URL`;
* `lru_cache` для settings.

---

## 1. Почему нужен отдельный слой настроек

Настройки нельзя хардкодить в коде.

Причины:

* разные окружения (local/dev/prod);
* секреты не должны жить в git;
* инфраструктура должна менять поведение без правок кода.

---

## 2. Pydantic Settings

Базовый класс:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "My API"
    DEBUG: bool = False
    DATABASE_URL: str
    REDIS_URL: str
    CORS_ORIGINS: list[str] = Field(default_factory=list)
```

---

## 3. `.env`

Пример `.env`:

```dotenv
APP_NAME=My API
DEBUG=true
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/app_db
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:5173"]
```

Важно:

* `.env` добавить в `.gitignore`;
* для команды держать `.env.example` без секретов.

---

## 4. Environment variables

Приоритет обычно у env переменных окружения (например, в Docker/K8s), а не у локального `.env`.

Пример:

```bash
export DEBUG=false
export DATABASE_URL=postgresql+asyncpg://...
```

---

## 5. Secrets

Секреты:

* `JWT_SECRET`;
* `DB_PASSWORD`;
* API keys внешних сервисов.

Правило:

1. не хранить в репозитории;
2. хранить в secret manager (Vault, AWS/GCP secrets, K8s secrets);
3. логировать только факт наличия, не значение.

Пример поля:

```python
JWT_SECRET: str
```

---

## 6. local/dev/prod configs

Подходы:

1. один класс `Settings` + разные env values;
2. базовый класс + наследники `DevSettings`, `ProdSettings`.

Практичный вариант:

* один класс и переменная `ENV`.

```python
ENV: str = "local"  # local/dev/prod
```

Можно в коде:

```python
if settings.ENV == "prod" and settings.DEBUG:
    raise RuntimeError("DEBUG must be false in prod")
```

---

## 7. `DEBUG`

`DEBUG` должен влиять на:

* уровень логов;
* dev middleware;
* диагностику ошибок.

В production:

* `DEBUG=False`;
* не отдавать внутренние stack traces клиенту.

---

## 8. `CORS_ORIGINS`

Список разрешённых origins для frontend.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Важно:

* не ставить `*` без необходимости;
* в prod перечислять конкретные домены.

---

## 9. `DATABASE_URL`

Пример async postgres:

```text
postgresql+asyncpg://user:password@host:5432/db_name
```

Использование:

```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
```

---

## 10. `REDIS_URL`

Используется для:

* кэша;
* rate limiting;
* брокера задач;
* distributed locks.

Пример:

```text
redis://localhost:6379/0
```

---

## 11. `lru_cache` для settings

Чтобы не пересоздавать `Settings` каждый раз:

```python
from functools import lru_cache


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

Плюсы:

* singleton-подобное поведение;
* быстрее;
* удобно использовать в dependencies.

---

## 12. Интеграция с Depends

```python
from fastapi import Depends, FastAPI

app = FastAPI()


@app.get("/info")
async def info(settings: Settings = Depends(get_settings)):
    return {
        "app_name": settings.APP_NAME,
        "debug": settings.DEBUG,
        "env": settings.ENV,
    }
```

---

## 13. Рекомендуемая структура

```text
app/
  core/
    settings.py
  main.py
.env
.env.example
```

`core/settings.py`:

* класс `Settings`;
* `get_settings` с `lru_cache`;
* валидация критичных флагов.

---

## 14. Частые ошибки

1. Хардкод `DATABASE_URL` в `db.py`.
2. Секреты в git.
3. Разные переменные в разных местах без централизованного `Settings`.
4. Нет `.env.example`.
5. `DEBUG=True` в prod.
6. Нет валидации конфигурации на старте.

---

## 15. Итог

Production-подход:

1. все настройки через Pydantic Settings;
2. env-only для prod;
3. секреты из secret manager;
4. `lru_cache` для единого экземпляра;
5. строгие проверки конфигурации при запуске.
