from __future__ import annotations

import logging

from celery import shared_task

from apps.parser.services.pipeline import run_pipeline
from apps.parser.services.source_loader import load_active_sources
from apps.parser.services.tasklog_resolver import get_tasklog_model

logger = logging.getLogger(__name__)


def _safe_tasklog_create(**kwargs):
    tasklog_model = get_tasklog_model()
    if tasklog_model is None:
        logger.warning("TaskLog model not found in installed apps")
        return None

    try:
        return tasklog_model.objects.create(**kwargs)
    except Exception:
        logger.exception("TaskLog create failed")
        return None


def _safe_tasklog_update(task_log, **kwargs):
    if not task_log:
        return
    try:
        for key, value in kwargs.items():
            setattr(task_log, key, value)
        task_log.save(update_fields=list(kwargs.keys()))
    except Exception:
        logger.exception("TaskLog update failed")


@shared_task(name="parser.parse_sources_task")
def parse_sources_task() -> dict:
    logger.info("parse_sources_task started")
    sources = load_active_sources()

    task_log = _safe_tasklog_create(task_name="parse_sources_task", status="started", meta={})

    try:
        metrics = run_pipeline(sources)
        meta = metrics.to_meta()
        _safe_tasklog_update(task_log, status="success", meta=meta)
        logger.info("parse_sources_task finished: %s", meta)
        return meta
    except Exception as exc:
        logger.exception("parse_sources_task failed")
        failed_meta = {
            "sources_total": sources.count(),
            "sources_active": sources.count(),
            "entries_found": 0,
            "news_created": 0,
            "duplicates": 0,
            "errors_count": 1,
            "published_at_missing_count": 0,
            "text_empty_count": 0,
            "errors_sample": [str(exc)[:300]],
        }
        _safe_tasklog_update(task_log, status="failed", meta=failed_meta)
        return failed_meta


@shared_task(name="parser.parse_news_stub")
def parse_news_stub():
    """Backward-compatible alias for legacy scheduler hooks."""
    return parse_sources_task()