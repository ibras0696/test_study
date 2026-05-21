# FastAPI Roadmap

## Визуальный маршрут

```text
[1] API Core
    ├─ routing + response
    ├─ pydantic schemas
    └─ dependency injection
         ↓
[2] HTTP Infrastructure
    ├─ errors
    └─ middleware
         ↓
[3] Auth
    ├─ OAuth2 Password Flow
    └─ JWT access/refresh
         ↓
[4] Async Jobs
    └─ background tasks / queues
         ↓
[5] Production Readiness
    ├─ config/settings
    └─ logging/observability
         ↓
[6] Testing
    └─ unit/integration/api/negative
```

---

## Порядок изучения (чеклист)

- [ ] 1. [fastapi_routing_and_responses.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_routing_and_responses.md)
- [ ] 2. [fastapi_pydantic_full.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_pydantic_full.md)
- [ ] 3. [fastapi_dependency_injection_full.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_dependency_injection_full.md)
- [ ] 4. [fastapi_errors_full.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_errors_full.md)
- [ ] 5. [fastapi_middleware_full.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_middleware_full.md)
- [ ] 6. [fastapi_oauth2_password_flow_full.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_oauth2_password_flow_full.md)
- [ ] 7. [fastapi_jwt_access_refresh_full.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_jwt_access_refresh_full.md)
- [ ] 8. [fastapi_background_tasks_and_queues.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_background_tasks_and_queues.md)
- [ ] 9. [fastapi_config_settings_full.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_config_settings_full.md)
- [ ] 10. [fastapi_logging_observability_full.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_logging_observability_full.md)
- [ ] 11. [fastapi_testing_full.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_testing_full.md)

---

## Этапы и результат

### Stage 1: API Core
- Файлы:
  - [fastapi_routing_and_responses.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_routing_and_responses.md)
  - [fastapi_pydantic_full.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_pydantic_full.md)
  - [fastapi_dependency_injection_full.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_dependency_injection_full.md)
- Done when:
  - умеешь собрать CRUD-роутер через `APIRouter`
  - есть строгие request/response schemas
  - `Depends` используется для `db` и `current_user`

### Stage 2: HTTP Infrastructure
- Файлы:
  - [fastapi_errors_full.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_errors_full.md)
  - [fastapi_middleware_full.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_middleware_full.md)
- Done when:
  - все ошибки возвращаются в едином формате
  - есть middleware: request-id + timing + access log
  - CORS настроен явно

### Stage 3: Auth
- Файлы:
  - [fastapi_oauth2_password_flow_full.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_oauth2_password_flow_full.md)
  - [fastapi_jwt_access_refresh_full.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_jwt_access_refresh_full.md)
- Done when:
  - работает `/auth/token` или `/auth/login`
  - access token защищает приватные роуты
  - refresh flow обновляет access

### Stage 4: Async Jobs
- Файл:
  - [fastapi_background_tasks_and_queues.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_background_tasks_and_queues.md)
- Done when:
  - понимаешь, где хватает `BackgroundTasks`
  - умеешь обосновать, когда нужен Celery + Redis/RabbitMQ

### Stage 5: Production Readiness
- Файлы:
  - [fastapi_config_settings_full.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_config_settings_full.md)
  - [fastapi_logging_observability_full.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_logging_observability_full.md)
- Done when:
  - все настройки идут через `Settings`
  - есть health/readiness endpoints
  - есть structured logs и базовые метрики

### Stage 6: Testing
- Файл:
  - [fastapi_testing_full.md](/Users/ibragim/PycharmProjects/aio_bot/test_study/app/fastapi_testing_full.md)
- Done when:
  - есть unit + integration + API tests
  - есть negative tests
  - внешние API замоканы

---

## Мини-план на 14 дней

```text
Day 1-2   -> Stage 1 (routing + pydantic)
Day 3-4   -> Stage 1 (DI + mini CRUD)
Day 5     -> Stage 2 (errors)
Day 6     -> Stage 2 (middleware)
Day 7-8   -> Stage 3 (OAuth2 + JWT)
Day 9     -> Stage 4 (background/queues)
Day 10-11 -> Stage 5 (settings)
Day 12    -> Stage 5 (observability)
Day 13-14 -> Stage 6 (tests)
```

---

## Финальный чек

- [ ] API модульный (`APIRouter`, `include_router`)
- [ ] Валидация строгая (`extra="forbid"`, ограничения `Field`)
- [ ] Ошибки единообразные
- [ ] Auth: access/refresh работает
- [ ] Настройки только через env/settings
- [ ] Логи и health/readiness есть
- [ ] Тесты покрывают позитивные и негативные кейсы
