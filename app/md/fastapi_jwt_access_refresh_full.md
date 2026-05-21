# FastAPI: JWT (Access + Refresh) Полный Разбор

## 0. Цель

Этот материал объясняет production-паттерн авторизации:

* короткоживущий `access token`;
* долгоживущий `refresh token`;
* безопасное обновление сессии;
* ротация и отзыв токенов.

---

## 1. Зачем 2 токена

### Access token

* живёт недолго (например, 5-15 минут);
* используется в `Authorization: Bearer <token>`;
* нужен для доступа к API.

### Refresh token

* живёт дольше (например, 7-30 дней);
* используется только для получения нового access token;
* не должен часто ходить по всем endpoint.

Идея:

* если access утёк, окно риска маленькое;
* пользователь не логинится каждые 10 минут, потому что есть refresh.

---

## 2. Базовый поток

1. Пользователь логинится (`/auth/login`).
2. Сервер возвращает `access_token` + `refresh_token`.
3. Клиент ходит в API с access token.
4. Access истёк -> клиент вызывает `/auth/refresh` с refresh token.
5. Сервер проверяет refresh, выдаёт новый access (и часто новый refresh).

---

## 3. Минимальная структура claims

Обычно в JWT кладут:

* `sub` — user id;
* `type` — `access` или `refresh`;
* `exp` — срок жизни;
* `iat` — когда выдан;
* `jti` — уникальный id токена.

Пример payload:

```json
{
  "sub": "123",
  "type": "access",
  "exp": 1760000000,
  "iat": 1759999000,
  "jti": "4f7d..."
}
```

---

## 4. Пример схем

```python
from pydantic import BaseModel


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str
```

---

## 5. Выдача токенов (логин)

```python
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenPair)
async def login(payload: LoginRequest):
    user = await auth_service.verify_credentials(payload.username, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="invalid credentials")

    access = token_service.create_access_token(user_id=user.id)
    refresh = token_service.create_refresh_token(user_id=user.id)
    return TokenPair(access_token=access, refresh_token=refresh)
```

---

## 6. Защита endpoint access-токеном

```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = token_service.decode(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="invalid token type")
    user_id = payload.get("sub")
    user = await user_service.get_by_id(int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="user not found")
    return user


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username}
```

---

## 7. Refresh endpoint

```python
@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(payload: RefreshRequest):
    token_data = token_service.decode(payload.refresh_token)

    if token_data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="invalid token type")

    user_id = int(token_data["sub"])
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="user not found")

    # optional: check token jti in DB / denylist
    new_access = token_service.create_access_token(user_id=user.id)
    new_refresh = token_service.create_refresh_token(user_id=user.id)  # rotation
    return TokenPair(access_token=new_access, refresh_token=new_refresh)
```

---

## 8. Где хранить refresh token

Варианты:

1. `HttpOnly` cookie (часто лучший для web);
2. secure storage на мобильном клиенте;
3. never localStorage для чувствительных токенов в браузере.

Для web:

* `HttpOnly`;
* `Secure`;
* `SameSite` по политике продукта.

---

## 9. Ротация refresh token

Рекомендуется:

1. при каждом `/refresh` выдавать новый refresh;
2. старый refresh делать недействительным;
3. хранить `jti`/семейство токенов в БД.

Плюс:

* снижает риск replay-атаки.

---

## 10. Отзыв токенов (logout / revoke)

JWT сам по себе stateless, но logout обычно требует state:

* denylist по `jti`;
* таблица активных refresh-сессий;
* инвалидация всех refresh для пользователя при смене пароля.

---

## 11. Время жизни токенов

Практичный baseline:

* access: 10-15 минут;
* refresh: 7-30 дней.

Зависит от риска и продукта:

* fintech/админки -> короче;
* user-facing apps -> баланс UX и security.

---

## 12. Частые ошибки

1. Делать access token на сутки.
2. Не различать `type=access` и `type=refresh`.
3. Не делать ротацию refresh.
4. Хранить токены в небезопасном месте.
5. Не проверять `exp`, `iss`, `aud` (если используешь).
6. Не иметь механизма revoke при компрометации.

---

## 13. Итог

`JWT access/refresh` — практичный стандарт для FastAPI API:

* короткий access для запросов;
* длинный refresh для продления;
* ротация, revoke и строгая проверка claims для безопасности.
