🚀 ОБНОВЛЁННЫЙ README
# 🚀 SmartNews

SmartNews — это MVP-сервис агрегации новостей с AI-пересказом и доставкой через Telegram-бота.

Система автоматически:

- собирает новости из RSS-источников
- извлекает текст статьи
- генерирует краткий AI-пересказ
- сохраняет данные в базе
- отправляет новости пользователю через Telegram

---

# ⚡ Быстрый старт

```bash
git clone <repo>
cd smartnews

cd backend
python -m venv .venv
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_initial_data
python manage.py runserver

В отдельном терминале:

celery -A config worker -l info -P solo
celery -A config beat -l info

В отдельном терминале:

cd telegram_bot
pip install -r requirements.txt
python main.py
🧱 Архитектура системы

Проект построен по микросервисному принципу:

Сервис	Назначение
backend	Django API и бизнес-логика
postgres	база данных
redis	брокер сообщений
celery_worker	выполнение фоновых задач
celery_beat	планировщик задач
telegram_bot	пользовательский интерфейс
🔄 Как работает система

Celery Beat

запускает парсинг RSS (каждые 5 минут)

запускает ежедневную рассылку

Parser

получает RSS

извлекает статьи

очищает HTML

сохраняет новости

AI Service

генерирует краткий пересказ

Backend API

отдаёт данные пользователю

Telegram Bot

получает данные через API

отображает пользователю

⚙️ Основные возможности
🔹 Новости

получение списка новостей

фильтрация по категориям

сортировка по дате

детальная информация

🔹 Пользователь

регистрация через Telegram ID

избранные новости

предпочтения категорий

🔹 Telegram-бот

/start — регистрация

/news — новости

/categories — выбор категорий

/favorites — избранное

🔹 Celery

парсинг RSS

генерация AI summary

ежедневная рассылка (digest) 

# 📂 Структура проекта

```text
smartnews
│
├── backend
│   │
│   ├── .venv
│   ├── apps
│   │   │
│   │   ├── ai_service
│   │   │   ├── migrations
│   │   │   │   └── __init__.py
│   │   │   ├── services
│   │   │   │   ├── __init__.py
│   │   │   │   └── gpt_client.py
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── tasks.py
│   │   │   ├── tests.py
│   │   │   └── views.py
│   │   │
│   │   ├── news
│   │   │   ├── migrations
│   │   │   │   ├── 0001_initial.py
│   │   │   │   └── __init__.py
│   │   │   ├── __init__.py
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
│   │   │   ├── management
│   │   │   │   ├── __init__.py
│   │   │   │   └── commands
│   │   │   │       ├── __init__.py
│   │   │   │       └── seed_initial_data.py
│   │   │   ├── migrations
│   │   │   │   └── __init__.py
│   │   │   ├── services
│   │   │   │   ├── content_extractor.py
│   │   │   │   ├── dedup.py
│   │   │   │   ├── entry_mapper.py
│   │   │   │   ├── errors.py
│   │   │   │   ├── html_cleaner.py
│   │   │   │   ├── http_client.py
│   │   │   │   ├── metrics.py
│   │   │   │   ├── persister.py
│   │   │   │   ├── pipeline.py
│   │   │   │   ├── rss_reader.py
│   │   │   │   ├── source_loader.py
│   │   │   │   └── tasklog_resolver.py
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── tasks.py
│   │   │   ├── tests.py
│   │   │   └── views.py
│   │   │
│   │   ├── tasklog
│   │   │   ├── migrations
│   │   │   │   ├── 0001_initial.py
│   │   │   │   └── __init__.py
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── tests.py
│   │   │   └── views.py
│   │   │
│   │   └── users
│   │       ├── migrations
│   │       │   ├── 0001_initial.py
│   │       │   ├── 0002_telegramuser.py
│   │       │   └── __init__.py
│   │       ├── __init__.py
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
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── local.py
│   │   │   └── prod.py
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── celery.py
│   │   ├── health.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── logs
│   │   └── app.log
│   │
│   ├── tests
│   │   ├── __init__.py
│   │   ├── test_ai_service.py
│   │   ├── test_favorites.py
│   │   ├── test_news_api.py
│   │   ├── test_parser.py
│   │   └── test_telegram_auth.py
│   │
│   ├── .env
│   ├── .env.docker
│   ├── .env.docker.example
│   ├── .env.example
│   ├── __init__.py
│   ├── celerybeat-schedule.bak
│   ├── celerybeat-schedule.dat
│   ├── celerybeat-schedule.dir
│   ├── db.sqlite3
│   ├── Dockerfile
│   ├── manage.py
│   └── requirements.txt
│
├── telegram_bot
│   ├── .venv
│   ├── handlers
│   ├── services
│   │   ├── __init__.py
│   │   ├── api_client.py
│   │   └── formatter.py
│   ├── .env
│   ├── .env.docker
│   ├── .env.docker.example
│   ├── .env.example
│   ├── bot_config.py
│   ├── Dockerfile
│   ├── keyboards.py
│   ├── main.py
│   ├── requirements.txt
│   └── state.py
│
├── .dockerignore
├── .gitattributes
├── .gitignore
├── docker-compose.yml
├── LICENSE
└── README.md 

🔐 Переменные окружения

В репозиторий НЕ добавляются реальные секреты.

Используются .env файлы.

Добавляются только:

.env.example
.env.docker.example
backend/.env.example
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0

PROXYAPI_API_KEY=your-proxyapi-key

BOT_SECRET=your-bot-secret
BOT_TOKEN=your-telegram-token
telegram_bot/.env.example
BOT_TOKEN=your-telegram-token
API_BASE_URL=http://127.0.0.1:8000
BOT_SECRET=your-bot-secret
🧪 Локальный запуск
Backend
cd backend

python -m venv .venv
pip install -r requirements.txt

python manage.py migrate
🔴 ВАЖНО
python manage.py seed_initial_data

Без этого шага API может возвращать пустые данные.

Celery (Windows)
celery -A config worker -l info -P solo
celery -A config beat -l info
Telegram bot
cd telegram_bot
pip install -r requirements.txt
python main.py
🐳 Запуск через Docker
Подготовка env
cp backend/.env.docker.example backend/.env.docker
cp telegram_bot/.env.docker.example telegram_bot/.env.docker

Заполнить:

BOT_TOKEN

BOT_SECRET

PROXYAPI_API_KEY

Запуск
docker compose up --build
🔎 API endpoints
Новости
GET /api/news/
GET /api/news/<id>/
Пользователь
GET /api/users/me/news/
GET /api/users/preferences/
POST /api/users/preferences/toggle/
Избранное
POST /api/favorites/toggle/
🧪 Тесты
python manage.py test tests.test_news_api tests.test_favorites tests.test_telegram_auth tests.test_parser tests.test_ai_service
🔎 Проверка системы

Проверено:

backend API работает

Telegram-бот работает

категории работают

избранное работает

Celery worker работает

Celery beat работает

digest отправляется

⚠️ Ограничения

Celery на Windows требует -P solo

некоторые RSS источники могут быть невалидны

AI зависит от внешнего API (ProxyAPI)

⚠️ Важные правила

В GitHub не должны попадать:

.env
.env.docker
.venv
db.sqlite3
logs
celerybeat-schedule*
.idea
📜 License

MIT License