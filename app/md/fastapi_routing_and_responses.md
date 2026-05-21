# FastAPI: Роутеры, Строгая Валидация, Request/Response

## 0. Цель

Этот материал объясняет, как в FastAPI строится слой API:

1. роутинг;
2. валидация входных данных;
3. контракт ответа через `response_model`;
4. форматы ответа (`JSONResponse`, `StreamingResponse`, `FileResponse`, custom response);
5. работа с headers/cookies/form/file.

---

## 1. Базовая идея роутинга

Роутинг в FastAPI сопоставляет:

* HTTP метод (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`);
* путь (`/users/{user_id}`);
* функцию-обработчик.

Пример:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
```

---

## 2. Роутинг

### 2.1 `@app.get()`

Чтение данных.

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    ...
```

### 2.2 `@app.post()`

Создание данных.

```python
@app.post("/users")
async def create_user(payload: UserCreate):
    ...
```

### 2.3 `@app.put()`

Полная замена ресурса.

```python
@app.put("/users/{user_id}")
async def replace_user(user_id: int, payload: UserReplace):
    ...
```

### 2.4 `@app.patch()`

Частичное обновление.

```python
@app.patch("/users/{user_id}")
async def update_user(user_id: int, payload: UserPatch):
    ...
```

### 2.5 `@app.delete()`

Удаление ресурса.

```python
@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    ...
```

### 2.6 `APIRouter`

`APIRouter` нужен для модульной структуры: отдельно `users`, `posts`, `auth`.

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_users():
    return []
```

### 2.7 `prefix`

Общий префикс для группы роутов.

```python
router = APIRouter(prefix="/users")
```

### 2.8 `tags`

Группировка в Swagger UI.

```python
router = APIRouter(prefix="/users", tags=["Users"])
```

### 2.9 `status_code`

Явная установка статуса ответа.

```python
from starlette import status

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(...):
    ...
```

### 2.10 `response_model`

Задаёт контракт ответа: что клиент увидит в JSON.

```python
@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int):
    ...
```

### 2.11 `include_router()`

Подключение модулей в главный `app`.

```python
app = FastAPI()
app.include_router(users_router)
app.include_router(posts_router)
```

---

## 3. Строгая валидация

Строгая валидация нужна, чтобы не пропускать кривые данные.

Ключевые инструменты:

* `Field(...)` с ограничениями;
* строгие типы (`StrictInt`, `StrictStr`, `EmailStr`);
* `constr`, `conint` или `Annotated` с правилами;
* запрет лишних полей через `model_config = ConfigDict(extra="forbid")`.

Пример:

```python
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, EmailStr


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: StrictStr = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    age: StrictInt = Field(ge=18, le=120)
```

Что это даёт:

* `age="25"` строкой не пройдет как `StrictInt`;
* неизвестные поля не принимаются;
* username проходит только по regex.

---

## 4. `response_model=ApiResponse`

Частая практика: единый envelope для всех ответов API.

```python
from typing import Any
from pydantic import BaseModel


class ApiResponse(BaseModel):
    success: bool
    message: str | None = None
    data: Any | None = None
```

Использование:

```python
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/{user_id}", response_model=ApiResponse)
async def get_user(user_id: int):
    user = {"id": user_id, "username": "ibra"} if user_id == 1 else None
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return ApiResponse(success=True, data=user)
```

Плюсы:

* единый формат для frontend;
* проще стандартизировать обработку ошибок/успеха;
* документация Swagger становится единообразной.

---

## 5. Headers

Чтение заголовков запроса:

```python
from fastapi import Header

@router.get("/me")
async def me(user_agent: str | None = Header(default=None)):
    return {"user_agent": user_agent}
```

Кейс:

* `Authorization`;
* `X-Request-ID`;
* `User-Agent`;
* `Accept-Language`.

---

## 6. Cookies

Чтение cookie:

```python
from fastapi import Cookie

@router.get("/session")
async def session(session_id: str | None = Cookie(default=None)):
    return {"session_id": session_id}
```

Установка cookie:

```python
from fastapi import Response

@router.post("/login")
async def login(response: Response):
    response.set_cookie(key="session_id", value="abc123", httponly=True, samesite="lax")
    return {"ok": True}
```

---

## 7. Form data

Когда данные идут как форма:

```python
from fastapi import Form

@router.post("/login-form")
async def login_form(username: str = Form(...), password: str = Form(...)):
    return {"username": username}
```

---

## 8. File upload

Загрузка файла через `UploadFile`.

```python
from fastapi import File, UploadFile

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    return {"filename": file.filename, "size": len(content)}
```

---

## 9. Response model

`response_model`:

* валидирует ответ;
* фильтрует лишние поля;
* формирует OpenAPI-схему.

```python
from pydantic import BaseModel


class UserRead(BaseModel):
    id: int
    username: str


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int):
    return {"id": user_id, "username": "ibra", "secret": "hidden"}  # secret будет отброшен
```

---

## 10. `JSONResponse`

Ручной контроль тела и статуса ответа.

```python
from fastapi.responses import JSONResponse

@router.get("/manual-json")
async def manual_json():
    return JSONResponse(status_code=202, content={"accepted": True})
```

---

## 11. `StreamingResponse`

Для потоковой отправки данных.

```python
from fastapi.responses import StreamingResponse


def iter_chunks():
    for i in range(3):
        yield f"chunk-{i}\n"


@router.get("/stream")
async def stream_data():
    return StreamingResponse(iter_chunks(), media_type="text/plain")
```

---

## 12. `FileResponse`

Отдача файла с диска:

```python
from fastapi.responses import FileResponse

@router.get("/download")
async def download_file():
    return FileResponse(path="reports/report.pdf", filename="report.pdf")
```

---

## 13. Custom response

Можно вернуть свой response-класс или настроить `Response` вручную.

```python
from fastapi import Response

@router.get("/plain")
async def plain_text():
    return Response(content="OK", media_type="text/plain", status_code=200)
```

---

## 14. Рекомендуемая структура проекта

```text
app/
  main.py
  api/
    routers/
      users.py
      posts.py
  schemas/
    common.py
    users.py
  services/
  models/
```

`main.py`:

```python
from fastapi import FastAPI
from api.routers.users import router as users_router
from api.routers.posts import router as posts_router

app = FastAPI()
app.include_router(users_router)
app.include_router(posts_router)
```

---

## 15. Частые ошибки

1. Возвращать `{"status": 404}` вместо `raise HTTPException(status_code=404, ...)`.
2. Смешивать ORM-модель в `response_model` напрямую.
3. Не задавать `response_model` для публичных роутов.
4. Не использовать `APIRouter`, а писать всё в одном `main.py`.
5. Слабая валидация (`str` без ограничений, `extra` не запрещён).

---

## 16. Итог

Минимальный production-подход:

1. Роуты только через `APIRouter`.
2. Явные `prefix`, `tags`, `status_code`.
3. Строгие request-схемы.
4. `response_model` для каждого endpoint.
5. Единый формат ответа (`ApiResponse`), где это уместно.
6. Явный выбор response-класса для специальных кейсов (stream/file/custom).
