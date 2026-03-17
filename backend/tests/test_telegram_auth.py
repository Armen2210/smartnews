from django.conf import settings
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.news.models import Category, Source, News


@override_settings(BOT_SECRET="test-bot-secret")
class TelegramAuthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.category = Category.objects.create(name="tech", slug="tech")
        self.source = Source.objects.create(
            name="BBC Tech",
            url="https://feeds.bbci.co.uk/news/technology/rss.xml",
            default_category=self.category,
        )
        self.news = News.objects.create(
            title="Protected News",
            url="https://example.com/protected-news",
            source=self.source,
            category=self.category,
            published_at="2026-03-17T10:00:00Z",
            original_text="A" * 200,
            summary_text="Protected summary",
            summary_status=News.SummaryStatus.DONE,
        )

    def test_news_detail_forbidden_without_secret(self):
        response = self.client.get(f"/api/news/{self.news.id}/")
        self.assertEqual(response.status_code, 403)

    def test_news_detail_forbidden_with_wrong_secret(self):
        response = self.client.get(
            f"/api/news/{self.news.id}/",
            HTTP_X_BOT_SECRET="wrong-secret",
        )
        self.assertEqual(response.status_code, 403)

    def test_news_detail_ok_with_correct_secret(self):
        response = self.client.get(
            f"/api/news/{self.news.id}/",
            HTTP_X_BOT_SECRET=settings.BOT_SECRET,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.news.id)
        self.assertEqual(response.data["title"], "Protected News")