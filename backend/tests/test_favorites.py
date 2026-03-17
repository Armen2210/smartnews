from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from apps.news.models import Category, Source, News
from apps.users.models import Favorite


class FavoritesTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        self.category = Category.objects.create(name="tech", slug="tech")
        self.source = Source.objects.create(
            name="BBC Tech",
            url="https://feeds.bbci.co.uk/news/technology/rss.xml",
            default_category=self.category,
        )
        self.news = News.objects.create(
            title="Favorite News",
            url="https://example.com/favorite-news",
            source=self.source,
            category=self.category,
            published_at="2026-03-17T10:00:00Z",
            original_text="A" * 200,
            summary_text="Summary text",
            summary_status=News.SummaryStatus.DONE,
        )

    def test_favorite_toggle_requires_auth(self):
        response = self.client.post("/api/favorites/toggle/", {"news_id": self.news.id})
        self.assertEqual(response.status_code, 403)

    def test_favorite_toggle_adds_favorite(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post("/api/favorites/toggle/", {"news_id": self.news.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "added")
        self.assertTrue(Favorite.objects.filter(user=self.user, news=self.news).exists())

    def test_favorite_toggle_removes_favorite(self):
        Favorite.objects.create(user=self.user, news=self.news)
        self.client.force_authenticate(user=self.user)

        response = self.client.post("/api/favorites/toggle/", {"news_id": self.news.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "removed")
        self.assertFalse(Favorite.objects.filter(user=self.user, news=self.news).exists())