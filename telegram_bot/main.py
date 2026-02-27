import asyncio
from aiogram import Bot, Dispatcher
from app.config import settings
from app.handlers import start, news


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(news.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())