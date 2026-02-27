from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.services.api_client import APIClient

router = Router()
api_client = APIClient()


@router.message(Command("news"))
async def news_handler(message: Message):
    telegram_id = message.from_user.id

    await message.answer("Загрузка новостей...")

    news_list = await api_client.get_news(telegram_id)

    if not news_list:
        await message.answer("Сервис временно недоступен")
        return

    if len(news_list) == 0:
        await message.answer("Сегодня пока нет новостей по вашим фильтрам")
        return

    news = news_list[0]

    text = (
        f"📰 {news['title']}\n\n"
        f"{news['summary_text']}\n\n"
        f"📂 Категория: {news['category']}\n"
        f"📅 {news['published_at'][:10]}"
    )

    await message.answer(text)