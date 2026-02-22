from __future__ import annotations

import feedparser

from .errors import RSSReadError

MAX_ENTRIES_PER_SOURCE = 20


def read_entries(rss_url: str) -> list[dict]:
    feed = feedparser.parse(rss_url)
    if getattr(feed, "bozo", False) and not getattr(feed, "entries", None):
        raise RSSReadError(f"Invalid RSS feed: {rss_url}")
    return list(feed.entries[:MAX_ENTRIES_PER_SOURCE])
