import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramBadRequest

from bot_config import BOT_TOKEN
from services.api_client import (
    get_news,
    toggle_favorite,
    get_favorites,
    get_news_by_id,
    get_preferences,
    toggle_preference,
)
from services.formatter import format_news
from keyboards import get_news_keyboard, get_categories_keyboard
from state import set_user_state, get_user_state, update_index


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

session = AiohttpSession(timeout=60)

bot = Bot(
    token=BOT_TOKEN,
    session=session
)

dp = Dispatcher()


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    telegram_id = message.from_user.id
    logger.info(f"{telegram_id} | action=start")

    await message.answer(
        "Привет! Напиши /news чтобы получить новости 📰\n"
        "Или /categories чтобы выбрать интересующие категории."
    )


@dp.message(Command("news"))
async def news_handler(message: types.Message):
    telegram_id = message.from_user.id
    logger.info(f"{telegram_id} | action=news")

    news_list = await get_news(telegram_id)

    if not news_list:
        await message.answer("❌ Не удалось получить новости")
        return

    news_ids = [news["id"] for news in news_list]
    set_user_state(telegram_id, news_ids)

    news = news_list[0]

    await message.answer(
        format_news(news, 0, len(news_list)),
        reply_markup=get_news_keyboard(news)
    )


@dp.message(Command("categories"))
async def categories_handler(message: types.Message):
    telegram_id = message.from_user.id
    logger.info(f"{telegram_id} | action=categories")

    categories = await get_preferences(telegram_id)

    if categories is None:
        await message.answer("❌ Не удалось получить категории")
        return

    if not categories:
        await message.answer("⚠️ Категории пока отсутствуют")
        return

    await message.answer(
        "Выбери интересующие категории:",
        reply_markup=get_categories_keyboard(categories)
    )


@dp.callback_query(lambda c: c.data == "next")
async def next_news(callback: types.CallbackQuery):
    telegram_id = callback.from_user.id
    logger.info(f"{telegram_id} | action=next")

    state = get_user_state(telegram_id)

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


@dp.callback_query(lambda c: c.data == "fav")
async def favorite_handler(callback: types.CallbackQuery):
    telegram_id = callback.from_user.id
    logger.info(f"{telegram_id} | action=fav")

    try:
        await callback.answer()
    except TelegramBadRequest as e:
        logger.warning(f"Callback answer skipped: {e}")

    state = get_user_state(telegram_id)

    if not state:
        await callback.message.answer("⚠️ Сначала вызови /news")
        return

    news_ids = state["news_ids"]
    index = state["index"]
    news_id = news_ids[index]

    news = await get_news_by_id(telegram_id, news_id)

    if not news:
        await callback.message.answer("❌ Не удалось получить новость")
        return

    result = await toggle_favorite(telegram_id, news_id)

    if not result:
        await callback.message.answer("❌ Ошибка при обновлении избранного")
        return

    if result["status"] == "added":
        news["is_favorite"] = True
        result_text = "⭐ Добавлено в избранное"
    else:
        news["is_favorite"] = False
        result_text = "❌ Удалено из избранного"

    try:
        await callback.message.edit_reply_markup(
            reply_markup=get_news_keyboard(news)
        )
    except TelegramBadRequest as e:
        logger.warning(f"Reply markup update skipped: {e}")

    await callback.message.answer(result_text)


@dp.callback_query(lambda c: c.data.startswith("cat:"))
async def category_toggle_handler(callback: types.CallbackQuery):
    telegram_id = callback.from_user.id
    logger.info(f"{telegram_id} | action=toggle_category | data={callback.data}")

    category_slug = callback.data.split(":", 1)[1]

    result = await toggle_preference(telegram_id, category_slug)

    if result is None:
        await callback.answer("❌ Ошибка переключения", show_alert=True)
        return

    categories = await get_preferences(telegram_id)

    if categories is None:
        await callback.answer("❌ Не удалось обновить список", show_alert=True)
        return

    try:
        await callback.message.edit_reply_markup(
            reply_markup=get_categories_keyboard(categories)
        )
    except TelegramBadRequest as e:
        logger.warning(f"Categories markup update skipped: {e}")

    await callback.answer("✅ Обновлено")


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


async def main():
    logger.info("🚀 Bot started...")
    await dp.start_polling(bot, polling_timeout=30)


if __name__ == "__main__":
    asyncio.run(main())