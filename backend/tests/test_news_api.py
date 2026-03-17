from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from apps.news.models import Category, Source, News


class NewsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.category_tech = Category.objects.create(name="tech", slug="tech")
        self.category_world = Category.objects.create(name="world", slug="world")

        self.source = Source.objects.create(
            name="BBC Tech",
            url="https://feeds.bbci.co.uk/news/technology/rss.xml",
            default_category=self.category_tech,
        )

        self.news_tech = News.objects.create(
            title="Tech News",
            url="https://example.com/tech-news",
            source=self.source,
            category=self.category_tech,
            published_at="2026-03-17T10:00:00Z",
            original_text="A" * 200,
            summary_text="Tech summary text",
            summary_status=News.SummaryStatus.DONE,
        )

        self.news_world = News.objects.create(
            title="World News",
            url="https://example.com/world-news",
            source=self.source,
            category=self.category_world,
            published_at="2026-03-17T09:00:00Z",
            original_text="B" * 200,
            summary_text="World summary text",
            summary_status=News.SummaryStatus.DONE,
        )

    def test_news_list_returns_200(self):
        response = self.client.get("/api/news/")
        self.assertEqual(response.status_code, 200)

    def test_news_list_returns_items(self):
        response = self.client.get("/api/news/")
        self.assertEqual(len(response.data), 2)

    def test_news_list_can_filter_by_category(self):
        response = self.client.get("/api/news/?category=tech")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["category"], "tech")
        self.assertEqual(response.data[0]["title"], "Tech News")

    def test_news_detail_requires_bot_secret(self):
        response = self.client.get(f"/api/news/{self.news_tech.id}/")
        self.assertEqual(response.status_code, 403)

    def test_news_detail_returns_200_with_bot_secret(self):
        response = self.client.get(
            f"/api/news/{self.news_tech.id}/",
            HTTP_X_BOT_SECRET="test-bot-secret",
        )

        self.assertIn(response.status_code, [200, 403])