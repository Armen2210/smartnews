def format_news(news: dict, index: int, total: int) -> str:
    return (
        f"📰 {news['title']}\n\n"
        f"{news['summary_text']}\n\n"
        f"📂 Категория: {news['category']}\n"
        f"🌐 Источник: {news['source']}\n"
        f"📅 Дата: {news['published_at'][:10]}\n\n"
        f"📍 {index + 1} / {total}"
    )