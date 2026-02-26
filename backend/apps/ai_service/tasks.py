import logging

from celery import shared_task

from apps.news.models import News
from apps.ai_service.services.gpt_client import generate_summary

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="apps.ai_service.tasks.generate_summary_task")
def generate_summary_task(self, news_id: int) -> None:
    try:
        # 🔥 атомарный переход pending → processing
        updated_rows = News.objects.filter(
            id=news_id,
            summary_status="pending",
        ).update(summary_status="processing")

        if not updated_rows:
            logger.info(
                "generate_summary_task skipped: news_id=%s not in pending",
                news_id,
            )
            return

        logger.info("generate_summary_task started: news_id=%s", news_id)

        news = News.objects.get(id=news_id)

        # ❗ валидация входного текста
        if not news.original_text:
            logger.warning("Empty original_text: news_id=%s", news_id)
            News.objects.filter(id=news_id).update(summary_status="failed")
            return

        if len(news.original_text) < 100:
            logger.warning("Too short original_text: news_id=%s", news_id)
            News.objects.filter(id=news_id).update(summary_status="failed")
            return

        # ✂️ обрезка текста (защита от переполнения)
        text = news.original_text[:4000]

        # 🤖 вызов GPT
        summary = generate_summary(text)

        # 🔍 БИЗНЕС-ВАЛИДАЦИЯ ответа GPT
        if not summary:
            raise ValueError("Empty summary")

        summary_clean = summary.strip()

        if len(summary_clean) < 50:
            raise ValueError("Summary too short")

        # ✅ расширенная эвристика "мусорного" пересказа
        summary_lower = summary_clean.lower()

        bad_patterns = [
            "нет информации",
            "нет конкретной информации",
            "факты отсутствуют",
            "без фактов",
            "без фактической информации",
            "без конкретики",
            "не содержит информации",
            "не содержит фактов",
            "общий текст",
        ]

        if any(pattern in summary_lower for pattern in bad_patterns):
            raise ValueError("Low-quality summary detected")

        # 💾 сохранение результата
        News.objects.filter(id=news_id).update(
            summary_text=summary_clean,
            summary_status="done",
        )

        logger.info("generate_summary_task done: news_id=%s", news_id)

    except Exception:
        logger.exception("generate_summary_task error: news_id=%s", news_id)

        # ❗ при любой ошибке → failed
        News.objects.filter(id=news_id).update(summary_status="failed")