import logging
from typing import Any

from django.conf import settings

import requests
from requests import Response
from requests.exceptions import ConnectionError, RequestException, Timeout

logger = logging.getLogger(__name__)


PROXYAPI_URL = "https://api.proxyapi.ru/openai/v1/chat/completions"
MODEL_NAME = "gpt-4o"
REQUEST_TIMEOUT_SECONDS = 30


class GPTClientError(Exception):
    """Base error for ProxyAPI GPT client."""


class GPTClientConfigError(GPTClientError):
    """Raised when ProxyAPI configuration is invalid."""


class GPTClientTimeoutError(GPTClientError):
    """Raised when ProxyAPI request times out."""


class GPTClientNetworkError(GPTClientError):
    """Raised on network-level failures while calling ProxyAPI."""


class GPTClientRateLimitError(GPTClientError):
    """Raised when ProxyAPI responds with HTTP 429."""


class GPTClientServerError(GPTClientError):
    """Raised when ProxyAPI responds with HTTP 5xx."""


def _build_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _build_payload(text: str) -> dict[str, Any]:
    return {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Сделай краткий пересказ новости в 2-3 предложениях. "
                    "Без воды. Только факты."
                ),
            },
            {"role": "user", "content": text},
        ],
        "temperature": 0.2,
    }


def _extract_summary(response: Response) -> str:
    data = response.json()

    choices = data.get("choices")
    if not choices:
        raise GPTClientError("ProxyAPI response does not contain choices")

    message = choices[0].get("message") or {}
    summary = (message.get("content") or "").strip()

    if not summary:
        raise GPTClientError("ProxyAPI response contains empty summary")

    return summary


def generate_summary(text: str) -> str:
    """Generate a summary for text via ProxyAPI (GPT-4o)."""

    api_key = settings.PROXYAPI_API_KEY
    if not api_key:
        raise GPTClientConfigError("PROXYAPI_API_KEY is not set")

    try:
        response = requests.post(
            PROXYAPI_URL,
            headers=_build_headers(api_key),
            json=_build_payload(text),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except Timeout as exc:
        logger.warning("ProxyAPI timeout after %s seconds", REQUEST_TIMEOUT_SECONDS)
        raise GPTClientTimeoutError("ProxyAPI request timed out") from exc
    except ConnectionError as exc:
        logger.warning("ProxyAPI network error: %s", exc)
        raise GPTClientNetworkError("ProxyAPI network error") from exc
    except RequestException as exc:
        logger.exception("ProxyAPI request failed")
        raise GPTClientError("ProxyAPI request failed") from exc

    if response.status_code == 429:
        logger.warning("ProxyAPI rate limit reached (429)")
        raise GPTClientRateLimitError("ProxyAPI rate limit exceeded")

    if 500 <= response.status_code <= 599:
        logger.warning("ProxyAPI server error: %s", response.status_code)
        raise GPTClientServerError(
            f"ProxyAPI server error: HTTP {response.status_code}"
        )

    try:
        response.raise_for_status()
        summary = _extract_summary(response)

        # 🔍 ВАЛИДАЦИЯ
        if len(summary) < 50:
            raise GPTClientError("Summary too short")

        if "as an ai" in summary.lower():
            raise GPTClientError("Invalid GPT response")

        # ✂️ ОГРАНИЧЕНИЕ ДЛИНЫ
        return summary[:1000]

    except ValueError as exc:
        logger.exception("ProxyAPI returned invalid JSON")
        raise GPTClientError("ProxyAPI returned invalid JSON") from exc
    except RequestException as exc:
        logger.exception("ProxyAPI returned HTTP error: %s", response.status_code)
        raise GPTClientError(
            f"ProxyAPI returned HTTP {response.status_code}"
        ) from exc