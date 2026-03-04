# 🚀 SmartNews (Backend + Telegram Bot)

SmartNews — MVP-сервис агрегации и доставки новостей:
- **backend (Django + DRF)** — источник истины (БД, логика, API)
- **Telegram-бот (aiogram)** — UI слой, работает только через HTTP API backend (без прямого доступа к БД)
- **фоновые задачи (Celery + Redis)** — парсинг, AI-summary, ежедневная рассылка дайджеста

---

## 🧱 Stack

### Backend
- Python 3.11
- Django 5 + Django REST Framework
- Celery + Redis
- SQLite (dev) / PostgreSQL (prod)
- Docker / Docker Compose
- Health-check: `/health/` и `/api/health/`
- Логи: `backend/logs/app.log`

### Telegram Bot
- Python 3.11
- aiogram
- httpx (async)
- python-dotenv

---

## ✅ Главные принципы архитектуры (ТЗ №5)

- `backend/` — **источник истины** (БД, бизнес-логика, API, Celery-задачи)
- `telegram_bot/` — **отдельное приложение (НЕ Django)**
- бот **не работает напрямую с БД**
- бот общается с backend **только по HTTP API**
- идентификация Telegram-пользователя на backend (MVP-safe) — через заголовки:
  - `X-Telegram-ID`
  - `X-BOT-SECRET`

---

## 🔐 Секреты и Git

- Реальные секреты не должны попадать в репозиторий.
- `.env` файлы исключены через `.gitignore`.
- Если `.env` когда-либо попадал в историю Git — нужно **перевыпустить**:
  - `BOT_TOKEN` (BotFather)
  - `BOT_SECRET`
  - `DJANGO_SECRET_KEY`

Проверка, что `.env` не отслеживается Git:
```bash
git ls-files backend/.env
git ls-files telegram_bot/.env

Если команды ничего не выводят — всё ок.

⚙️ Запуск проекта (локально, Windows)
1) Backend

Открой терминал в папке backend/ и активируй окружение:

cd backend
.\.venv\Scripts\activate
python manage.py runserver

Backend будет доступен:

http://127.0.0.1:8000/

Health-check:

GET /health/ → {"status":"ok"}

GET /api/health/ → {"status":"ok"}

2) Redis (нужен для Celery)

Celery использует Redis на localhost:6379 (обычно redis://localhost:6379/0).

Если Redis не запущен — задачи Celery работать не будут.

3) Celery worker (backend)

В отдельном терминале:

cd backend
.\.venv\Scripts\activate
celery -A config worker -l info -P solo
4) Telegram Bot

Открой терминал в папке telegram_bot/ и активируй окружение:

cd telegram_bot
.\.venv\Scripts\activate
python main.py
🔐 Переменные окружения (.env)
backend/.env

Минимально необходимо:

DJANGO_SECRET_KEY=...
BOT_SECRET=...
BOT_TOKEN=...        # нужен для Celery-рассылки (backend -> Telegram API)
REDIS_URL=redis://localhost:6379/0
telegram_bot/.env

Ожидается:

BOT_TOKEN=...
API_BASE_URL=http://127.0.0.1:8000
BOT_SECRET=...

Рекомендуется использовать http://127.0.0.1:8000, чтобы избежать проблем с localhost.

🔌 API (важное для Telegram-бота)
Health

GET /health/

GET /api/health/

Новости (общий API)

GET /api/news/

Новости для Telegram-бота (без Django-auth)

GET /api/users/me/news/

Headers:

X-Telegram-ID: <int>

X-BOT-SECRET: <secret>

Правила:

backend возвращает не более 10 новостей

выдаются только новости с summary_status = done

Toggle избранного для Telegram-бота

POST /api/favorites/toggle-bot/

Headers:

X-Telegram-ID: <int>

X-BOT-SECRET: <secret>

Body:

{"news_id": 123}

Response:

{"status":"added"} / {"status":"removed"}

Список избранного для Telegram-бота

GET /api/users/me/favorites/

Headers:

X-Telegram-ID: <int>

X-BOT-SECRET: <secret>

🤖 Telegram Bot — команды

/start — приветствие

/news — показать новости + листание

/favorites — показать избранное

Inline-кнопки под новостью:

➡ Следующая

⭐ В избранное / ❌ Убрать

🔗 Открыть (показывается только если url начинается с http/https)

Устойчивость (ТЗ №5):

если состояние (state) потеряно → бот запрашивает новости заново (fallback)

если список закончился → бот запрашивает новости заново

если backend недоступен → выводится сообщение “Сервис временно недоступен”

📤 Ежедневная рассылка (backend Celery)

По ТЗ №5:

рассылку делает backend напрямую через Telegram API (бот не участвует)

5–10 новостей (у нас сейчас 5)

ограничение скорости ~1 сообщение/сек

обработка ошибок:

429 Too Many Requests → ожидание retry_after и повтор

403 Forbidden (пользователь заблокировал) → удаление/деактивация пользователя

защита от дублей:

ключ вида digest:YYYY-MM-DD (в Redis или БД), чтобы не отправлять повторно в тот же день

⚠️ Важно про модели пользователей (MVP)

В backend есть модель TelegramUser.
На текущем этапе TelegramUser не связан с django.contrib.auth.models.User.
Это допустимое MVP-упрощение.

📁 Project Structure (АКТУАЛЬНО по твоим скринам)
smartnews/
├── .venv/
├── backend/
│   ├── .venv/
│   ├── apps/
│   │   ├── ai_service/
│   │   │   ├── migrations/
│   │   │   │   └── __init__.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   └── gpt_client.py
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── tasks.py
│   │   │   ├── tests.py
│   │   │   └── views.py
│   │   ├── news/
│   │   │   ├── migrations/
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
│   │   ├── parser/
│   │   │   ├── api/
│   │   │   │   ├── serializers.py
│   │   │   │   ├── urls.py
│   │   │   │   └── views.py
│   │   │   ├── migrations/
│   │   │   │   └── __init__.py
│   │   │   ├── services/
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
│   │   │   │   ├── tasklog_resolver.py
│   │   │   │   └── __init__.py
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── tasks.py
│   │   │   ├── tests.py
│   │   │   └── views.py
│   │   ├── tasklog/
│   │   │   ├── migrations/
│   │   │   │   ├── 0001_initial.py
│   │   │   │   └── __init__.py
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py
│   │   │   ├── tests.py
│   │   │   └── views.py
│   │   └── users/
│   │       ├── migrations/
│   │       │   ├── 0001_initial.py
│   │       │   ├── 0002_telegramuser.py
│   │       │   └── __init__.py
│   │       ├── __init__.py
│   │       ├── admin.py
│   │       ├── apps.py
│   │       ├── models.py
│   │       ├── serializers.py
│   │       ├── tasks.py
│   │       ├── tests.py
│   │       ├── urls.py
│   │       └── views.py
│   ├── config/
│   │   ├── settings/
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
│   ├── logs/
│   │   └── app.log
│   ├── .env
│   ├── .env.example
│   ├── __init__.py
│   ├── celerybeat-schedule.bak
│   ├── celerybeat-schedule.dat
│   ├── celerybeat-schedule.dir
│   ├── db.sqlite3
│   ├── docker-compose.yml
│   ├── manage.py
│   └── requirements.txt
├── telegram_bot/
│   ├── .venv/
│   ├── handlers/              # сейчас пустая (задел на будущее)
│   ├── services/
│   │   ├── api_client.py
│   │   └── formatter.py
│   ├── .env
│   ├── config.py
│   ├── keyboards.py
│   ├── main.py
│   ├── requirements.txt
│   └── state.py
├── .gitattributes
├── .gitignore
├── LICENSE
└── README.md
🧪 Примечания по разработке

Если backend пишет No module named 'django' — активировано не то окружение:

backend: backend/.venv

bot: telegram_bot/.venv

Если Celery ругается на Redis — проверь, что Redis запущен и порт 6379 доступен.

Если Telegram API отвечает bots can't send messages to bots — в базе мог оказаться telegram_id самого бота (нужно удалить такую запись из TelegramUser).

✅ Статус по ТЗ №5

/start работает ✅

/news работает ✅

навигация “Следующая” работает ✅

избранное toggle работает ✅

ссылки проверяются ✅ (кнопка показывается только при валидном url)

fallback при потере state ✅

рассылка backend Celery ✅

защита от дублей ✅

обработка 429/403 ✅

устойчивость при ошибках ✅