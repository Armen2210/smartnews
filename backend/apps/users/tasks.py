import os
import redis
import time
import requests

from datetime import date
from celery import shared_task
from django.conf import settings

from .models import TelegramUser
from apps.news.models import News


redis_client = redis.Redis.from_url(settings.REDIS_URL)

# =========================================
# 📤 Отправка сообщения в Telegram
# =========================================
def send_telegram_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    try:
        response = requests.post(url, json=payload, timeout=10)

        # ✅ Успешно
        if response.status_code == 200:
            return True

        # 🔥 403 — пользователь заблокировал
        if response.status_code == 403:
            print(f"User {chat_id} blocked bot. Removing...")
            TelegramUser.objects.filter(telegram_id=chat_id).delete()
            return False

        # ⚡ 429 — rate limit
        if response.status_code == 429:
            data = response.json()
            retry_after = data.get("parameters", {}).get("retry_after", 1)
            print(f"Rate limited. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)

            # повторная попытка
            retry_response = requests.post(url, json=payload, timeout=10)

            if retry_response.status_code == 200:
                return True

            print("Retry failed:", retry_response.text)
            return False

        print("Telegram error:", response.text)
        return False

    except Exception as e:
        print("Send error:", e)
        return False


# =========================================
# 🧠 Формат новости
# =========================================
def format_news(news: News) -> str:
    return (
        f"📰 {news.title}\n\n"
        f"{news.summary_text}\n\n"
        f"Категория: {news.category}"
    )


# =========================================
# 🚀 Основная задача
# =========================================
@shared_task
def send_daily_digest():
    print("START DIGEST")
    today_key = f"digest:{date.today()}"

    # если уже отправляли сегодня — выходим
    if redis_client.get(today_key):
        print("DIGEST ALREADY SENT TODAY")
        return

    # ставим ключ на 24 часа
    redis_client.setex(today_key, 60 * 60 * 24, "1")

    users = TelegramUser.objects.all()
    news_list = (
        News.objects
        .filter(summary_status=News.SummaryStatus.DONE)
        .order_by("-published_at")[:5]
    )

    for user in users:
        print(f"Send to {user.telegram_id}")

        for news in news_list:
            text = format_news(news)

            send_telegram_message(
                chat_id=user.telegram_id,
                text=text
            )

            # ⚠️ защита от rate limit
            time.sleep(1)

    print("END DIGEST")