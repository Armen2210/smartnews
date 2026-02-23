# 🚀 SmartNews Backend

Backend-сервис для агрегации, обработки и доставки новостей:
- сбор из RSS-источников (Celery)
- сохранение новостей, источников и категорий
- API для новостей и избранного
- инфраструктура: Redis, логирование, health-check

---

## 🧱 Stack

- Python 3.11
- Django 5 + Django REST Framework
- Celery 5 + Redis
- SQLite (dev) / PostgreSQL (prod)
- Docker / Docker Compose

---

## 📦 Features

### 🔹 News & Users
- Хранение новостей, категорий, источников
- Пользователи (Django auth)
- Избранные новости (Favorite)
- Предпочтения по категориям (UserPreferences)

### 🔹 Parser (RSS)
- Загрузка активных источников
- Чтение RSS через `feedparser`
- Маппинг entries → News
- Извлечение текста (fallback через HTTP + HTML parsing)
- Дедупликация
- Метрики пайплайна (создано/дубликаты/ошибки/пустой текст и т.д.)
- Логирование выполнения задач в отдельную модель TaskLog (приложение `tasklog`)

### 🔹 Infrastructure
- Celery worker (асинхронная обработка)
- Redis (broker + result backend)
- Логирование в файл `backend/logs/app.log`
- Health-check endpoints: `/health/` и `/api/health/`

---

## 📁 Project Structure (актуально по проекту)


smartnews/
├── backend/
│ ├── apps/
│ │ ├── ai_service/
│ │ │ ├── migrations/
│ │ │ ├── admin.py
│ │ │ ├── apps.py
│ │ │ ├── models.py
│ │ │ ├── tasks.py
│ │ │ ├── tests.py
│ │ │ └── views.py
│ │ │
│ │ ├── news/
│ │ │ ├── migrations/
│ │ │ ├── admin.py
│ │ │ ├── apps.py
│ │ │ ├── models.py
│ │ │ ├── serializers.py
│ │ │ ├── urls.py
│ │ │ ├── views.py
│ │ │ └── tests.py
│ │ │
│ │ ├── users/
│ │ │ ├── migrations/
│ │ │ ├── admin.py
│ │ │ ├── apps.py
│ │ │ ├── models.py
│ │ │ ├── serializers.py
│ │ │ ├── urls.py
│ │ │ ├── views.py
│ │ │ └── tests.py
│ │ │
│ │ ├── tasklog/
│ │ │ ├── migrations/
│ │ │ ├── admin.py
│ │ │ ├── apps.py
│ │ │ ├── models.py
│ │ │ ├── views.py
│ │ │ └── tests.py
│ │ │
│ │ └── parser/
│ │ ├── api/
│ │ │ ├── serializers.py
│ │ │ ├── urls.py
│ │ │ └── views.py
│ │ ├── migrations/
│ │ ├── services/
│ │ │ ├── content_extractor.py
│ │ │ ├── dedup.py
│ │ │ ├── entry_mapper.py
│ │ │ ├── errors.py
│ │ │ ├── html_cleaner.py
│ │ │ ├── http_client.py
│ │ │ ├── metrics.py
│ │ │ ├── persister.py
│ │ │ ├── pipeline.py
│ │ │ ├── rss_reader.py
│ │ │ ├── source_loader.py
│ │ │ └── tasklog_resolver.py
│ │ ├── admin.py
│ │ ├── apps.py
│ │ ├── models.py
│ │ ├── tasks.py
│ │ ├── views.py
│ │ └── tests.py
│ │
│ ├── config/
│ │ ├── settings/
│ │ │ ├── base.py
│ │ │ ├── local.py
│ │ │ └── prod.py
│ │ ├── celery.py
│ │ ├── health.py
│ │ ├── urls.py
│ │ ├── asgi.py
│ │ └── wsgi.py
│ │
│ ├── logs/
│ │ └── app.log
│ │
│ ├── .env
│ ├── .env.example
│ ├── celerybeat-schedule.dat
│ ├── celerybeat-schedule.dir
│ ├── celerybeat-schedule.bak
│ ├── db.sqlite3
│ ├── manage.py
│ ├── docker-compose.yml
│ ├── Dockerfile
│ └── requirements.txt
│
├── .gitattributes
├── LICENSE
└── README.md


---

## 🌐 API Endpoints

### 🔹 News

#### Получить список новостей

GET /api/news/


Фильтр по категории (slug):

GET /api/news/?category=politics


#### Получить одну новость

GET /api/news/<id>/


---

### 🔹 Favorites

#### Toggle избранного

POST /api/favorites/toggle/


Body:
```json
{
  "news_id": 1
}

Ответ:

{"status": "added"}

или

{"status": "removed"}
❤️ Health-check
Endpoint	Description
/health/	Проверка backend
/api/health/	Проверка API

Ответ:

{"status": "ok"}
⚙️ Environment Variables

Файл: backend/.env

Пример (backend/.env.example):

DJANGO_DEBUG=1
DJANGO_SECRET_KEY=unsafe-dev-key

DATABASE_URL=sqlite:///db.sqlite3

REDIS_URL=redis://localhost:6379/0

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
💻 Local Development (Windows)
1) Установить зависимости
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
2) Redis (проще через Docker)
docker run -p 6379:6379 --name smartnews-redis -d redis:7
3) Миграции + запуск Django
python manage.py migrate
python manage.py runserver
4) Celery Worker (Windows)
celery -A config worker -l info -P solo

⚠️ На Windows используем -P solo.

5) Celery Beat (если нужен планировщик)
celery -A config beat -l info
🔁 Celery Tasks
Парсинг RSS-источников

Запуск из Django shell:

from apps.parser.tasks import parse_sources_task
parse_sources_task.delay()
📝 Logging

Логи пишутся в:

backend/logs/app.log
🧠 Notes / Known Issues

На Windows prefork работает нестабильно → используем -P solo.

Для production рекомендуется Linux + PostgreSQL.

✅ Status
Component	Status
Models	✅
Admin	✅
API (News)	✅
API (Favorites)	✅
Parser (RSS)	✅
Redis	✅
Celery Worker	✅
Logging	✅
Health-check	✅
📈 Next Steps

Пересказ через AI (интеграция в ai_service)

Планировщик (Celery Beat) для регулярного парсинга

Telegram bot

PostgreSQL (prod)

Авторизация (JWT / Telegram ID)

Персональные подборки/рассылки