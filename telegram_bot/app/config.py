import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    BACKEND_URL = os.getenv("BACKEND_URL")
    BOT_SECRET = os.getenv("BOT_SECRET")


settings = Settings()