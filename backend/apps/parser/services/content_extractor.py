from __future__ import annotations

from bs4 import BeautifulSoup

from .errors import ContentExtractionError
from .html_cleaner import clean_html
from .http_client import get


def extract_text(mapped: dict) -> str:
    raw = mapped.get("content") or mapped.get("summary")
    if raw:
        return clean_html(raw)

    url = mapped.get("url")
    if not url:
        return ""

    try:
        response = get(url, timeout=15)
    except Exception as exc:
        raise ContentExtractionError(str(exc)) from exc

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()

    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    return clean_html(" ".join(filter(None, paragraphs)))