# FastAPI на Python 3.12 — начало курса

## 0. Цель материала

Этот материал — старт полноценного модуля по **FastAPI**.

Мы будем изучать FastAPI не как “быстро сделать роут”, а как **backend-фреймворк для production API**:

* HTTP API;
* типизация;
* валидация данных;
* Pydantic v2;
* структура проекта;
* зависимости;
* работа с БД;
* авторизация;
* тесты;
* Docker;
* деплой.

FastAPI — современный Python web framework для построения API на основе стандартных Python type hints. Это не “магия”, а тонкая связка:

```text
Python type hints
        ↓
FastAPI
        ↓
Pydantic validation
        ↓
OpenAPI документация
        ↓
HTTP API
```

FastAPI официально строится вокруг path operations, автоматической документации и type hints. ([fastapi.tiangolo.com][1])

---

# 1. Что такое FastAPI

**FastAPI** — это фреймворк для создания HTTP API на Python.

Пример API:

```http
GET /users/1
POST /users
PATCH /users/1
DELETE /users/1
```

FastAPI нужен, когда backend должен:

* принимать HTTP-запросы;
* валидировать входные данные;
* отдавать JSON;
* работать с БД;
* иметь Swagger/OpenAPI документацию;
* быть удобным для async-кода;
* нормально тестироваться.

---

## 1.1. Главное отличие FastAPI от “просто Flask/Django”

FastAPI сильно опирается на **типизацию Python**.

Например:

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
```

Здесь `user_id: int` — это не просто подсказка для разработчика.

FastAPI использует это для:

* преобразования данных;
* валидации;
* генерации документации;
* описания OpenAPI схемы.

Path-параметры в FastAPI объявляются через синтаксис `{parameter}` в URL и передаются в функцию как аргументы. ([fastapi.tiangolo.com][2])

---

# 2. Что нужно знать до FastAPI

Минимальная база:

```text
Python:
- функции
- async / await
- классы
- type hints
- virtualenv / venv
- pip / uv

HTTP:
- GET / POST / PUT / PATCH / DELETE
- status codes
- JSON
- headers
- query params
- path params

Backend:
- request / response
- validation
- database
- service layer
```

Если async пока слабый — не критично. Но надо понимать:

```python
async def handler():
    ...
```

FastAPI поддерживает `async def` для path operation functions и отдельно объясняет разницу между concurrency, parallelism и async/await. ([fastapi.tiangolo.com][3])

---

# 3. Установка проекта на Python 3.12

## 3.1. Создаём папку

```bash
mkdir fastapi_course
cd fastapi_course
```

## 3.2. Создаём виртуальное окружение

```bash
python3.12 -m venv .venv
```

Активируем:

### Linux / macOS

```bash
source .venv/bin/activate
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

---

## 3.3. Устанавливаем зависимости

```bash
pip install fastapi "uvicorn[standard]"
```

`uvicorn[standard]` ставит Uvicorn с дополнительными production-полезными зависимостями, включая оптимизированные компоненты там, где они доступны. ([PyPI][4])

Проверяем:

```bash
python --version
pip freeze
```

Ожидаемо:

```text
Python 3.12.x
fastapi==...
uvicorn==...
pydantic==...
```

FastAPI использует Pydantic для валидации данных, а актуальная ветка Pydantic v2 является основной современной веткой. Pydantic v2 — существенная переработка по сравнению с v1. ([PyPI][5])

---

# 4. Первый FastAPI-файл

Создай файл:

```bash
touch main.py
```

Код:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root() -> dict[str, str]:
    """Корневой endpoint приложения."""
    return {"message": "FastAPI работает"}
```

Запуск:

```bash
uvicorn main:app --reload
```

Открой в браузере:

```text
http://127.0.0.1:8000
```

Ответ:

```json
{
  "message": "FastAPI работает"
}
```

---

# 5. Разбор строки запуска

```bash
uvicorn main:app --reload
```

Разбираем:

```text
uvicorn       → ASGI-сервер
main          → файл main.py
app           → объект FastAPI внутри main.py
--reload      → автоперезапуск при изменении кода
```

Важно:

```bash
uvicorn main:app --reload
```

означает:

```python
# main.py
app = FastAPI()
```

Если файл называется `src/app.py`, запуск будет другой:

```bash
uvicorn src.app:app --reload
```

---

# 6. Что такое `app = FastAPI()`

```python
app = FastAPI()
```

Это главный объект приложения.

Через него регистрируются:

* routes;
* middleware;
* exception handlers;
* dependencies;
* startup/shutdown logic;
* metadata проекта;
* OpenAPI документация.

Пример с metadata:

```python
from fastapi import FastAPI

app = FastAPI(
    title="FastAPI Course API",
    description="Учебный API на FastAPI и Python 3.12",
    version="0.1.0",
)
```

---

# 7. Что такое route / endpoint / path operation

В FastAPI часто используется термин **path operation**.

Пример:

```python
@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
```

Разбор:

```text
@app.get("/health")     → decorator
GET                     → HTTP method
/health                 → path
health_check            → handler function
return {...}            → response body
```

FastAPI path operation состоит из пути, HTTP-операции и функции, которая обрабатывает запрос. ([fastapi.tiangolo.com][1])

---

# 8. Добавим несколько endpoint’ов

```python
from fastapi import FastAPI

app = FastAPI(
    title="FastAPI Course API",
    version="0.1.0",
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "FastAPI работает"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version")
async def get_version() -> dict[str, str]:
    return {"version": "0.1.0"}
```

Теперь доступны:

```text
GET /
GET /health
GET /version
```

---

# 9. Автоматическая документация

FastAPI автоматически генерирует документацию.

Открой:

```text
http://127.0.0.1:8000/docs
```

Это Swagger UI.

Ещё есть:

```text
http://127.0.0.1:8000/redoc
```

И OpenAPI JSON:

```text
http://127.0.0.1:8000/openapi.json
```

FastAPI генерирует OpenAPI metadata для path operations, включая параметры, request body, responses и другие элементы спецификации. ([fastapi.tiangolo.com][6])

---

# 10. Path parameters

Path parameter — это переменная внутри URL.

Пример:

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int) -> dict[str, int]:
    return {"user_id": user_id}
```

Запрос:

```http
GET /users/10
```

Ответ:

```json
{
  "user_id": 10
}
```

Если открыть:

```http
GET /users/abc
```

FastAPI вернёт ошибку валидации, потому что `user_id` должен быть `int`.

---

## Почему это важно

Ты не пишешь вручную:

```python
try:
    user_id = int(user_id)
except ValueError:
    ...
```

FastAPI делает это через type hints и Pydantic.

---

# 11. Query parameters

Query parameters идут после `?`.

Пример:

```http
GET /users?limit=10&offset=0
```

Код:

```python
@app.get("/users")
async def list_users(
    limit: int = 10,
    offset: int = 0,
) -> dict[str, int]:
    return {
        "limit": limit,
        "offset": offset,
    }
```

Запрос:

```http
GET /users?limit=20&offset=40
```

Ответ:

```json
{
  "limit": 20,
  "offset": 40
}
```

---

# 12. Path parameters vs Query parameters

| Вид параметра   | Где находится | Пример            | Когда использовать        |
| --------------- | ------------- | ----------------- | ------------------------- |
| Path parameter  | В URL path    | `/users/10`       | Когда ресурс конкретный   |
| Query parameter | После `?`     | `/users?limit=10` | Фильтры, пагинация, поиск |

Пример правильного API:

```text
GET /users/10
GET /users?limit=10&offset=0
GET /users?search=ali
```

Плохой стиль:

```text
GET /get-user?id=10
GET /users/get/10
```

---

# 13. Request body

Для `POST`, `PUT`, `PATCH` обычно нужен body.

Пример JSON:

```json
{
  "username": "ibragim",
  "email": "ibragim@example.com",
  "age": 25
}
```

FastAPI работает с body через Pydantic-модели.

```python
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    age: int
```

Endpoint:

```python
@app.post("/users")
async def create_user(user_data: UserCreate) -> dict[str, str | int]:
    return {
        "username": user_data.username,
        "email": user_data.email,
        "age": user_data.age,
    }
```

Полный код:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="FastAPI Course API",
    version="0.1.0",
)


class UserCreate(BaseModel):
    username: str
    email: str
    age: int


@app.post("/users")
async def create_user(user_data: UserCreate) -> dict[str, str | int]:
    return {
        "username": user_data.username,
        "email": user_data.email,
        "age": user_data.age,
    }
```

---

# 14. Что здесь делает Pydantic

Pydantic проверяет:

```python
class UserCreate(BaseModel):
    username: str
    email: str
    age: int
```

То есть входной JSON должен соответствовать схеме:

```json
{
  "username": "string",
  "email": "string",
  "age": 123
}
```

Если передать:

```json
{
  "username": "ibragim",
  "email": "ibragim@example.com",
  "age": "wrong"
}
```

FastAPI вернёт ошибку валидации.

Pydantic использует Python-типы для валидации и сериализации данных. ([pydantic.dev][7])

---

# 15. Response model

Сейчас endpoint возвращает словарь:

```python
@app.post("/users")
async def create_user(user_data: UserCreate) -> dict[str, str | int]:
    ...
```

Но в нормальном API лучше явно описывать ответ.

```python
class UserRead(BaseModel):
    id: int
    username: str
    email: str
    age: int
```

Endpoint:

```python
@app.post("/users", response_model=UserRead)
async def create_user(user_data: UserCreate) -> UserRead:
    return UserRead(
        id=1,
        username=user_data.username,
        email=user_data.email,
        age=user_data.age,
    )
```

Зачем `response_model`:

* фиксирует контракт ответа;
* чистит лишние поля;
* улучшает OpenAPI документацию;
* помогает frontend-разработчику;
* снижает риск случайно отдать лишние данные.

---

# 16. Полный стартовый пример

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="FastAPI Course API",
    description="Учебный API на FastAPI и Python 3.12",
    version="0.1.0",
)


class UserCreate(BaseModel):
    username: str
    email: str
    age: int


class UserRead(BaseModel):
    id: int
    username: str
    email: str
    age: int


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "FastAPI работает"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/users/{user_id}", response_model=UserRead)
async def get_user(user_id: int) -> UserRead:
    return UserRead(
        id=user_id,
        username="test_user",
        email="test@example.com",
        age=25,
    )


@app.get("/users")
async def list_users(
    limit: int = 10,
    offset: int = 0,
) -> dict[str, int]:
    return {
        "limit": limit,
        "offset": offset,
    }


@app.post("/users", response_model=UserRead)
async def create_user(user_data: UserCreate) -> UserRead:
    return UserRead(
        id=1,
        username=user_data.username,
        email=user_data.email,
        age=user_data.age,
    )
```

---

# 17. Проверка через Swagger

Запусти:

```bash
uvicorn main:app --reload
```

Открой:

```text
http://127.0.0.1:8000/docs
```

Проверь:

```text
GET /
GET /health
GET /users/{user_id}
GET /users
POST /users
```

Для `POST /users` отправь:

```json
{
  "username": "ibragim",
  "email": "ibragim@example.com",
  "age": 25
}
```

---

# 18. Что важно понять сразу

FastAPI endpoint — это не место для бизнес-логики.

Плохо:

```python
@app.post("/users")
async def create_user(user_data: UserCreate):
    # тут 100 строк логики
    # тут SQL
    # тут отправка email
    # тут создание токена
    # тут всё подряд
    ...
```

Правильно:

```text
router/controller → принимает HTTP
service           → бизнес-логика
repository        → работа с БД
schema            → Pydantic-модели
model             → SQLAlchemy-модели
```

FastAPI handler должен быть тонким.

---

# 19. Минимальная архитектурная схема

```text
app/
├── main.py
├── api/
│   └── v1/
│       └── users.py
├── schemas/
│   └── users.py
├── services/
│   └── users.py
├── repositories/
│   └── users.py
├── models/
│   └── users.py
└── core/
    └── config.py
```

Пока мы начали с одного `main.py`, чтобы понять механику.

Но production-проект нельзя держать в одном файле.

---

# 20. Антипаттерны на старте

## 20.1. Писать всё в `main.py`

Для первого урока можно.

Для реального проекта — нет.

---

## 20.2. Не использовать типизацию

Плохо:

```python
@app.get("/users/{user_id}")
async def get_user(user_id):
    ...
```

Нормально:

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int) -> UserRead:
    ...
```

---

## 20.3. Возвращать “что попало”

Плохо:

```python
return user.__dict__
```

Нормально:

```python
return UserRead.model_validate(user)
```

---

## 20.4. Смешивать Pydantic schema и SQLAlchemy model

Pydantic-модель:

```python
class UserRead(BaseModel):
    id: int
    username: str
```

SQLAlchemy-модель:

```python
class User(Base):
    __tablename__ = "users"
```

Это разные сущности.

---

# 21. Мини-задание

Создай API для товаров.

Нужно сделать:

```text
GET /products/{product_id}
GET /products?limit=10&offset=0
POST /products
```

Модели:

```python
class ProductCreate(BaseModel):
    title: str
    price: int
    description: str | None = None
```

```python
class ProductRead(BaseModel):
    id: int
    title: str
    price: int
    description: str | None = None
```

Требования:

* `product_id` должен быть `int`;
* `price` должен быть `int`;
* `description` может быть `None`;
* `POST /products` должен возвращать `ProductRead`;
* Swagger должен показывать все схемы.

---

# 22. Итог

Ты должен понять 7 вещей:

```text
1. FastAPI-приложение начинается с app = FastAPI()
2. Endpoint создаётся через @app.get(), @app.post() и т.д.
3. Path parameters идут внутри URL: /users/{user_id}
4. Query parameters идут после ?: /users?limit=10
5. Request body описывается через Pydantic BaseModel
6. response_model фиксирует контракт ответа
7. Handler не должен превращаться в мусорку с бизнес-логикой
```

---

# Что дальше

Следующий материал логично делать так:

```text
2_Структура_FastAPI_проекта.md
```

Там надо разобрать:

* почему `main.py` быстро становится мусором;
* что такое `APIRouter`;
* как разделять endpoints по модулям;
* как строить `api/v1`;
* где держать schemas;
* почему service layer обязателен;
* как выглядит нормальный минимальный FastAPI-проект.

[1]: https://fastapi.tiangolo.com/tutorial/first-steps/?utm_source=chatgpt.com "First Steps"
[2]: https://fastapi.tiangolo.com/tutorial/path-params/?utm_source=chatgpt.com "Path Parameters"
[3]: https://fastapi.tiangolo.com/async/?utm_source=chatgpt.com "Concurrency and async / await"
[4]: https://pypi.org/project/uvicorn/?utm_source=chatgpt.com "uvicorn"
[5]: https://pypi.org/project/pydantic/?utm_source=chatgpt.com "Pydantic"
[6]: https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/?utm_source=chatgpt.com "Path Operation Advanced Configuration"
[7]: https://pydantic.dev/docs/validation/2.12/concepts/types/?utm_source=chatgpt.com "Types | Pydantic Docs"
