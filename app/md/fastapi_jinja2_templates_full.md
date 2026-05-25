# FastAPI + Jinja2: Полный Разбор С HTML И Мини-Фронтом

## 0. Цель

Материал покрывает:

* зачем нужен Jinja2 в FastAPI;
* базовый синтаксис шаблонов;
* подробная работа с типами данных в `context`;
* детальный разбор циклов и условий;
* inheritance (`base.html` + дочерние шаблоны);
* циклы, условия, фильтры, макросы;
* подключение CSS/JS и статических файлов;
* мини-фронт пример (карточки постов + поиск на клиенте);
* безопасность (`autoescape`, `|safe`, XSS);
* типичные ошибки и как их избегать.

---

## 1. Что такое Jinja2

`Jinja2` это шаблонизатор:

* ты пишешь HTML-шаблон;
* сервер подставляет данные в шаблон;
* клиент получает готовую HTML-страницу.

Jinja2 полезен, когда:

* нужен server-side rendered (SSR) интерфейс;
* есть админка/внутренний кабинет;
* хочешь быстрый фронт без тяжелого SPA.

---

## 2. Установка и подключение в FastAPI

Установка:

```bash
pip install jinja2
```

Базовая интеграция:

```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Главная",
            "username": "Ibragim",
        },
    )
```

Важно: в `TemplateResponse` всегда передавай `request`.

---

## 3. Структура проекта

Рекомендуемая структура:

```text
app/
  main.py
  templates/
    base.html
    index.html
    components/
      post_card.html
  static/
    css/
      app.css
    js/
      app.js
```

---

## 4. Синтаксис Jinja2

### 4.1 Как читается шаблон

В Jinja2 есть 3 базовые конструкции:

* `{{ ... }}`: вывести значение в HTML;
* `{% ... %}`: выполнить логику (цикл, условие, block, include);
* `{# ... #}`: комментарий в шаблоне (в HTML не попадает).

Пример:

```jinja2
<h1>{{ title }}</h1>
{% if is_admin %}
  <p>Роль: admin</p>
{% endif %}
{# служебная заметка разработчика #}
```

### 4.2 Типы данных в шаблоне

Jinja2 не «изобретает» свои типы, а работает с Python-данными из `context`.

`str`:

```jinja2
<p>{{ username }}</p>
<p>{{ username|upper }}</p>
```

`int`/`float`:

```jinja2
<p>Заказов: {{ orders_count }}</p>
<p>Сумма: {{ '%.2f'|format(total_price) }} ₽</p>
```

`bool`:

```jinja2
{% if is_authenticated %}
  <a href="/profile">Профиль</a>
{% else %}
  <a href="/login">Войти</a>
{% endif %}
```

`None`:

```jinja2
<p>{{ user.bio or 'Описание не заполнено' }}</p>
```

`list`:

```jinja2
{% for tag in tags %}
  <span>{{ tag }}</span>
{% endfor %}
```

`dict` и объекты:

```jinja2
<h3>{{ post.title }}</h3>
<h3>{{ post['title'] }}</h3>
<p>{{ user.created_at }}</p>
```

Практика: в шаблон лучше передавать уже подготовленные данные (DTO/Pydantic), а не «сырые» ORM-сущности с ленивыми связями.

### 4.3 Циклы: как работают и где ошибаются

Базовый цикл:

```jinja2
<ul>
  {% for item in items %}
    <li>{{ item }}</li>
  {% endfor %}
</ul>
```

Полезные переменные `loop`:

```jinja2
{% for post in posts %}
  <p>
    {{ loop.index }} / {{ loop.length }}
    {% if loop.first %}(первый){% endif %}
    {% if loop.last %}(последний){% endif %}
  </p>
{% endfor %}
```

Пустой список можно обработать через `else`:

```jinja2
{% for post in posts %}
  <article>{{ post.title }}</article>
{% else %}
  <p>Постов пока нет.</p>
{% endfor %}
```

Частая ошибка: ожидать, что `for` будет итерировать `None`. Если переменная может быть `None`, передавай пустой список на backend.

### 4.4 Условия: truthy/falsy и читаемость

`if` в Jinja2 использует обычную truthy/falsy-логику Python:

* falsy: `None`, `False`, `0`, `''`, `[]`, `{}`;
* truthy: почти все остальные значения.

Пример:

```jinja2
{% if user and user.is_active %}
  <p>Активный пользователь</p>
{% elif user %}
  <p>Пользователь не активен</p>
{% else %}
  <p>Гость</p>
{% endif %}
```

Для безопасности проверяй объект перед доступом к полям (`user and user.email`), если `user` может быть `None`.

### 4.5 Пример `context` с типами из FastAPI

```python
from datetime import datetime

return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={
        "title": "Dashboard",              # str
        "orders_count": 12,                 # int
        "total_price": 3490.5,              # float
        "is_authenticated": True,           # bool
        "user": {"bio": None},            # dict with None
        "tags": ["fastapi", "jinja2"],   # list[str]
        "posts": [{"title": "Hello"}],   # list[dict]
        "created_at": datetime.utcnow(),    # datetime
    },
)
```

### 4.6 Комментарии

```jinja2
{# Это комментарий, в HTML не попадет #}
```

---

## 5. Наследование шаблонов

`templates/base.html`:

```html
<!doctype html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{% block title %}My App{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', path='css/app.css') }}" />
  </head>
  <body>
    <header class="topbar">
      <h1>Study Board</h1>
      <button id="themeBtn" type="button">Сменить тему</button>
    </header>

    <main class="container">
      {% block content %}{% endblock %}
    </main>

    <script src="{{ url_for('static', path='js/app.js') }}"></script>
  </body>
</html>
```

`templates/index.html`:

```jinja2
{% extends "base.html" %}

{% block title %}Лента постов{% endblock %}

{% block content %}
  <section class="hero">
    <h2>Привет, {{ username }}!</h2>
    <p>Найди пост по заголовку:</p>
    <input id="searchInput" type="text" placeholder="Например: FastAPI" />
  </section>

  <section id="postGrid" class="grid">
    {% for post in posts %}
      <article class="card" data-title="{{ post.title|lower }}">
        <h3>{{ post.title }}</h3>
        <p>{{ post.body }}</p>
        <span class="tag">{{ post.tag }}</span>
      </article>
    {% else %}
      <p>Пока нет постов.</p>
    {% endfor %}
  </section>
{% endblock %}
```

---

## 6. Мини-фронт: CSS + JS

`static/css/app.css`:

```css
:root {
  --bg: #f7f4ef;
  --surface: #fffdf8;
  --text: #1f2a2e;
  --accent: #c75c36;
  --muted: #6b7478;
}

body {
  margin: 0;
  font-family: "Manrope", "Segoe UI", sans-serif;
  background: radial-gradient(circle at top right, #f2d4c6, var(--bg));
  color: var(--text);
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  background: var(--surface);
  border-bottom: 1px solid #eadfd7;
}

.container {
  max-width: 980px;
  margin: 0 auto;
  padding: 24px;
}

.hero {
  margin-bottom: 20px;
}

#searchInput {
  width: 100%;
  max-width: 320px;
  padding: 10px;
  border: 1px solid #d8c7bb;
  border-radius: 10px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.card {
  background: var(--surface);
  border: 1px solid #eadfd7;
  border-radius: 14px;
  padding: 14px;
}

.tag {
  display: inline-block;
  margin-top: 8px;
  font-size: 12px;
  color: var(--muted);
}

.hidden {
  display: none;
}

body.dark {
  --bg: #111417;
  --surface: #1a2025;
  --text: #e9f0f4;
  --accent: #ff8f5a;
  --muted: #9cadb8;
}
```

`static/js/app.js`:

```javascript
const searchInput = document.getElementById("searchInput");
const cards = document.querySelectorAll("#postGrid .card");
const themeBtn = document.getElementById("themeBtn");

if (searchInput) {
  searchInput.addEventListener("input", (e) => {
    const q = e.target.value.trim().toLowerCase();
    cards.forEach((card) => {
      const title = card.dataset.title || "";
      card.classList.toggle("hidden", !title.includes(q));
    });
  });
}

if (themeBtn) {
  themeBtn.addEventListener("click", () => {
    document.body.classList.toggle("dark");
  });
}
```

Что делает этот мини-фронт:

* сервер отдает готовую HTML страницу;
* JS добавляет клиентский поиск без перезагрузки;
* кнопка переключает тему;
* CSS делает адаптивную сетку карточек.

---

## 7. FastAPI маршрут для этого фронта

```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/posts", response_class=HTMLResponse)
async def posts_page(request: Request):
    posts = [
        {"title": "FastAPI Basics", "body": "Роуты, схемы, DI", "tag": "backend"},
        {"title": "Jinja2 Intro", "body": "Шаблоны и блоки", "tag": "templating"},
        {"title": "SQLAlchemy", "body": "Модели и миграции", "tag": "db"},
    ]
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"username": "Ibragim", "posts": posts},
    )
```

---

## 8. Полезные фильтры и конструкции

Фильтры:

```jinja2
{{ username|upper }}
{{ title|lower }}
{{ text|truncate(50) }}
{{ created_at.strftime('%d.%m.%Y %H:%M') }}
```

`loop` в цикле:

```jinja2
{% for post in posts %}
  <p>#{{ loop.index }} {{ post.title }}</p>
{% endfor %}
```

Объединение строк:

```jinja2
{{ first_name ~ ' ' ~ last_name }}
```

Значение по умолчанию:

```jinja2
{{ bio or 'Описание не заполнено' }}
```

---

## 9. Компоненты через include и макросы

`include`:

```jinja2
{% include "components/post_card.html" %}
```

Макрос:

```jinja2
{% macro badge(text, tone='default') %}
  <span class="badge badge-{{ tone }}">{{ text }}</span>
{% endmacro %}

{{ badge('new', 'success') }}
```

Когда использовать:

* `include` для простых повторяемых кусков;
* `macro` для параметризуемых UI-элементов.

---

## 10. Безопасность и XSS

Jinja2 обычно экранирует HTML автоматически.

Пример безопасного вывода:

```jinja2
<p>{{ user_input }}</p>
```

Опасный вариант:

```jinja2
<p>{{ user_input|safe }}</p>
```

`|safe` используй только если строка уже очищена sanitizer-ом.

Практика:

* не вставляй сырой пользовательский HTML;
* не передавай секреты в шаблон;
* в проде ставь строгий CSP в headers.

---

## 11. Частые ошибки

1. `TemplateNotFound`.

Причина: неверный путь к `templates`.

2. `request is undefined`.

Причина: не передали `request` в `TemplateResponse`.

3. Не грузятся CSS/JS.

Причина: не подключен `app.mount('/static', ...)` или ошибочный `url_for`.

4. Конфликт имен переменных.

Причина: в context передали данные под тем же именем, что и служебная переменная.

---

## 12. Когда Jinja2 подходит, а когда нет

Подходит:

* админки;
* внутренние панели;
* SSR страницы с простой интерактивностью;
* лендинги и контентные страницы.

Не лучший выбор:

* сложный stateful UI (drag/drop, сложные realtime dashboard);
* heavy SPA с большим объемом клиентской логики.

---

## 13. Практический чеклист

1. Создать `templates/` и `static/`.
2. Подключить `Jinja2Templates` и `StaticFiles`.
3. Сделать `base.html` и наследование.
4. Передавать данные через `context`.
5. Добавить минимальный JS только там, где реально нужен.
6. Проверить XSS-риски и не злоупотреблять `|safe`.

---

## 14. Короткий итог

Jinja2 + FastAPI дает быстрый SSR-фронт:

* простая архитектура;
* понятный рендер HTML на сервере;
* легко добавить небольшой интерактивный фронт через CSS/JS;
* хорошо подходит для CRUD-интерфейсов и внутренних приложений.
