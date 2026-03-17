from unittest.mock import patch

from django.test import TestCase

from apps.news.models import Category, Source, News
from apps.ai_service.tasks import generate_summary_task


class AIServiceTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="tech", slug="tech")

        self.source = Source.objects.create(
            name="BBC Tech",
            url="https://feeds.bbci.co.uk/news/technology/rss.xml",
            default_category=self.category,
        )

        self.news = News.objects.create(
            title="AI News",
            url="https://example.com/ai-news",
            source=self.source,
            category=self.category,
            published_at="2026-03-17T10:00:00Z",
            original_text="A" * 500,
            summary_status=News.SummaryStatus.PENDING,
        )

    @patch("apps.ai_service.tasks.generate_summary")
    def test_generate_summary_success(self, mock_generate_summary):
        mock_generate_summary.return_value = "Valid summary text " * 5

        generate_summary_task(self.news.id)

        self.news.refresh_from_db()

        self.assertEqual(self.news.summary_status, News.SummaryStatus.DONE)
        self.assertTrue(self.news.summary_text is not None)

    @patch("apps.ai_service.tasks.generate_summary")
    def test_generate_summary_fail_empty(self, mock_generate_summary):
        mock_generate_summary.return_value = ""

        generate_summary_task(self.news.id)

        self.news.refresh_from_db()

        self.assertEqual(self.news.summary_status, News.SummaryStatus.FAILED)

    def test_generate_summary_fail_short_text(self):
        self.news.original_text = "short"
        self.news.save()

        generate_summary_task(self.news.id)

        self.news.refresh_from_db()

        self.assertEqual(self.news.summary_status, News.SummaryStatus.FAILED)