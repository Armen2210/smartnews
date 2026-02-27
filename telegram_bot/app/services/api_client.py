import httpx
from app.config import settings


class APIClient:
    def __init__(self):
        self.base_url = settings.BACKEND_URL
        self.bot_secret = settings.BOT_SECRET

    async def get_news(self, telegram_id: int):
        url = f"{self.base_url}/api/users/me/news/"

        headers = {
            "X-Telegram-ID": str(telegram_id),
            "X-BOT-SECRET": self.bot_secret,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)

            if response.status_code == 200:
                return response.json()

            print(f"API ERROR: {response.status_code} {response.text}")
            return None

        except Exception as e:
            print(f"REQUEST FAILED: {e}")
            return None