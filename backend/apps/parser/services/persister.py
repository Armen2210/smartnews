from __future__ import annotations

from django.db import IntegrityError

from .dedup import create_news_if_not_exists


def persist(mapped: dict, text: str) -> tuple[bool, bool]:
    payload = {
        "title": mapped["title"],
        "url": mapped["url"],
        "source": mapped["source"],
        "category": mapped["category"],
        "published_at": mapped["published_at"],
        "original_text": text,
    }

    try:
        _, created = create_news_if_not_exists(payload)
        return created, not created
    except IntegrityError:
        return False, True