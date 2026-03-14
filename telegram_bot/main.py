import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import BOT_TOKEN
from services.api_client import get_news, toggle_favorite, get_favorites, get_news_by_id
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

    # сохраняем только ID
    news_ids = [news["id"] for news in news_list]

    set_user_state(telegram_id, news_ids)

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

        news_ids = [news["id"] for news in news_list]
        set_user_state(telegram_id, news_ids)

        news = news_list[0]

        await callback.message.answer(
            format_news(news, 0, len(news_ids)),
            reply_markup=get_news_keyboard(news)
        )

        await callback.answer("🔄 Состояние восстановлено")
        return

    news_ids = state["news_ids"]
    index = state["index"] + 1

    # 🔄 если список закончился — новый запрос
    if index >= len(news_ids):
        news_list = await get_news(telegram_id)

        if not news_list:
            await callback.answer("❌ Не удалось обновить новости")
            return

        news_ids = [news["id"] for news in news_list]
        set_user_state(telegram_id, news_ids)

        index = 0
        await callback.answer("🔄 Обновлено")

    else:
        update_index(telegram_id, index)

    news_id = news_ids[index]

    news = await get_news_by_id(telegram_id, news_id)

    if not news:
        await callback.answer("❌ Ошибка загрузки новости")
        return

    await callback.message.edit_text(
        format_news(news, index, len(news_ids)),
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

    if not state:
        await callback.answer("⚠️ Сначала вызови /news")
        return

    news_ids = state["news_ids"]
    index = state["index"]

    news_id = news_ids[index]

    news = await get_news_by_id(telegram_id, news_id)

    if not news:
        await callback.answer("❌ Не удалось получить новость")
        return

    result = await toggle_favorite(telegram_id, news_id)

    if not result:
        await callback.answer("❌ Ошибка")
        return

    if result["status"] == "added":
        news["is_favorite"] = True
        await callback.answer("⭐ Добавлено")
    else:
        news["is_favorite"] = False
        await callback.answer("❌ Удалено")

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

    news_ids = [news["id"] for news in news_list]
    set_user_state(telegram_id, news_ids)

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