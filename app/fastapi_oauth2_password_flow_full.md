# FastAPI: OAuth2 Password Flow Полный Разбор

## 0. Цель

Этот материал объясняет `OAuth2 Password Flow` в FastAPI:

* как работает flow;
* как выглядит endpoint `/token`;
* как использовать `OAuth2PasswordBearer`;
* где этот flow уместен, а где лучше выбрать другой.

---

## 1. Что такое OAuth2 Password Flow

Password Flow:

1. клиент отправляет логин/пароль на `/token`;
2. сервер валидирует credentials;
3. сервер возвращает access token;
4. клиент ходит с bearer token в API.

В FastAPI это классический учебно-практический сценарий для backend API.

---

## 2. Когда уместен

Подходит:

* когда у тебя свой backend и свой login/password;
* first-party клиенты;
* internal systems и классические API.

Не лучший выбор:

* публичные third-party интеграции;
* сложный SSO через внешних провайдеров.

Для SSO обычно используют Authorization Code + PKCE / OIDC.

---

## 3. Базовые компоненты в FastAPI

1. `OAuth2PasswordBearer` — dependency для чтения bearer токена.
2. `OAuth2PasswordRequestForm` — форма для `/token`.
3. `tokenUrl` — URL endpoint выдачи токена.

---

## 4. `OAuth2PasswordBearer`

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
```

Что делает:

* ожидает `Authorization: Bearer <token>`;
* отдаёт токен строкой в dependency.

---

## 5. Endpoint `/token` с `OAuth2PasswordRequestForm`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token")
async def issue_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await auth_service.verify_credentials(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid credentials",
        )

    access_token = token_service.create_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer"}
```

Важно:

* `OAuth2PasswordRequestForm` принимает `application/x-www-form-urlencoded`, не JSON.

---

## 6. Защищённый endpoint

```python
from fastapi import Depends, HTTPException


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = token_service.decode(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="invalid token")
    user = await user_service.get_by_id(int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="user not found")
    return user


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username}
```

---

## 7. Swagger интеграция

Когда задан `oauth2_scheme`, Swagger UI:

* показывает кнопку `Authorize`;
* умеет отправлять bearer token в запросы.

Это удобно для ручного тестирования.

---

## 8. Password Flow + JWT (частый паттерн)

На практике Password Flow обычно выдает JWT:

* access token (обязательно);
* refresh token (часто отдельно endpoint `/refresh`).

То есть flow отвечает за выдачу токена, а формат токена часто JWT.

---

## 9. Безопасность

Обязательные меры:

1. только HTTPS;
2. хранить пароль в БД только как hash (`bcrypt/argon2`);
3. rate-limit на `/token`;
4. lockout/pause после серии неудачных входов;
5. аудит входов и `request_id` в логах.

---

## 10. Частые ошибки

1. Ждать JSON вместо form-data на `/token`.
2. Не хэшировать пароль.
3. Выдавать слишком долгоживущий access token.
4. Не возвращать правильный `401` для невалидного токена.
5. Смешивать auth-логику в каждом endpoint вместо dependency.

---

## 11. Мини-шаблон структуры

```text
app/
  api/
    routers/
      auth.py
  core/
    security.py
  services/
    auth_service.py
```

Границы:

* `auth.py` — HTTP слой (`/token`, `/refresh`);
* `security.py` — токены/хеширование;
* `auth_service.py` — проверка пользователя.

---

## 12. Итог

`OAuth2 Password Flow` в FastAPI:

* простой и рабочий способ выдать bearer token;
* отлично подходит для first-party API;
* обычно используется в связке с JWT и зависимостью `OAuth2PasswordBearer`.
