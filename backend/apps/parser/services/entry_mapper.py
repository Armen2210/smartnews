from __future__ import annotations

from datetime import datetime

from django.utils import timezone


def _parse_published(entry: dict) -> tuple[datetime, bool]:
    raw = entry.get("published_parsed") or entry.get("updated_parsed")
    if not raw:
        return timezone.now(), True

    try:
        return datetime(*raw[:6], tzinfo=timezone.utc), False
    except Exception:
        return timezone.now(), True


def map_entry(entry: dict, source) -> tuple[dict, bool]:
    published_at, is_missing = _parse_published(entry)
    return {
        "title": (entry.get("title") or "").strip()[:500],
        "url": (entry.get("link") or "").strip(),
        "summary": entry.get("summary") or "",
        "content": (entry.get("content") or [{}])[0].get("value", "") if entry.get("content") else "",
        "published_at": published_at,
        "source": source,
        "category": getattr(source, "default_category", None),
    }, is_missing