from __future__ import annotations

import re

from bs4 import BeautifulSoup

MAX_TEXT_LENGTH = 7000


def clean_html(value: str) -> str:
    soup = BeautifulSoup(value or "", "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_TEXT_LENGTH]