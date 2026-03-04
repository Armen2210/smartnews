import asyncio
import logging
import httpx

from config import API_BASE_URL, BOT_SECRET

logger = logging.getLogger(__name__)


async def request_with_retry(method: str, url: str, headers: dict, json: dict | None = None):
    for attempt in range(2):  # 1 retry
        try:
            async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers)
                else:
                    response = await client.post(url, headers=headers, json=json)

            if response.status_code == 200:
                return response.json()

            logger.error(f"API ERROR {response.status_code}: {response.text}")
            return None

        except Exception as e:
            logger.error(f"HTTPX ERROR (attempt {attempt + 1}): {e}")
            await asyncio.sleep(1)

    return None


async def get_news(telegram_id: int):
    url = f"{API_BASE_URL}/api/users/me/news/"
    headers = {
        "X-Telegram-ID": str(telegram_id),
        "X-BOT-SECRET": BOT_SECRET,
    }
    return await request_with_retry("GET", url, headers)


async def toggle_favorite(telegram_id: int, news_id: int):
    url = f"{API_BASE_URL}/api/favorites/toggle-bot/"
    headers = {
        "X-Telegram-ID": str(telegram_id),
        "X-BOT-SECRET": BOT_SECRET,
    }
    payload = {"news_id": news_id}
    return await request_with_retry("POST", url, headers, json=payload)


async def get_favorites(telegram_id: int):
    url = f"{API_BASE_URL}/api/users/me/favorites/"
    headers = {
        "X-Telegram-ID": str(telegram_id),
        "X-BOT-SECRET": BOT_SECRET,
    }
    return await request_with_retry("GET", url, headers)