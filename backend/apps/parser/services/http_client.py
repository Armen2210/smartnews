from __future__ import annotations

import requests

DEFAULT_TIMEOUT = 12
DEFAULT_HEADERS = {
    "User-Agent": "SmartNewsParser/1.0 (+https://smartnews.local)",
}


def get(url: str, timeout: int = DEFAULT_TIMEOUT, headers: dict | None = None) -> requests.Response:
    merged_headers = dict(DEFAULT_HEADERS)
    if headers:
        merged_headers.update(headers)
    response = requests.get(url, timeout=timeout, headers=merged_headers)
    response.raise_for_status()
    return response