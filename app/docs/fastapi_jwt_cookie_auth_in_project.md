# FastAPI: JWT через Cookie

## 0. Что это

Cookie-вариант значит, что JWT лежит в cookie:

```http
Cookie: access_token=<jwt>
```

То есть JWT все еще остается JWT, но передается не через:

```http
Authorization: Bearer <token>
```

а через:

```http
Cookie: access_token=<token>
```

Браузер сам прикладывает cookie к запросам на нужный домен.

---

## 1. Когда использовать cookie

Cookie-вариант хорошо подходит для обычных web-приложений:

* frontend и backend на одном домене;
* сервер сам ставит токен в cookie;
* JavaScript не обязан видеть токен;
* можно поставить `HttpOnly`, чтобы токен нельзя было прочитать через `document.cookie`.

Главный плюс:

```text
HttpOnly cookie снижает риск кражи токена через XSS.
```

Главный минус:

```text
Cookie отправляются браузером автоматически, поэтому надо думать про CSRF.
```

---

## 2. Поток

1. Пользователь логинится через `/auth/login`.
2. Сервер проверяет пароль.
3. Сервер создает `access_token` и `refresh_token`.
4. Сервер кладет их в cookie через `response.set_cookie(...)`.
5. Клиент ходит в API без ручного `Authorization` header.
6. FastAPI читает `access_token` из cookie.
7. Если access истек, клиент дергает `/auth/refresh`, а сервер читает `refresh_token` из cookie.
8. При logout сервер удаляет cookie.

---

## 3. Зависимости

Нужны JWT и password hashing:

```bash
pip install "python-jose[cryptography]" passlib[bcrypt]
```

В `requirements.txt`:

```txt
python-jose[cryptography]
passlib[bcrypt]
```

---

## 4. Настройки

Пример для `config.py`.

```python
JWT_SECRET_KEY = "change-me"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 14
JWT_ISSUER = "test-study-api"
JWT_AUDIENCE = "test-study-users"

COOKIE_SECURE = False
COOKIE_SAMESITE = "lax"
```

Для production:

```python
COOKIE_SECURE = True
COOKIE_SAMESITE = "lax"  # или "strict", если подходит по UX
```

`secure=True` означает, что cookie отправляется только по HTTPS.

---

## 5. `core/security.py`

Создай файл `core/security.py`.

```python
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from config import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_AUDIENCE,
    JWT_ISSUER,
    JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    JWT_SECRET_KEY,
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(user_id: int, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload = {
        "sub": str(user_id),
        "type": token_type,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": str(uuid4()),
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_access_token(user_id: int) -> str:
    return create_token(
        user_id=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: int) -> str:
    return create_token(
        user_id=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    payload = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
        audience=JWT_AUDIENCE,
        issuer=JWT_ISSUER,
    )

    if payload.get("type") != expected_type:
        raise JWTError("invalid token type")

    return payload
```

Отличие от простого access-only варианта: здесь есть и `access`, и `refresh`.

---

## 6. `schemas/auth.py`

Создай файл `schemas/auth.py`.

```python
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class AuthStatus(BaseModel):
    status: str
```

При cookie-auth токены можно не возвращать в JSON, потому что они ставятся в cookie.

Ответ может быть таким:

```json
{
  "status": "ok"
}
```

---

## 7. Cookie helpers

Можно сделать отдельный файл `core/auth_cookies.py`.

```python
from fastapi import Response

from config import COOKIE_SAMESITE, COOKIE_SECURE, JWT_REFRESH_TOKEN_EXPIRE_DAYS


ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
) -> None:
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=access_token,
        max_age=30 * 60,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/",
    )
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/auth",
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(
        key=ACCESS_COOKIE_NAME,
        path="/",
    )
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path="/auth",
    )
```

Почему `refresh_token` с `path="/auth"`:

* он нужен только для `/auth/refresh` и `/auth/logout`;
* браузер не будет отправлять refresh-токен на обычные API endpoints;
* это уменьшает лишнюю поверхность риска.

---

## 8. Поиск пользователя по email

Для логина нужен метод поиска по email.

В `repo/users.py`:

```python
from sqlalchemy import select

from core.models.user import User


async def get_user_by_email(self, email: str) -> User | None:
    result = await self.session.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()
```

В `services/users.py`:

```python
async def get_user_by_email(self, email: str) -> User | None:
    if not isinstance(email, str) or not email.strip():
        raise ValueError("email is empty")

    return await self.repo.get_user_by_email(email=email)
```

---

## 9. `routers/auth.py`

Создай файл `routers/auth.py`.

```python
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from jose import JWTError
from starlette import status

from core.auth_cookies import clear_auth_cookies, set_auth_cookies
from core.deps import get_user_service
from core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from schemas.auth import AuthStatus, LoginRequest
from services.users import UserServise


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthStatus)
async def login(
    payload: LoginRequest,
    response: Response,
    service: UserServise = Depends(get_user_service),
) -> AuthStatus:
    user = await service.get_user_by_email(payload.email)

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid email or password",
        )

    access_token = create_access_token(user_id=user.id)
    refresh_token = create_refresh_token(user_id=user.id)
    set_auth_cookies(response, access_token, refresh_token)

    return AuthStatus(status="ok")


@router.post("/refresh", response_model=AuthStatus)
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    service: UserServise = Depends(get_user_service),
) -> AuthStatus:
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="refresh token missing",
        )

    try:
        payload = decode_token(refresh_token, expected_type="refresh")
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid refresh token",
        )

    user = await service.get_user(user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user not found",
        )

    new_access_token = create_access_token(user_id=user.id)
    new_refresh_token = create_refresh_token(user_id=user.id)
    set_auth_cookies(response, new_access_token, new_refresh_token)

    return AuthStatus(status="ok")


@router.post("/logout", response_model=AuthStatus)
async def logout(response: Response) -> AuthStatus:
    clear_auth_cookies(response)
    return AuthStatus(status="ok")
```

Важно: настоящий production-refresh лучше хранить в БД по `jti`, делать ротацию и уметь отзывать токены. Пример выше показывает механику cookie-auth.

---

## 10. `core/deps.py`: чтение access token из cookie

Для cookie-варианта не нужен `OAuth2PasswordBearer`, потому что токен не в `Authorization` header.

```python
from fastapi import Cookie, Depends, HTTPException
from jose import JWTError
from starlette import status

from core.auth_cookies import ACCESS_COOKIE_NAME
from core.security import decode_token
from services.users import UserServise


async def get_current_user(
    access_token: str | None = Cookie(default=None, alias=ACCESS_COOKIE_NAME),
    service: UserServise = Depends(get_user_service),
):
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not authenticated",
        )

    try:
        payload = decode_token(access_token, expected_type="access")
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid access token",
        )

    user = await service.get_user(user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user not found",
        )

    return user
```

Теперь protected endpoints работают так же, как в Bearer-варианте:

```python
from fastapi import Depends

from core.deps import get_current_user
from core.models.user import User
from schemas.users import UserRead


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

Разница только в том, откуда `get_current_user` берет токен.

---

## 11. Подключение router

В `routers/__init__.py`:

```python
from fastapi import APIRouter

from routers.auth import router as auth_router
from routers.posts import router as posts_router
from routers.users import router as users_router


router = APIRouter()
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(posts_router)
```

`main.py` уже делает:

```python
app.include_router(router=router)
```

---

## 12. Как дергать через curl

Логин с сохранением cookie в файл:

```bash
curl -i -c cookies.txt -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

В ответе будут headers:

```http
Set-Cookie: access_token=eyJhbGciOiJIUzI1NiIs...; HttpOnly; Path=/; SameSite=lax
Set-Cookie: refresh_token=eyJhbGciOiJIUzI1NiIs...; HttpOnly; Path=/auth; SameSite=lax
```

Защищенный запрос с cookie:

```bash
curl -b cookies.txt http://127.0.0.1:8000/users/me
```

Refresh:

```bash
curl -i -b cookies.txt -c cookies.txt -X POST http://127.0.0.1:8000/auth/refresh
```

Logout:

```bash
curl -i -b cookies.txt -c cookies.txt -X POST http://127.0.0.1:8000/auth/logout
```

---

## 13. Как дергать из JavaScript

Если frontend и backend на одном домене:

```javascript
await fetch("/auth/login", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    email: "test@example.com",
    password: "password123",
  }),
});

const meResponse = await fetch("/users/me");
const me = await meResponse.json();
```

Если frontend на другом домене, надо явно включать credentials:

```javascript
await fetch("https://api.example.com/auth/login", {
  method: "POST",
  credentials: "include",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    email: "test@example.com",
    password: "password123",
  }),
});

const meResponse = await fetch("https://api.example.com/users/me", {
  credentials: "include",
});
```

---

## 14. CORS для cookie

Если frontend и API на разных доменах, в `main.py` нужен CORS с credentials.

```python
from fastapi.middleware.cors import CORSMiddleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend.example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Нельзя использовать:

```python
allow_origins=["*"]
allow_credentials=True
```

Когда credentials включены, origin должен быть конкретным.

---

## 15. CSRF

Cookie отправляются браузером автоматически. Из-за этого появляется риск CSRF: чужой сайт может попытаться отправить запрос от имени пользователя.

Что помогает:

* `SameSite=Lax` или `SameSite=Strict`;
* CSRF-token для опасных методов `POST`, `PATCH`, `DELETE`;
* проверка `Origin` / `Referer`;
* разделение frontend/backend доменов с правильной CORS-политикой.

Для простого учебного проекта обычно начинают с:

```python
samesite="lax"
httponly=True
secure=True  # на HTTPS
```

---

## 16. Главная схема

```text
Client
  |
  | POST /auth/login {email, password}
  v
FastAPI
  |
  | проверяет пароль
  | создает access JWT
  | создает refresh JWT
  | Set-Cookie: access_token=...
  | Set-Cookie: refresh_token=...
  v
Browser хранит HttpOnly cookies
  |
  | GET /users/me
  | Cookie: access_token=<jwt>
  v
FastAPI
  |
  | читает access_token из cookie
  | decode JWT
  | проверка exp/iss/aud/signature
  | поиск user по sub
  v
Endpoint получает current_user
```

---

## 17. Bearer против Cookie

```text
Bearer:
Authorization: Bearer <jwt>

Cookie:
Cookie: access_token=<jwt>
```

Оба варианта могут быть JWT-авторизацией.

Разница:

* Bearer — клиент сам кладет токен в header;
* Cookie — браузер сам прикладывает cookie;
* Bearer удобно для API/Postman/mobile;
* Cookie удобно для web-приложения в браузере;
* Cookie с `HttpOnly` защищает токен от чтения через JS;
* Cookie требует внимания к CSRF.

---

## 18. Коротко

Cookie JWT auth:

```text
JWT = сам токен
Cookie = способ передать токен автоматически через браузер
```

Пример:

```http
Cookie: access_token=eyJhbGciOiJIUzI1NiIs...
```

Плюсы:

* удобно для браузерных web-приложений;
* можно использовать `HttpOnly`;
* frontend не обязан хранить токен руками.

Минусы:

* нужно учитывать CSRF;
* CORS сложнее, если frontend и backend на разных доменах;
* Swagger не так удобно тестировать, как Bearer.
