# FastAPI: JWT через Bearer в Authorization Header

## 0. Что это

Bearer-вариант значит, что клиент отправляет JWT в HTTP header:

```http
Authorization: Bearer <access_token>
```

JWT здесь отвечает на вопрос **что передаем**, а Bearer отвечает на вопрос **как передаем**.

Поток:

1. Пользователь логинится по email/password.
2. Сервер проверяет пароль.
3. Сервер возвращает `access_token`.
4. Клиент сам добавляет header `Authorization: Bearer ...` в защищенные запросы.
5. FastAPI достает токен из header, проверяет его и пускает пользователя.

---

## 1. Когда использовать Bearer

Bearer хорошо подходит для:

* API;
* мобильных приложений;
* Postman/Swagger;
* backend-to-backend запросов;
* frontend, где токен хранится на стороне клиента и руками кладется в header.

Минус для браузерного frontend: если хранить JWT в `localStorage`, его может украсть XSS. Поэтому для обычного web-приложения часто безопаснее cookie с `HttpOnly`.

---

## 2. Зависимости

В проекте сейчас нет JWT-библиотеки. Для примеров нужен пакет:

```bash
pip install "python-jose[cryptography]" passlib[bcrypt]
```

В `requirements.txt` потом должны появиться примерно:

```txt
python-jose[cryptography]
passlib[bcrypt]
```

`passlib` нужен для нормальной проверки пароля. В твоем проекте поле называется `hashed_password`, но при создании пользователя сейчас туда можно передать обычный пароль. В реальном проекте пароль надо хешировать до записи в БД.

---

## 3. Настройки

Можно хранить настройки в `config.py`.

```python
JWT_SECRET_KEY = "change-me"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_ISSUER = "test-study-api"
JWT_AUDIENCE = "test-study-users"
```

Важно:

* `JWT_SECRET_KEY` нельзя коммитить в публичный репозиторий;
* в production его берут из `.env`;
* если секрет утек, все старые JWT надо считать скомпрометированными.

---

## 4. `core/security.py`

Создай файл `core/security.py`.

```python
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from config import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_AUDIENCE,
    JWT_ISSUER,
    JWT_SECRET_KEY,
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    payload = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
        audience=JWT_AUDIENCE,
        issuer=JWT_ISSUER,
    )

    if payload.get("type") != "access":
        raise JWTError("invalid token type")

    return payload
```

Что важно:

* `sub` — id пользователя;
* `type` — тип токена, чтобы refresh-токен нельзя было использовать как access;
* `exp` — срок жизни;
* `iss` — кто выпустил токен;
* `aud` — для кого токен.

---

## 5. `schemas/auth.py`

Создай файл `schemas/auth.py`.

```python
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

Ответ будет таким:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

## 6. Поиск пользователя по email

В текущем `UserServise` есть поиск по id, но для логина нужен поиск по email.

Пример метода в `repo/users.py`:

```python
from sqlalchemy import select

from core.models.user import User


async def get_user_by_email(self, email: str) -> User | None:
    result = await self.session.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()
```

Пример метода в `services/users.py`:

```python
async def get_user_by_email(self, email: str) -> User | None:
    if not isinstance(email, str) or not email.strip():
        raise ValueError("email is empty")

    return await self.repo.get_user_by_email(email=email)
```

---

## 7. `routers/auth.py`

Создай файл `routers/auth.py`.

```python
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from core.deps import get_user_service
from core.security import create_access_token, verify_password
from schemas.auth import LoginRequest, TokenResponse
from services.users import UserServise


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    service: UserServise = Depends(get_user_service),
) -> TokenResponse:
    user = await service.get_user_by_email(payload.email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid email or password",
        )

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid email or password",
        )

    access_token = create_access_token(user_id=user.id)
    return TokenResponse(access_token=access_token)
```

Этот endpoint только выдает токен. Он еще не защищает другие routes.

---

## 8. `core/deps.py`: зависимость текущего пользователя

Bearer-токен удобно доставать через `OAuth2PasswordBearer`.

```python
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from starlette import status

from core.security import decode_access_token
from services.users import UserServise


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    service: UserServise = Depends(get_user_service),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise credentials_exception

    user = await service.get_user(user_id=user_id)
    if user is None:
        raise credentials_exception

    return user
```

Теперь любой route может получить текущего пользователя через `Depends(get_current_user)`.

---

## 9. Защита endpoint

Например, защищенный `/users/me`.

```python
from fastapi import Depends

from core.deps import get_current_user
from core.models.user import User
from schemas.users import UserRead


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

Если токена нет, FastAPI вернет `401`.

Если токен плохой или истек, тоже `401`.

---

## 10. Подключение router

Если у тебя в `routers/__init__.py` собран общий router, добавь туда auth-router.

Пример:

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

`main.py` уже подключает общий router:

```python
app.include_router(router=router)
```

---

## 11. Как дергать через curl

Логин:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

Ответ:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

Защищенный запрос:

```bash
curl http://127.0.0.1:8000/users/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

---

## 12. Как дергать из JavaScript

```javascript
const loginResponse = await fetch("/auth/login", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    email: "test@example.com",
    password: "password123",
  }),
});

const tokens = await loginResponse.json();

const meResponse = await fetch("/users/me", {
  headers: {
    Authorization: `Bearer ${tokens.access_token}`,
  },
});

const me = await meResponse.json();
```

Здесь frontend сам хранит токен и сам кладет его в header.

---

## 13. Swagger

Из-за `OAuth2PasswordBearer(tokenUrl="/auth/login")` в Swagger UI появится кнопка **Authorize**.

Но стандартный Swagger OAuth2 password flow ожидает form-data с `username` и `password`, а пример выше принимает JSON `email/password`.

Для учебного проекта это не критично. Если хочешь максимально совместить со Swagger, login endpoint можно сделать через `OAuth2PasswordRequestForm`.

---

## 14. Главная схема

```text
Client
  |
  | POST /auth/login {email, password}
  v
FastAPI
  |
  | проверяет пароль
  | создает JWT
  v
Client получает access_token
  |
  | GET /users/me
  | Authorization: Bearer <jwt>
  v
FastAPI
  |
  | decode JWT
  | проверка exp/iss/aud/signature
  | поиск user по sub
  v
Endpoint получает current_user
```

---

## 15. Коротко

Bearer JWT auth:

```text
JWT = сам токен
Bearer = способ передать токен через Authorization header
```

Пример:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

Плюсы:

* удобно для API;
* удобно тестировать через Swagger/Postman;
* не требует cookie.

Минусы:

* клиент должен сам хранить токен;
* при хранении в `localStorage` есть риск кражи через XSS;
* refresh/logout надо проектировать отдельно.
