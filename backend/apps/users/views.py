from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.news.models import News, Category
from .models import Favorite, TelegramUser, UserPreferences
from .serializers import (
    FavoriteToggleSerializer,
    PreferenceToggleSerializer,
    CategoryPreferenceSerializer,
)


class FavoriteToggleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FavoriteToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        news_id = serializer.validated_data["news_id"]
        news = get_object_or_404(News, id=news_id)

        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            news=news
        )

        if created:
            return Response({"status": "added"}, status=status.HTTP_200_OK)

        favorite.delete()
        return Response({"status": "removed"}, status=status.HTTP_200_OK)


class FavoriteToggleBotAPIView(APIView):
    def post(self, request):
        bot_secret = request.headers.get("X-BOT-SECRET")
        telegram_id = request.headers.get("X-Telegram-ID")

        if bot_secret != settings.BOT_SECRET:
            return Response({"error": "Forbidden"}, status=403)

        if not telegram_id:
            return Response({"error": "No telegram_id"}, status=400)

        user, _ = User.objects.get_or_create(username=f"tg_{telegram_id}")

        news_id = request.data.get("news_id")
        if not news_id:
            return Response({"error": "No news_id"}, status=400)

        news = get_object_or_404(News, id=news_id)

        favorite, created = Favorite.objects.get_or_create(
            user=user,
            news=news
        )

        if created:
            return Response({"status": "added"})

        favorite.delete()
        return Response({"status": "removed"})


class UserPreferencesAPIView(APIView):
    def get(self, request):
        bot_secret = request.headers.get("X-BOT-SECRET")
        telegram_id = request.headers.get("X-Telegram-ID")

        if bot_secret != settings.BOT_SECRET:
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        if not telegram_id:
            return Response({"error": "No telegram_id"}, status=status.HTTP_400_BAD_REQUEST)

        user, _ = User.objects.get_or_create(username=f"tg_{telegram_id}")
        preferences, _ = UserPreferences.objects.get_or_create(user=user)

        selected_slugs = set(
            preferences.categories.values_list("slug", flat=True)
        )

        categories = Category.objects.all().order_by("name")

        data = [
            {
                "name": category.name,
                "slug": category.slug,
                "selected": category.slug in selected_slugs,
            }
            for category in categories
        ]

        serializer = CategoryPreferenceSerializer(data, many=True)
        return Response(serializer.data)


class UserPreferenceToggleAPIView(APIView):
    def post(self, request):
        bot_secret = request.headers.get("X-BOT-SECRET")
        telegram_id = request.headers.get("X-Telegram-ID")

        if bot_secret != settings.BOT_SECRET:
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        if not telegram_id:
            return Response({"error": "No telegram_id"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PreferenceToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        category_slug = serializer.validated_data["category_slug"]

        user, _ = User.objects.get_or_create(username=f"tg_{telegram_id}")
        preferences, _ = UserPreferences.objects.get_or_create(user=user)

        category = get_object_or_404(Category, slug=category_slug)

        if preferences.categories.filter(id=category.id).exists():
            preferences.categories.remove(category)
            return Response({"status": "removed", "category_slug": category.slug})

        preferences.categories.add(category)
        return Response({"status": "added", "category_slug": category.slug})


class UserNewsAPIView(APIView):
    def get(self, request):
        bot_secret = request.headers.get("X-BOT-SECRET")
        telegram_id = request.headers.get("X-Telegram-ID")

        if bot_secret != settings.BOT_SECRET:
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        if not telegram_id:
            return Response({"error": "No telegram_id"}, status=status.HTTP_400_BAD_REQUEST)

        TelegramUser.objects.get_or_create(telegram_id=telegram_id)

        user, _ = User.objects.get_or_create(username=f"tg_{telegram_id}")
        preferences, _ = UserPreferences.objects.get_or_create(user=user)

        news_qs = News.objects.filter(
            summary_status=News.SummaryStatus.DONE
        )

        selected_categories = preferences.categories.all()

        if selected_categories.exists():
            news_qs = news_qs.filter(category__in=selected_categories)

        news = news_qs.order_by("-published_at")[:10]

        data = [
            {
                "id": n.id,
                "title": n.title,
                "summary_text": n.summary_text,
                "category": n.category.name,
                "source": n.source.name,
                "published_at": n.published_at,
                "url": n.url,
                "is_favorite": Favorite.objects.filter(user=user, news=n).exists(),
            }
            for n in news
        ]

        return Response(data)


class UserFavoritesAPIView(APIView):
    def get(self, request):
        bot_secret = request.headers.get("X-BOT-SECRET")
        telegram_id = request.headers.get("X-Telegram-ID")

        if bot_secret != settings.BOT_SECRET:
            return Response({"error": "Forbidden"}, status=403)

        if not telegram_id:
            return Response({"error": "No telegram_id"}, status=400)

        TelegramUser.objects.get_or_create(telegram_id=telegram_id)

        user, _ = User.objects.get_or_create(username=f"tg_{telegram_id}")

        favorites = Favorite.objects.filter(user=user).select_related("news")

        news_list = [f.news for f in favorites]

        data = [
            {
                "id": n.id,
                "title": n.title,
                "summary_text": n.summary_text,
                "category": n.category.name,
                "source": n.source.name,
                "published_at": n.published_at,
                "url": n.url,
                "is_favorite": True,
            }
            for n in news_list
        ]

        return Response(data)