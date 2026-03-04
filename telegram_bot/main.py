import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import BOT_TOKEN
from services.api_client import get_news, toggle_favorite, get_favorites
from services.formatter import format_news
from keyboards import get_news_keyboard
from state import set_user_state, get_user_state, update_index


# =========================================
# 🔹 Logging
# =========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# =========================================
# 🔹 Bot init
# =========================================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# =========================================
# 🔹 /start
# =========================================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    telegram_id = message.from_user.id
    logger.info(f"{telegram_id} | action=start")

    await message.answer("Привет! Напиши /news чтобы получить новости 📰")


# =========================================
# 🔹 /news
# =========================================
@dp.message(Command("news"))
async def news_handler(message: types.Message):
    telegram_id = message.from_user.id
    logger.info(f"{telegram_id} | action=news")

    news_list = await get_news(telegram_id)

    if not news_list:
        await message.answer("❌ Не удалось получить новости")
        return

    set_user_state(telegram_id, news_list)

    news = news_list[0]

    await message.answer(
        format_news(news, 0, len(news_list)),
        reply_markup=get_news_keyboard(news)
    )


# =========================================
# 🔹 NEXT
# =========================================
@dp.callback_query(lambda c: c.data == "next")
async def next_news(callback: types.CallbackQuery):
    telegram_id = callback.from_user.id
    logger.info(f"{telegram_id} | action=next")

    state = get_user_state(telegram_id)

    # 🔄 fallback — если состояние потеряно
    if not state:
        news_list = await get_news(telegram_id)

        if not news_list:
            await callback.answer("❌ Не удалось получить новости")
            return

        set_user_state(telegram_id, news_list)

        news = news_list[0]

        await callback.message.answer(
            format_news(news, 0, len(news_list)),
            reply_markup=get_news_keyboard(news)
        )

        await callback.answer("🔄 Состояние восстановлено")
        return

    news_list = state["news_list"]
    index = state["index"] + 1

    # 🔄 если список закончился — новый запрос
    if index >= len(news_list):
        news_list = await get_news(telegram_id)

        if not news_list:
            await callback.answer("❌ Не удалось обновить новости")
            return

        set_user_state(telegram_id, news_list)
        index = 0

        await callback.answer("🔄 Обновлено")

    else:
        update_index(telegram_id, index)

    news = news_list[index]

    await callback.message.edit_text(
        format_news(news, index, len(news_list)),
        reply_markup=get_news_keyboard(news)
    )


# =========================================
# ⭐ FAVORITE
# =========================================
@dp.callback_query(lambda c: c.data == "fav")
async def favorite_handler(callback: types.CallbackQuery):
    telegram_id = callback.from_user.id
    logger.info(f"{telegram_id} | action=fav")

    state = get_user_state(telegram_id)

    # 🔄 fallback если состояние потеряно
    if not state:
        news_list = await get_news(telegram_id)

        if not news_list:
            await callback.answer("❌ Не удалось получить новости")
            return

        set_user_state(telegram_id, news_list)
        news = news_list[0]

        await callback.message.answer(
            format_news(news, 0, len(news_list)),
            reply_markup=get_news_keyboard(news)
        )

        await callback.answer("🔄 Состояние восстановлено")
        return

    news = state["news_list"][state["index"]]

    result = await toggle_favorite(telegram_id, news["id"])

    if not result:
        await callback.answer("❌ Ошибка")
        return

    # 🔥 обновляем локальное состояние
    news["is_favorite"] = result["status"] == "added"

    await callback.answer(
        "⭐ Добавлено" if news["is_favorite"] else "❌ Удалено"
    )

    await callback.message.edit_reply_markup(
        reply_markup=get_news_keyboard(news)
    )


# =========================================
# ⭐ /favorites
# =========================================
@dp.message(Command("favorites"))
async def favorites_handler(message: types.Message):
    telegram_id = message.from_user.id
    logger.info(f"{telegram_id} | action=favorites")

    news_list = await get_favorites(telegram_id)

    if news_list is None:
        await message.answer("❌ Ошибка при получении избранного")
        return

    if not news_list:
        await message.answer("⭐ У тебя пока нет избранных новостей")
        return

    set_user_state(telegram_id, news_list)

    news = news_list[0]

    await message.answer(
        format_news(news, 0, len(news_list)),
        reply_markup=get_news_keyboard(news)
    )


# =========================================
# 🔹 запуск
# =========================================
async def main():
    logger.info("🚀 Bot started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())