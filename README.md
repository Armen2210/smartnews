# 🚀 SmartNews Backend

Backend-сервис для агрегации, обработки и анализа новостей.

---

## 🧱 Stack

- Python 3.11
- Django + DRF
- Celery
- Redis
- Docker / Docker Compose

---

## 📦 Features

- REST API (Django REST Framework)
- Асинхронные задачи (Celery)
- Планировщик задач (Celery Beat)
- Health-check endpoints
- Логирование в файл
- Готовность к Docker-развёртыванию

---

## 📁 Project Structure


backend/
├── apps/
│ ├── parser/
│ └── ai_service/
├── config/
│ ├── settings/
│ │ ├── base.py
│ │ ├── local.py
│ │ └── prod.py
│ ├── celery.py
│ ├── init.py
├── logs/
│ └── app.log
├── manage.py
├── docker-compose.yml
└── Dockerfile


---

## ❤️ Health-check

| Endpoint | Description |
|----------|------------|
| `/health/` | Проверка backend |
| `/api/health/` | Проверка API |

**Ответ:**

```json
{"status": "ok"}
⚙️ Environment Variables

Файл: backend/.env

DJANGO_DEBUG=1
DJANGO_SECRET_KEY=unsafe-dev-key

DATABASE_URL=sqlite:///db.sqlite3

REDIS_URL=redis://redis:6379/0

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
🐳 Run with Docker (recommended)
docker compose up --build
Доступ:

API: http://localhost:8000

Redis: localhost:6379

💻 Local Development (Windows)
1. Redis
docker run -p 6379:6379 --name smartnews-redis -d redis:7
2. Django
cd backend
python manage.py migrate
python manage.py runserver
3. Celery Worker
celery -A config worker -l info -P solo

⚠️ Важно:
Windows → используем -P solo (из-за ограничений multiprocessing)

4. Celery Beat
celery -A config beat -l info
🔁 Celery Tasks
Parser
from apps.parser.tasks import parse_news_stub
parse_news_stub.delay()
AI Service
from apps.ai_service.tasks import summarize_stub
summarize_stub.delay()
📝 Logging

Логи пишутся в:

backend/logs/app.log

Пример:

GET /health/ 200
GET /api/health/ 200
🐳 Docker Configuration
docker-compose.yml
services:
  redis:
    image: redis:7
    ports:
      - "6379:6379"

  web:
    build:
      context: ./backend
    env_file:
      - ./backend/.env
    command: >
      sh -c "python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - redis

  worker:
    build:
      context: ./backend
    env_file:
      - ./backend/.env
    command: celery -A config worker -l info
    volumes:
      - ./backend:/app
    depends_on:
      - redis
      - web

  beat:
    build:
      context: ./backend
    env_file:
      - ./backend/.env
    command: celery -A config beat -l info
    volumes:
      - ./backend:/app
    depends_on:
      - redis
      - web
Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app
⚠️ Redis Configuration
Environment	URL
Docker	redis://redis:6379/0
Local	redis://localhost:6379/0
📌 Known Issues

Celery prefork не работает стабильно на Windows

Используется -P solo для dev-среды

В production рекомендуется Linux / Docker

🧠 Architecture Notes

Django и Celery — отдельные процессы

Celery инициализируется через config/celery.py

Используется shared_task

Redis — broker и result backend

✅ Status
Component	Status
Django	✅
Redis	✅
Celery Worker	✅
Celery Beat	✅
Tasks	✅
Health-check	✅
Logging	✅
📈 Next Steps

Подключение PostgreSQL

Реальный парсер новостей

Интеграция AI (LLM)

Авторизация пользователей

API для управления задачами