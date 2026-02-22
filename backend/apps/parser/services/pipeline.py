from __future__ import annotations

import logging

from .content_extractor import extract_text
from .entry_mapper import map_entry
from .metrics import PipelineMetrics
from .persister import persist
from .rss_reader import read_entries

logger = logging.getLogger(__name__)


def run_pipeline(sources) -> PipelineMetrics:
    metrics = PipelineMetrics(sources_total=sources.count(), sources_active=sources.count())

    for source in sources:
        source_found = 0
        source_created = 0
        source_duplicates = 0
        try:
            entries = read_entries(source.url)
            metrics.entries_found += len(entries)

            for entry in entries:
                source_found += 1
                mapped, missing_published = map_entry(entry, source)
                if not mapped.get("url"):
                    metrics.add_error(f"Source {source.id}: empty url")
                    continue

                if missing_published:
                    metrics.published_at_missing_count += 1

                if not mapped.get("category"):
                    metrics.add_error(f"Source {source.id}: category is required")
                    continue

                text = extract_text(mapped)
                if not text:
                    metrics.text_empty_count += 1

                created, duplicate = persist(mapped, text)
                if created:
                    metrics.news_created += 1
                    source_created += 1
                if duplicate:
                    metrics.duplicates += 1
                    source_duplicates += 1

        except Exception as exc:
            logger.exception("Parser failed for source=%s", source.id)
            metrics.add_error(f"Source {source.id}: {exc}")

        logger.info(
            "Source %s processed: found=%s created=%s duplicates=%s",
            source.id,
            source_found,
            source_created,
            source_duplicates,
        )

    return metrics
