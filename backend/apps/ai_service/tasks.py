import logging

from celery import shared_task

from apps.news.models import News
from apps.ai_service.services.gpt_client import generate_summary

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="apps.ai_service.tasks.generate_summary_task")
def generate_summary_task(self, news_id: int) -> None:
    try:
        # 🔥 атомарный переход
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

        # ❗ проверки текста
        if not news.original_text:
            News.objects.filter(id=news_id).update(summary_status="failed")
            return

        if len(news.original_text) < 100:
            News.objects.filter(id=news_id).update(summary_status="failed")
            return

        # ✂️ обрезка текста
        text = news.original_text[:4000]

        # 🤖 вызов GPT
        summary = generate_summary(text)

        # 💾 сохранение результата
        News.objects.filter(id=news_id).update(
            summary_text=summary,
            summary_status="done",
        )

        logger.info("generate_summary_task done: news_id=%s", news_id)

    except Exception:
        logger.exception("generate_summary_task error: news_id=%s", news_id)

        # ❗ при любой ошибке
        News.objects.filter(id=news_id).update(summary_status="failed")