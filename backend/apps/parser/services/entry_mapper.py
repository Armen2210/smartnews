from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Tuple

from django.utils import timezone


def _get_entry_value(entry: Any, key: str) -> Any:
    """
    Надёжно достаёт значение из entry, который может быть:
    - dict
    - feedparser.util.FeedParserDict (ведёт себя как dict, но иногда лучше поддержать getattr)
    - любой объект с атрибутами
    """
    # dict / FeedParserDict
    try:
        if hasattr(entry, "get"):
            val = entry.get(key)
            if val is not None:
                return val
    except Exception:
        pass

    # object attribute
    try:
        return getattr(entry, key)
    except Exception:
        return None


def _parse_published(entry) -> tuple[datetime, bool]:
    raw = entry.get("published_parsed") or entry.get("updated_parsed")

    if not raw:
        return timezone.now(), True

    try:
        # правильная конвертация struct_time → datetime
        dt = datetime.fromtimestamp(time.mktime(raw))

        # делаем timezone-aware
        dt = timezone.make_aware(dt, timezone=timezone.get_current_timezone())

        return dt, False

    except Exception as e:
        print("DATE PARSE ERROR:", e)
        return timezone.now(), True


def map_entry(entry: Any, source) -> Tuple[dict, bool]:
    """
    Маппит RSS entry в словарь для persister/pipeline.
    """
    published_at, is_missing = _parse_published(entry)

    title = (_get_entry_value(entry, "title") or "").strip()[:500]
    url = (_get_entry_value(entry, "link") or "").strip()

    summary = _get_entry_value(entry, "summary") or ""

    content = ""
    raw_content = _get_entry_value(entry, "content")
    if raw_content:
        # обычно это список словарей [{'value': '...'}]
        try:
            content = (raw_content[0] or {}).get("value", "") if isinstance(raw_content, list) else ""
        except Exception:
            content = ""

    return {
        "title": title,
        "url": url,
        "summary": summary,
        "content": content,
        "published_at": published_at,
        "source": source,
        "category": getattr(source, "default_category", None),
    }, is_missing