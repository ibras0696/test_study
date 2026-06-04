# FastAPI: Ошибки и Обработка Ошибок

## 0. Цель

Этот материал закрывает практический блок по ошибкам:

* `HTTPException`;
* статус-коды;
* custom exceptions;
* exception handlers;
* validation errors;
* business errors;
* единая error schema;
* логирование ошибок.

---

## 1. Базовая логика ошибок в API

Любая ошибка в API должна быть:

1. предсказуемой для клиента;
2. понятной по статус-коду;
3. безопасной (без утечки внутренностей);
4. залогированной на сервере.

Неправильно:

* просто `return {"error": "something wrong"}` со статусом 200.

Правильно:

* вернуть правильный HTTP статус + структурированное тело.

---

## 2. `HTTPException`

Самый базовый инструмент FastAPI.

```python
from fastapi import HTTPException


def get_user_or_404(user_id: int):
    user = None
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return user
```

Важно:

* `raise`, а не `return`;
* `detail` может быть строкой или объектом.

---

## 3. Status codes

Частые коды в FastAPI API:

* `400 Bad Request` — запрос некорректный;
* `401 Unauthorized` — не авторизован;
* `403 Forbidden` — нет прав;
* `404 Not Found` — ресурс не найден;
* `409 Conflict` — конфликт состояния;
* `422 Unprocessable Entity` — ошибки валидации;
* `500 Internal Server Error` — внутренняя ошибка.

Пример:

```python
from fastapi import HTTPException, status

raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
```

---

## 4. Custom exceptions

Для бизнес-слоя лучше свои исключения.

```python
class UserNotFoundError(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"user {user_id} not found")


class PermissionDeniedError(Exception):
    pass
```

Плюс:

* бизнес-логика не знает про HTTP;
* HTTP-слой решает, как мапить исключение в статус/ответ.

---

## 5. Exception handlers

Глобальные обработчики связывают custom exception с HTTP-ответом.

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "USER_NOT_FOUND",
                "message": f"user {exc.user_id} not found",
            }
        },
    )
```

---

## 6. Validation errors

Ошибки валидации входа FastAPI обычно возвращает как `422`.

Пример невалидного запроса:

* ожидали `int`, пришла строка;
* не прошёл `min_length`;
* отсутствует обязательное поле.

Можно переопределить обработчик:

```python
from fastapi.exceptions import RequestValidationError


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "request validation failed",
                "details": exc.errors(),
            }
        },
    )
```

---

## 7. Business errors

Бизнес-ошибки — это не технические баги, а доменные правила.

Примеры:

* недостаточно средств;
* пользователь заблокирован;
* срок подписки истёк;
* нельзя удалить сущность в текущем статусе.

Рекомендуемая схема:

1. сервис бросает `BusinessError`;
2. global handler мапит в `409/422/403`;
3. клиент получает стабильный `error.code`.

```python
class BusinessError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 409):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)
```

---

## 8. Error schema

Хорошая практика: единый формат ошибки.

```python
from pydantic import BaseModel


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict | list | None = None


class ErrorResponse(BaseModel):
    error: ErrorPayload
```

Плюсы:

* frontend проще обрабатывать ошибки;
* API становится предсказуемым;
* документация чище.

---

## 9. Logging errors

Ошибки нужно логировать на сервере, но клиенту отдавать безопасный текст.

```python
import logging
from fastapi import Request

logger = logging.getLogger("app.errors")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error", extra={"path": str(request.url)})
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "internal server error",
            }
        },
    )
```

Важно:

* в логах — максимум деталей;
* в ответе клиенту — минимум деталей.

---

## 10. Мини-шаблон production

1. `HTTPException` для простых кейсов.
2. Custom exceptions для бизнес-логики.
3. Global handlers для стандартизации.
4. Единая `ErrorResponse`.
5. Логирование всех `Exception`.
6. Не отдавать stack trace клиенту.

---

## 11. Частые ошибки

1. Возвращать `200` с полем `"error"`.
2. Мешать бизнес-логику и HTTP-слой.
3. Отдавать разные форматы ошибки в разных роутерах.
4. Отдавать внутренние тексты SQL/Python наружу.
5. Не логировать контекст запроса (`path`, `request_id`, `user_id`).

---

## 12. Итог

Качественная обработка ошибок в FastAPI = это контракт:

* для клиента — понятный статус и стабильный `error.code`;
* для backend — структурированные исключения и логи;
* для команды — меньше хаоса при отладке и интеграции.
