# 🚀 SmartNews Backend

Backend-сервис для агрегации, обработки и доставки новостей с краткими пересказами и поддержкой Telegram-бота.

---

## 🧱 Stack

* Python 3.11
* Django 5
* Django REST Framework
* Celery + Redis
* SQLite (dev) / PostgreSQL (prod)
* Docker / Docker Compose

---

## 📦 Features

### 🔹 Core

* Агрегация новостей (подготовка к парсингу)
* Хранение новостей, категорий и источников
* Генерация и хранение AI-пересказов (подготовлено)

### 🔹 API

* Получение списка новостей
* Фильтрация по категориям
* Детальная информация по новости
* Работа с избранным (toggle)

### 🔹 Users

* Пользователи (Django auth)
* Предпочтения по категориям
* Избранные новости

### 🔹 Infrastructure

* Celery (асинхронные задачи)
* Redis (broker + backend)
* Логирование
* Health-check endpoints

---

## 📁 Project Structure

```
backend/
├── apps/
│   ├── news/          # Новости, категории, источники, API
│   ├── users/         # Пользователи, избранное, предпочтения
│   ├── parser/        # (заготовка под парсер)
│   └── ai_service/    # (заготовка под AI)
│
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── prod.py
│   ├── celery.py
│   ├── urls.py
│   └── health.py
│
├── logs/
│   └── app.log
│
├── manage.py
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 🌐 API Endpoints

### 🔹 News

#### Получить список новостей

```
GET /api/news/
```

Фильтр по категории:

```
GET /api/news/?category=politics
```

Ответ:

```json
[
  {
    "id": 1,
    "title": "Заголовок",
    "summary_text": "Краткий пересказ",
    "category": "politics",
    "source": "BBC",
    "published_at": "2026-02-22T12:00:00Z"
  }
]
```

---

#### Получить одну новость

```
GET /api/news/<id>/
```

---

### 🔹 Favorites

#### Toggle избранного

```
POST /api/favorites/toggle/
```

Body:

```json
{
  "news_id": 1
}
```

Ответ:

```json
{"status": "added"}
```

или

```json
{"status": "removed"}
```

---

## 🧠 Data Models

### News

* title
* url (unique)
* source (FK)
* category (FK)
* published_at
* original_text
* summary_text
* summary_status (pending / processing / done / failed)

### Category

* name (unique)
* slug (unique)

### Source

* name
* url
* is_active

### UserPreferences

* user (OneToOne)
* categories (ManyToMany)

### Favorite

* user + news (unique)

---

## ❤️ Health-check

| Endpoint       | Description      |
| -------------- | ---------------- |
| `/health/`     | Проверка backend |
| `/api/health/` | Проверка API     |

Ответ:

```json
{"status": "ok"}
```

---

## ⚙️ Environment Variables

Файл: `backend/.env`

```
DJANGO_DEBUG=1
DJANGO_SECRET_KEY=unsafe-dev-key

DATABASE_URL=sqlite:///db.sqlite3

REDIS_URL=redis://redis:6379/0

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

---

## 🐳 Run with Docker (recommended)

```
docker compose up --build
```

Доступ:

* API: http://localhost:8000
* Redis: localhost:6379

---

## 💻 Local Development (Windows)

### 1. Redis

```
docker run -p 6379:6379 --name smartnews-redis -d redis:7
```

### 2. Django

```
cd backend
python manage.py migrate
python manage.py runserver
```

### 3. Celery Worker

```
celery -A config worker -l info -P solo
```

⚠️ Windows:
используем `-P solo`

### 4. Celery Beat

```
celery -A config beat -l info
```

---

## 🔁 Celery Tasks (заготовка)

```python
from apps.parser.tasks import parse_news_stub
parse_news_stub.delay()

from apps.ai_service.tasks import summarize_stub
summarize_stub.delay()
```

---

## 📝 Logging

Логи:

```
backend/logs/app.log
```

---

## 🐳 Docker Configuration

(оставляем как есть — уже настроено)

---

## ⚠️ Known Issues

* Celery prefork не работает стабильно на Windows
* Используется `-P solo` для разработки
* В production рекомендуется Linux

---

## 🧠 Architecture Notes

* Django и Celery — отдельные процессы
* Redis — broker и result backend
* Используется `shared_task`
* API построен на DRF
* Архитектура модульная (apps)

---

## ✅ Status

| Component       | Status |
| --------------- | ------ |
| Models          | ✅      |
| Admin           | ✅      |
| API (News)      | ✅      |
| API (Favorites) | ✅      |
| Redis           | ✅      |
| Celery          | ✅      |
| Logging         | ✅      |

---

## 📈 Next Steps

* Парсинг новостей (RSS)
* Интеграция ProxyAPI (AI пересказ)
* Telegram-бот
* PostgreSQL
* Авторизация (JWT / Telegram ID)
* Персонализированные рассылки
