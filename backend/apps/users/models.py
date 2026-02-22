from django.conf import settings
from django.db import models


class UserPreferences(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="preferences",
    )
    categories = models.ManyToManyField(
        "news.Category",
        blank=True,
        related_name="preferred_by_users",
    )

    def __str__(self):
        return f"Preferences: {self.user}"


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    news = models.ForeignKey(
        "news.News",
        on_delete=models.CASCADE,
        related_name="favorited_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "news"], name="unique_favorite")
        ]

    def __str__(self):
        return f"{self.user} → {self.news_id}"
