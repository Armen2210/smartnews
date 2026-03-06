# 🚀 SmartNews

SmartNews — это MVP-сервис агрегации новостей с AI-пересказом и доставкой через Telegram-бота.

Система автоматически:

* собирает новости из RSS
* извлекает текст статьи
* делает краткий AI-пересказ
* сохраняет данные в БД
* отправляет новости пользователю в Telegram

---

# 🧱 Архитектура системы

Проект состоит из нескольких сервисов:

| Сервис            | Назначение                 |
| ----------------- | -------------------------- |
| **backend**       | Django API и бизнес-логика |
| **postgres**      | база данных                |
| **redis**         | брокер сообщений           |
| **celery_worker** | выполнение фоновых задач   |
| **celery_beat**   | планировщик задач          |
| **telegram_bot**  | пользовательский интерфейс |

---

# 🐳 Docker архитектура

При запуске через Docker поднимаются контейнеры:

```
backend
postgres
redis
celery_worker
celery_beat
telegram_bot
```

Все сервисы запускаются через:

```
docker-compose.yml
```

---

# ⚙️ Технологический стек

### Backend

* Python 3.11
* Django 5
* Django REST Framework

### Асинхронные задачи

* Celery
* Redis

### База данных

* SQLite (development)
* PostgreSQL (Docker)

### Парсинг новостей

* feedparser
* requests
* BeautifulSoup

### AI-пересказ

* ProxyAPI (GPT-4o)

### Telegram-бот

* aiogram
* httpx

---

# 📂 Полная структура проекта

```
smartnews
│
├── backend
│   │
│   ├── apps
│   │   │
│   │   ├── ai_service
│   │   │   ├── migrations
│   │   │   ├── services
│   │   │   │   └── gpt_client.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── tasks.py
│   │   │   ├── tests.py
│   │   │   └── views.py
│   │   │
│   │   ├── news
│   │   │   ├── migrations
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── tests.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   │
│   │   ├── parser
│   │   │   ├── api
│   │   │   │   ├── serializers.py
│   │   │   │   ├── urls.py
│   │   │   │   └── views.py
│   │   │   ├── migrations
│   │   │   ├── services
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── tasks.py
│   │   │   ├── tests.py
│   │   │   └── views.py
│   │   │
│   │   ├── tasklog
│   │   │   ├── migrations
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── tests.py
│   │   │   └── views.py
│   │   │
│   │   └── users
│   │       ├── migrations
│   │       ├── admin.py
│   │       ├── apps.py
│   │       ├── models.py
│   │       ├── permissions.py
│   │       ├── serializers.py
│   │       ├── tasks.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   │
│   ├── config
│   │   ├── settings
│   │   │   ├── base.py
│   │   │   ├── local.py
│   │   │   └── prod.py
│   │   │
│   │   ├── asgi.py
│   │   ├── celery.py
│   │   ├── health.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── logs
│   │   └── app.log
│   │
│   ├── .env.example
│   ├── Dockerfile
│   ├── manage.py
│   └── requirements.txt
│
├── telegram_bot
│   │
│   ├── handlers
│   │
│   ├── services
│   │   ├── api_client.py
│   │   └── formatter.py
│   │
│   ├── .env.example
│   ├── config.py
│   ├── keyboards.py
│   ├── main.py
│   ├── state.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml
├── README.md
├── LICENSE
└── .gitignore
```

---

# 🔐 Переменные окружения

В репозиторий **не добавляются реальные секреты**.

Используются `.env` файлы.

В GitHub добавляются только:

```
.env.example
```

---

## backend/.env.example

```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

DATABASE_URL=sqlite:///db.sqlite3

REDIS_URL=redis://localhost:6379/0

PROXYAPI_API_KEY=your-proxyapi-key
BOT_SECRET=your-bot-secret
BOT_TOKEN=your-telegram-token
```

---

## telegram_bot/.env.example

```
BOT_TOKEN=your-telegram-token
API_BASE_URL=http://127.0.0.1:8000
BOT_SECRET=your-bot-secret
```

---

# 🧪 Локальный запуск

## Backend

```
cd backend

python -m venv .venv
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

Backend:

```
http://127.0.0.1:8000
```

Health check:

```
http://127.0.0.1:8000/health/
```

---

## Celery worker

```
celery -A config worker -l info
```

---

## Celery beat

```
celery -A config beat -l info
```

---

## Telegram bot

```
cd telegram_bot
pip install -r requirements.txt

python main.py
```

---

# 🐳 Запуск через Docker

Из корня проекта:

```
docker compose up --build
```

---

# 🔎 Проверка работы

Backend:

```
http://localhost:8000/health/
```

Ответ:

```
{"status": "ok"}
```

---

# ⚠️ Важные правила

В GitHub **не должны попадать**:

```
.env
.env.docker
.venv
db.sqlite3
logs
celerybeat-schedule*
.idea
```

В репозиторий добавляются только:

```
.env.example
```

---

# 📜 License

MIT License
