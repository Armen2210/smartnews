from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_news_keyboard(news: dict):
    if news.get("is_favorite"):
        fav_text = "❌ Убрать"
    else:
        fav_text = "⭐ В избранное"

    buttons = [
        [
            InlineKeyboardButton(text="➡ Следующая", callback_data="next"),
            InlineKeyboardButton(text=fav_text, callback_data="fav"),
        ]
    ]

    if news.get("url") and str(news["url"]).startswith("http"):
        buttons.append(
            [InlineKeyboardButton(text="🔗 Открыть", url=news["url"])]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_categories_keyboard(categories: list[dict]):
    buttons = []

    for category in categories:
        prefix = "✔" if category.get("selected") else "✖"
        text = f"{prefix} {category['name']}"
        callback_data = f"cat:{category['slug']}"

        buttons.append([
            InlineKeyboardButton(text=text, callback_data=callback_data)
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)