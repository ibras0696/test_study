# FastAPI: Testing Полный Разбор

## 0. Цель

Этот материал покрывает:

* `pytest`;
* `TestClient`;
* `httpx.AsyncClient`;
* `dependency_overrides`;
* test database;
* fixtures;
* unit/integration/API/negative tests;
* mocking external APIs.

---

## 1. `pytest`

`pytest` — основной раннер тестов в Python.

Минимальная структура:

```text
app/
tests/
  conftest.py
  test_users_api.py
```

Запуск:

```bash
pytest -q
```

---

## 2. `TestClient`

Для синхронных API-тестов FastAPI.

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
```

Плюс:

* простой вход;
* удобно для smoke/API тестов.

---

## 3. `httpx.AsyncClient`

Для async-тестов и async-стека.

```python
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_health_async():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/health")
    assert resp.status_code == 200
```

Когда лучше использовать:

* async endpoint;
* async DB;
* сложные цепочки async-зависимостей.

---

## 4. `dependency_overrides`

Подмена зависимостей в тестах.

```python
from main import app
from api.dependencies import get_current_user


def fake_user():
    return {"id": 999, "role": "admin"}


def test_me(client):
    app.dependency_overrides[get_current_user] = fake_user
    resp = client.get("/me")
    assert resp.status_code == 200
    assert resp.json()["id"] == 999
    app.dependency_overrides.clear()
```

Зачем:

* не ходить в реальный auth;
* детерминированные тесты;
* проще управлять контекстом.

---

## 5. Test database

Нужна отдельная БД для тестов.

Минимум:

1. отдельный `DATABASE_URL_TEST`;
2. миграции/схема для тестов;
3. очистка между тестами.

Пример подхода:

```python
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
```

Лучше в CI:

* поднимать отдельный Postgres контейнер;
* прогонять миграции перед тестами.

---

## 6. Fixtures

Fixtures управляют setup/teardown.

```python
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)
```

Async fixture:

```python
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

---

## 7. Unit tests

Тестируют функцию/класс изолированно.

Пример:

```python
def test_calc_discount():
    assert calc_discount(100, 10) == 90
```

Unit test:

* быстрый;
* без реальной БД/сети;
* фокус на бизнес-логике.

---

## 8. Integration tests

Проверяют интеграцию нескольких слоёв:

* API + DB;
* service + repository;
* dependency chain.

Пример:

```python
def test_create_user_integration(client):
    resp = client.post("/users", json={"username": "ibra", "email": "i@e.com", "age": 21})
    assert resp.status_code == 201
```

---

## 9. API tests

Проверяют HTTP-контракт:

* статус;
* response schema;
* headers;
* body.

Пример:

```python
def test_get_user_schema(client):
    resp = client.get("/users/1")
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        data = resp.json()
        assert "id" in data
        assert "username" in data
```

---

## 10. Negative tests

Тесты на ошибки и невалидные кейсы.

Примеры:

* неверный тип `user_id`;
* отсутствует auth;
* `age` вне диапазона;
* несуществующий ресурс.

```python
def test_get_user_wrong_id(client):
    resp = client.get("/users/not-int")
    assert resp.status_code == 422


def test_get_missing_user(client):
    resp = client.get("/users/999999")
    assert resp.status_code == 404
```

---

## 11. Mocking external APIs

Внешние сервисы в тестах нужно мокать.

Вариант через `unittest.mock`:

```python
from unittest.mock import AsyncMock, patch


@patch("services.email_service.send_email", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_register_sends_email(mock_send, async_client):
    resp = await async_client.post("/auth/register", json={"email": "a@b.com", "password": "12345678"})
    assert resp.status_code == 201
    mock_send.assert_awaited_once()
```

Цель:

* исключить сетевую нестабильность;
* ускорить тесты;
* сделать тесты детерминированными.

---

## 12. Рекомендуемая стратегия тестов

1. Unit — много, быстро, на бизнес-логику.
2. Integration — среднее количество, на связки слоёв.
3. API — ключевые endpoint-контракты.
4. Negative tests — обязательно для ошибок и валидации.
5. Mock внешних API — везде, где нет цели тестировать реальную интеграцию.

---

## 13. Частые ошибки

1. Тесты бьют продовую БД.
2. Нет cleanup между тестами.
3. Не очищают `dependency_overrides`.
4. Слишком много e2e без unit.
5. Внешние API не мокают.
6. Не тестируют негативные сценарии.

---

## 14. Итог

Хорошая тестовая база FastAPI = это:

* `pytest` + fixtures;
* `TestClient`/`AsyncClient` по задаче;
* isolated test DB;
* `dependency_overrides` для инфраструктуры;
* coverage позитивных и негативных кейсов.
