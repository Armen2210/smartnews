import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import httpx

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")
BOT_SECRET = os.getenv("BOT_SECRET")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =========================================
# 🧠 STATE (MVP)
# =========================================
user_state = {}


# =========================================
# 🔹 API: получить новости
# =========================================
async def get_news(telegram_id: int):
    url = f"{API_BASE_URL}/api/users/me/news/"

    headers = {
        "X-Telegram-ID": str(telegram_id),
        "X-BOT-SECRET": BOT_SECRET,
    }

    async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
        try:
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                return response.json()
            return None

        except Exception as e:
            print("HTTPX ERROR:", e)
            return None


# =========================================
# 🔹 API: toggle избранного
# =========================================
async def toggle_favorite(telegram_id: int, news_id: int):
    url = f"{API_BASE_URL}/api/favorites/toggle/"

    headers = {
        "X-Telegram-ID": str(telegram_id),
        "X-BOT-SECRET": BOT_SECRET,
    }

    payload = {
        "news_id": news_id
    }

    async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                return response.json()
            return None

        except Exception as e:
            print("HTTPX ERROR:", e)
            return None


# =========================================
# 🔹 КНОПКИ
# =========================================
def get_news_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➡ Следующая", callback_data="next"),
            InlineKeyboardButton(text="⭐ В избранное", callback_data="fav"),
        ]
    ])


# =========================================
# 🔹 формат новости
# =========================================
def format_news(news: dict) -> str:
    return (
        f"📰 {news['title']}\n\n"
        f"{news['summary_text']}\n\n"
        f"Категория: {news['category']}"
    )


# =========================================
# 🔹 /start
# =========================================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Напиши /news чтобы получить новости 📰")


# =========================================
# 🔹 /news
# =========================================
@dp.message(Command("news"))
async def news_handler(message: types.Message):
    telegram_id = message.from_user.id

    news_list = await get_news(telegram_id)

    if not news_list:
        await message.answer("❌ Не удалось получить новости")
        return

    user_state[telegram_id] = {
        "news_list": news_list,
        "index": 0
    }

    news = news_list[0]

    await message.answer(
        format_news(news),
        reply_markup=get_news_keyboard()
    )


# =========================================
# 🔹 NEXT
# =========================================
@dp.callback_query(lambda c: c.data == "next")
async def next_news(callback: types.CallbackQuery):
    telegram_id = callback.from_user.id

    if telegram_id not in user_state:
        await callback.message.answer("⚠️ Начни с /news")
        return

    state = user_state[telegram_id]
    news_list = state["news_list"]
    index = state["index"] + 1

    if index >= len(news_list):
        index = 0

    state["index"] = index
    news = news_list[index]

    await callback.message.edit_text(
        format_news(news),
        reply_markup=get_news_keyboard()
    )


# =========================================
# ⭐ FAVORITE
# =========================================
@dp.callback_query(lambda c: c.data == "fav")
async def favorite_handler(callback: types.CallbackQuery):
    telegram_id = callback.from_user.id

    if telegram_id not in user_state:
        await callback.answer("⚠️ Начни с /news")
        return

    state = user_state[telegram_id]
    news = state["news_list"][state["index"]]

    result = await toggle_favorite(telegram_id, news["id"])

    if not result:
        await callback.answer("❌ Ошибка")
        return

    if result["status"] == "added":
        await callback.answer("⭐ Добавлено")
    else:
        await callback.answer("❌ Удалено")


# =========================================
# 🔹 запуск
# =========================================
async def main():
    print("🚀 Bot started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())