from unittest.mock import patch

from django.test import TestCase

from apps.news.models import Category, Source, News
from apps.parser.services.pipeline import run_pipeline
from apps.parser.services.source_loader import load_active_sources


class ParserTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="tech", slug="tech")

        self.active_source = Source.objects.create(
            name="BBC Tech",
            url="https://feeds.bbci.co.uk/news/technology/rss.xml",
            is_active=True,
            default_category=self.category,
        )

        self.inactive_source = Source.objects.create(
            name="Inactive Source",
            url="https://example.com/inactive.xml",
            is_active=False,
            default_category=self.category,
        )

    def test_load_active_sources_returns_only_active(self):
        sources = load_active_sources()

        self.assertEqual(sources.count(), 1)
        self.assertEqual(sources.first().id, self.active_source.id)

    @patch("apps.parser.services.pipeline.persist")
    @patch("apps.parser.services.pipeline.extract_text")
    @patch("apps.parser.services.pipeline.map_entry")
    @patch("apps.parser.services.pipeline.read_entries")
    def test_run_pipeline_creates_metrics(
        self,
        mock_read_entries,
        mock_map_entry,
        mock_extract_text,
        mock_persist,
    ):
        mock_read_entries.return_value = [{"title": "Test entry"}]

        mock_map_entry.return_value = (
            {
                "title": "Test news",
                "url": "https://example.com/test-news",
                "category": self.category,
                "source": self.active_source,
                "published_at": "2026-03-17T10:00:00Z",
            },
            False,
        )

        mock_extract_text.return_value = "A" * 300
        mock_persist.return_value = (True, False)

        metrics = run_pipeline(load_active_sources())

        self.assertEqual(metrics.sources_total, 1)
        self.assertEqual(metrics.sources_active, 1)
        self.assertEqual(metrics.entries_found, 1)
        self.assertEqual(metrics.news_created, 1)
        self.assertEqual(metrics.duplicates, 0)

    @patch("apps.parser.services.pipeline.read_entries")
    def test_run_pipeline_handles_reader_error(self, mock_read_entries):
        mock_read_entries.side_effect = Exception("RSS error")

        metrics = run_pipeline(load_active_sources())

        self.assertEqual(metrics.sources_total, 1)
        self.assertEqual(metrics.sources_active, 1)
        self.assertEqual(metrics.news_created, 0)
        self.assertEqual(metrics.errors_count, 1)
        self.assertTrue(len(metrics.errors_sample) >= 1)