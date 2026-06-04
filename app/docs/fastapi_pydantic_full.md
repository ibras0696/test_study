# FastAPI + Pydantic: Полное Практическое Объяснение

## 0. Зачем Pydantic в FastAPI

Pydantic в FastAPI решает 3 задачи:

1. валидация входных данных;
2. сериализация/десериализация;
3. контракт API для OpenAPI/Swagger.

Если коротко:

* request -> Pydantic проверяет;
* обработчик работает с типизированными объектами;
* response -> Pydantic формирует безопасный JSON.

---

## 1. `BaseModel`

Базовый класс для схем.

```python
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    age: int
```

Теперь FastAPI умеет автоматически:

* парсить JSON в `UserCreate`;
* валидировать типы;
* отдавать ошибки 422 при невалидных данных.

---

## 2. `Field()`

Через `Field` задаются ограничения и метаданные.

```python
from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    age: int = Field(ge=18, le=120)
```

Что это даёт:

* `username` короче 3 -> ошибка;
* `age=15` -> ошибка;
* `email="abc"` -> ошибка.

---

## 3. Validation

Валидация идёт в несколько уровней:

1. типы (`int`, `str`, `EmailStr`);
2. ограничения (`ge`, `le`, `min_length`, `pattern`);
3. пользовательская логика (validators).

Пример пользовательской проверки:

```python
from pydantic import BaseModel, field_validator


class PasswordInput(BaseModel):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("password must be at least 8 chars")
        return value
```

---

## 4. Serialization

Сериализация = преобразование модели в словарь/JSON.

В Pydantic v2:

* `model_dump()` -> `dict`;
* `model_dump_json()` -> JSON-строка.

```python
user = UserCreate(username="ibra", email="ibra@example.com", age=21)
payload = user.model_dump()
json_str = user.model_dump_json()
```

---

## 5. `model_config`

Настройки поведения схемы.

```python
from pydantic import BaseModel, ConfigDict


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str
```

Полезные опции:

* `extra="forbid"` -> запрет лишних полей;
* `from_attributes=True` -> чтение данных из ORM-объекта;
* `populate_by_name=True` -> поддержка alias при создании.

---

## 6. `from_attributes=True`

Нужно для преобразования ORM-объекта в Pydantic response-схему.

```python
from pydantic import BaseModel, ConfigDict


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
```

Тогда можно сделать:

```python
user_read = UserRead.model_validate(user_orm_object)
```

Без `from_attributes=True` это часто падает, потому что Pydantic ожидает `dict`, а не ORM instance.

---

## 7. `model_validate()`

Универсальный вход для валидации:

```python
data = {"username": "ibra", "email": "ibra@example.com", "age": 21}
user = UserCreate.model_validate(data)
```

Также работает с ORM (если `from_attributes=True`):

```python
user_read = UserRead.model_validate(user_orm)
```

---

## 8. `model_dump()`

Правильный способ отдать схему наружу как `dict`.

```python
result = user_read.model_dump()
```

С фильтрами:

```python
result_public = user_read.model_dump(exclude={"email"})
```

---

## 9. DTO / Schemas

DTO (Data Transfer Object) в FastAPI обычно выражается через Pydantic-схемы.

Задача DTO:

* отделить транспортный контракт API от внутренних моделей/сервисов;
* контролировать, что принимает и что возвращает endpoint.

---

## 10. Request schemas

Схемы входа:

```python
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    age: int = Field(ge=18)
```

```python
class UserPatch(BaseModel):
    username: str | None = None
    age: int | None = Field(default=None, ge=18)
```

Использование:

```python
@router.post("/users")
async def create_user(payload: UserCreate):
    ...
```

---

## 11. Response schemas

Схемы выхода:

```python
class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
```

```python
@router.get("/users/{user_id}", response_model=UserRead)
async def get_user(user_id: int):
    user = await service.get_user(user_id)
    return user
```

Что важно:

* в ответ попадут только поля `UserRead`;
* внутренние поля не утекут случайно.

---

## 12. Ошибка: не смешивать ORM-модели и API-схемы

Антипаттерн:

* принимать/возвращать SQLAlchemy-модель напрямую в API-слое.

Почему это плохо:

1. утечка внутренних полей (`password_hash`, flags, внутренние id);
2. жёсткая связность между БД и API;
3. хуже контроль валидации;
4. сложнее версионировать контракт API.

Правильный подход:

* ORM-модели (`models/*`) только для слоя хранения;
* Pydantic-схемы (`schemas/*`) только для API-контрактов.

Слой преобразования:

```python
user_read = UserRead.model_validate(user_orm)
```

---

## 13. Рекомендуемый набор схем

Для сущности `User` обычно делают:

1. `UserCreate` (POST);
2. `UserPatch` (PATCH);
3. `UserRead` (GET);
4. `UserListItem` (краткий список);
5. `ApiResponse[UserRead]` или единый envelope без generic.

---

## 14. Мини-практика

```python
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, EmailStr, Field

router = APIRouter(prefix="/users", tags=["Users"])


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=3, max_length=32)
    email: EmailStr
    age: int = Field(ge=18, le=120)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: EmailStr
    age: int


@router.post("/", response_model=UserRead, status_code=201)
async def create_user(payload: UserCreate):
    user = await user_service.create(payload)
    return UserRead.model_validate(user)
```

---

## 15. Итог

Правильная логика:

1. `BaseModel` для всех API-схем.
2. `Field` и строгие ограничения.
3. `model_config(extra="forbid")` для строгого входа.
4. `from_attributes=True` для ORM -> schema.
5. `model_validate()` и `model_dump()` как стандартные точки преобразования.
6. Никогда не смешивать ORM-модели и API-схемы в одном слое.
