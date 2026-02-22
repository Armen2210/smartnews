from apps.news.models import News


def create_news_if_not_exists(payload: dict) -> tuple[object, bool]:
    return News.objects.get_or_create(url=payload["url"], defaults=payload)