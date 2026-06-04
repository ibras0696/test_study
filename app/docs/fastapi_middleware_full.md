# FastAPI: Middleware Полный Разбор

## 0. Цель

Этот материал закрывает middleware-блок:

* request/response lifecycle;
* CORS middleware;
* logging middleware;
* request ID middleware;
* timing middleware;
* auth middleware (и почему осторожно);
* ошибка: бизнес-логика в middleware.

---

## 1. Что такое middleware

Middleware — слой между HTTP-запросом и endpoint.

Он:

* принимает запрос до роутера;
* может изменить request/response;
* передаёт управление дальше (`call_next`);
* получает response обратно.

---

## 2. Request/response lifecycle

Упрощённо:

1. клиент отправляет request;
2. middleware №1;
3. middleware №2;
4. роутер/endpoint;
5. middleware №2 (обратный путь);
6. middleware №1 (обратный путь);
7. клиент получает response.

То есть middleware работает как "обёртка".

---

## 3. Базовый middleware

```python
from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def sample_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-App"] = "my-api"
    return response
```

---

## 4. CORS middleware

Нужен, когда frontend и backend на разных origins.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://frontend.example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

В проде:

* не использовать `allow_origins=["*"]` вместе с credential cookies;
* хранить список origins явно.

---

## 5. Logging middleware

Логирует метод, путь, статус, время.

```python
import logging
import time
from fastapi import Request

logger = logging.getLogger("app.http")


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    logger.info(
        "HTTP %s %s -> %s (%.2fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response
```

---

## 6. Request ID middleware

Нужен для трассировки одного запроса через все логи/сервисы.

```python
import uuid
from fastapi import Request


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

Плюс:

* backend и frontend могут ссылаться на один ID;
* проще искать ошибку в логах.

---

## 7. Timing middleware

Добавляет серверное время обработки.

```python
import time
from fastapi import Request


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-Ms"] = f"{elapsed:.2f}"
    return response
```

---

## 8. Auth middleware — осторожно

Авторизацию можно делать middleware, но это не всегда лучший путь.

Почему осторожно:

1. сложно гибко отключать для отдельных роутов;
2. сложнее использовать зависимости (`Depends`) с разной логикой ролей;
3. легко превратить middleware в "монолит".

Часто лучше:

* аутентификацию делать в dependency (`get_current_user`);
* middleware оставить для технических задач (ID, timing, logging, CORS).

---

## 9. Ошибка: пихать бизнес-логику в middleware

Антипаттерн:

* в middleware проверять бизнес-правила заказа, баланса, статусов домена.

Почему плохо:

* теряется явность в endpoint;
* сложнее тестировать;
* сложно переиспользовать по роутам;
* растёт связность.

Правильно:

* middleware = инфраструктура (техслой);
* бизнес-логика = service слой + dependencies.

---

## 10. Порядок middleware имеет значение

Порядок добавления влияет на поведение.

Практический порядок:

1. `Request-ID`;
2. `Logging`;
3. `Timing`;
4. `CORS` (обычно добавляется отдельно через `add_middleware`).

Смысл:

* каждый лог содержит request-id;
* время запроса меряется вокруг всей обработки.

---

## 11. Мини-практика полной связки

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid
import logging

logger = logging.getLogger("app.http")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.middleware("http")
async def logging_and_timing_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000

    response.headers["X-Process-Time-Ms"] = f"{elapsed:.2f}"
    logger.info(
        "[%s] %s %s -> %s %.2fms",
        getattr(request.state, "request_id", "-"),
        request.method,
        request.url.path,
        response.status_code,
        elapsed,
    )
    return response
```

---

## 12. Частые ошибки

1. Хранить важные доменные проверки в middleware.
2. Делать один гигантский middleware "на всё".
3. Не ставить request-id.
4. Логировать только ошибки, без успешных запросов.
5. Неправильно настраивать CORS для prod.
6. Не понимать порядок middleware и получить неожиданные заголовки/логи.

---

## 13. Итог

Middleware в FastAPI — это инфраструктурный слой.

Используй его для:

* CORS;
* request-id;
* timing;
* технического логирования;
* технических заголовков.

Не используй для:

* бизнес-правил;
* сложной auth/permission логики, которую лучше держать в dependencies и сервисах.
