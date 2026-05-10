# FastAPI: Background Tasks и Очереди

## 0. Цель

Этот материал закрывает практический блок:

* `BackgroundTasks`;
* когда использовать;
* когда не использовать;
* Celery;
* RabbitMQ/Redis broker;
* retry/backoff;
* idempotency;
* periodic tasks;
* ключевая ошибка: считать `BackgroundTasks` заменой Celery.

---

## 1. Что такое BackgroundTasks

`BackgroundTasks` в FastAPI позволяет запланировать функцию после отправки HTTP-ответа.

```python
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()


def write_log(message: str) -> None:
    with open("app.log", "a", encoding="utf-8") as f:
        f.write(message + "\n")


@app.post("/orders")
async def create_order(background_tasks: BackgroundTasks):
    background_tasks.add_task(write_log, "order created")
    return {"ok": True}
```

Смысл:

* клиент получает ответ быстро;
* дополнительная работа запускается в фоне внутри процесса API.

---

## 2. Когда можно использовать `BackgroundTasks`

Используй, если задача:

1. короткая и лёгкая;
2. не критична к гарантированной доставке;
3. не требует сложных retry/persistence;
4. допустимо потерять задачу при падении процесса.

Примеры:

* запись audit-лога;
* отправка "мягкого" webhook;
* обновление кеша без строгих гарантий;
* пост-обработка, которую можно повторить вручную.

---

## 3. Когда нельзя использовать `BackgroundTasks`

Не используй, если задача:

1. долгоживущая (секунды/минуты/часы);
2. критичная для бизнеса (деньги, биллинг, инвойсы);
3. требует гарантированного исполнения;
4. требует ретраев и dead-letter логики;
5. должна переживать рестарт API-инстанса.

Примеры:

* платежные операции;
* генерация больших отчётов;
* массовые email/SMS рассылки;
* интеграции с внешними API с обязательной доставкой.

---

## 4. Celery

`Celery` — полноценная система фоновых задач с очередями.

Что даёт:

* отдельные worker-процессы;
* брокер сообщений;
* retries;
* backoff;
* планировщик периодических задач (через beat);
* масштабирование независимо от API.

Базовая архитектура:

```text
FastAPI -> broker (Redis/RabbitMQ) -> Celery worker
```

---

## 5. RabbitMQ / Redis broker

Брокер — транспорт между API и workers.

### Redis

Плюсы:

* проще старт;
* удобно для малого/среднего проекта.

### RabbitMQ

Плюсы:

* сильная модель очередей и маршрутизации;
* часто лучше для сложных enterprise-сценариев.

Выбор зависит от требований:

* простота/скорость старта -> Redis;
* сложная маршрутизация/надежность очередей -> RabbitMQ.

---

## 6. Retry / backoff

Нужны, когда внешняя система может временно падать.

Принцип:

1. задача упала;
2. повторяем через задержку;
3. каждый следующий retry с увеличением задержки (backoff);
4. после лимита — fail + алерт.

Пример с Celery:

```python
from celery import Celery

celery_app = Celery("tasks", broker="redis://localhost:6379/0")


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5})
def send_email(self, email: str, body: str):
    # external SMTP/API call
    ...
```

---

## 7. Idempotency

Идемпотентность = повторный запуск задачи не ломает состояние.

Почему важно:

* retry может запустить задачу повторно;
* worker может обработать дубль;
* сеть/таймауты приводят к повторной отправке.

Подходы:

1. уникальный `idempotency_key`;
2. таблица обработанных операций;
3. проверка "уже выполнено?" перед действием;
4. уникальные индексы в БД.

Пример идеи:

```text
if operation_key already processed:
    skip
else:
    do work + mark processed
```

---

## 8. Periodic tasks

Периодические задачи:

* очистка старых данных;
* синхронизация с внешним сервисом;
* пересчёт агрегатов;
* nightly отчёты.

Для Celery обычно используют `celery beat`.

Пример:

```python
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "cleanup-nightly": {
        "task": "tasks.cleanup_old_data",
        "schedule": crontab(hour=3, minute=0),
    },
}
```

---

## 9. Ошибка: считать `BackgroundTasks` заменой Celery

Это главный анти-паттерн.

`BackgroundTasks`:

* живёт в процессе API;
* не очередь;
* нет гарантий доставки;
* не переживает падение процесса.

Celery:

* отдельные workers;
* брокер;
* retries/backoff;
* масштабирование;
* более высокая надежность.

Итог:

* `BackgroundTasks` — для лёгких best-effort задач;
* Celery/очереди — для важных и тяжёлых задач.

---

## 10. Практическая стратегия выбора

Используй `BackgroundTasks`, если:

1. задача до 100-300 мс и не критична;
2. допустимо редкое выпадение;
3. не нужна сложная оркестрация.

Используй Celery + Redis/RabbitMQ, если:

1. задача критична;
2. нужна гарантия и наблюдаемость;
3. нужна масштабируемость workers;
4. нужен retry/backoff и schedule.

---

## 11. Мини-шаблон продовой архитектуры

1. API принимает запрос и валидирует данные.
2. Создаёт запись операции в БД (`pending`).
3. Публикует задачу в broker.
4. Worker берёт задачу и выполняет.
5. Обновляет статус (`done`/`failed`).
6. При ошибке — retry/backoff.
7. Все шаги логируются с `request_id`/`task_id`.

---

## 12. Итог

Коротко:

* `BackgroundTasks` не является очередью;
* для серьёзных задач нужен queue-based worker stack;
* надежность фоновой обработки = broker + retries + idempotency + monitoring.
