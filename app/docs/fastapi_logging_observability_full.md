# FastAPI: Логирование и Observability Полный Разбор

## 0. Цель

Материал покрывает:

* logging;
* structured logs;
* request_id;
* error logs;
* access logs;
* Prometheus/metrics;
* healthcheck;
* readiness;
* Sentry;
* Grafana dashboards.

---

## 1. Что такое observability

Observability — способность понять состояние системы из:

1. логов;
2. метрик;
3. трассировок (traces).

Минимум для FastAPI:

* структурированные логи;
* request-id;
* health/readiness;
* прометеус-метрики;
* централизованный сбор ошибок (например, Sentry).

---

## 2. Logging

Базовая настройка:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger("app")
logger.info("service started")
```

---

## 3. Structured logs

Структурированные логи лучше хранить в JSON-подобном виде.

Почему:

* проще фильтрация в ELK/Loki;
* лучше корреляция запросов;
* легче строить дашборды.

Пример с `extra`:

```python
logger.info(
    "request handled",
    extra={
        "request_id": request_id,
        "path": "/users/1",
        "method": "GET",
        "status_code": 200,
    },
)
```

---

## 4. `request_id`

`request_id` нужен, чтобы связать:

* access log;
* error log;
* логи сервиса;
* логи downstream сервисов.

Middleware-пример:

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

---

## 5. Error logs

Логируй ошибки с контекстом:

* `request_id`;
* path;
* user_id (если есть);
* traceback.

```python
import logging

logger = logging.getLogger("app.errors")

try:
    ...
except Exception:
    logger.exception(
        "unhandled error",
        extra={"request_id": request_id, "path": path},
    )
    raise
```

Правило:

* в логи максимум контекста;
* в ответ клиенту минимум деталей.

---

## 6. Access logs

Access log фиксирует каждый HTTP-запрос:

* method;
* path;
* status_code;
* latency;
* request_id.

Пример middleware:

```python
import time


@app.middleware("http")
async def access_log_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000

    logger.info(
        "access",
        extra={
            "request_id": getattr(request.state, "request_id", "-"),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "elapsed_ms": round(elapsed_ms, 2),
        },
    )
    return response
```

---

## 7. Prometheus / metrics

Минимально полезные метрики:

* RPS (requests per second);
* latency (p50/p95/p99);
* error rate (4xx/5xx);
* количество активных workers.

Обычно:

* endpoint `/metrics`;
* scraping Prometheus;
* визуализация в Grafana.

Инструменты:

* `prometheus_client`;
* middleware для HTTP метрик.

---

## 8. Healthcheck

`/health` обычно отвечает только "жив ли процесс".

```python
@app.get("/health")
async def health():
    return {"status": "ok"}
```

Это liveness-probe.

---

## 9. Readiness

`/ready` проверяет готовность к трафику:

* доступность БД;
* доступность Redis;
* загрузка критичных зависимостей.

Пример:

```python
from fastapi import HTTPException


@app.get("/ready")
async def ready():
    db_ok = True  # например, ping DB
    redis_ok = True
    if not (db_ok and redis_ok):
        raise HTTPException(status_code=503, detail="not ready")
    return {"status": "ready"}
```

---

## 10. Sentry

Sentry нужен для автоматического сбора исключений.

Минимальная инициализация:

```python
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

sentry_sdk.init(
    dsn="YOUR_DSN",
    traces_sample_rate=0.1,
    environment="prod",
)

app.add_middleware(SentryAsgiMiddleware)
```

Практика:

* отдельные окружения (`dev`, `staging`, `prod`);
* не ставить слишком высокий trace rate без необходимости.

---

## 11. Grafana dashboards

Что обычно кладут в дашборд:

1. RPS по endpoint;
2. latency p50/p95/p99;
3. error rate;
4. top 5 endpoint по latency;
5. saturation (CPU/RAM/workers);
6. DB pool utilization.

Цель:

* быстро видеть деградацию;
* понимать, где bottleneck;
* ускорять incident response.

---

## 12. Минимальный продовый observability-stack

1. request-id middleware;
2. access + error structured logs;
3. `/health`, `/ready`, `/metrics`;
4. Prometheus + Grafana;
5. Sentry для ошибок.

---

## 13. Частые ошибки

1. Логи без `request_id`.
2. Нет разделения access/error логов.
3. Нет readiness, только health.
4. Нет метрик latency percentiles.
5. Не собирают ошибки централизованно.
6. Логируют секреты/PII.

---

## 14. Итог

Observability в FastAPI это не опция, а обязательный слой для production.

Минимальный практичный baseline:

* structured logging;
* request correlation;
* метрики и дашборды;
* отдельные probes;
* централизованный error tracking.
