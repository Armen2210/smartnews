from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.news.models import News
from .models import Favorite
from .models import TelegramUser  # NEW
from .serializers import FavoriteToggleSerializer


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


# NEW: для Telegram-бота
# 🔹 API для Telegram-бота (без Django auth)
class FavoriteToggleBotAPIView(APIView):
    def post(self, request):
        bot_secret = request.headers.get("X-BOT-SECRET")
        telegram_id = request.headers.get("X-Telegram-ID")

        # 🔐 проверка секрета
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


# NEW: новый endpoint для бота
class UserNewsAPIView(APIView):
    def get(self, request):
        bot_secret = request.headers.get("X-BOT-SECRET")
        telegram_id = request.headers.get("X-Telegram-ID")

        # 🔐 проверка секрета
        if bot_secret != settings.BOT_SECRET:  # NEW (из .env)
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        if not telegram_id:
            return Response({"error": "No telegram_id"}, status=status.HTTP_400_BAD_REQUEST)

        # создаем TelegramUser
        tg_user, _ = TelegramUser.objects.get_or_create(
            telegram_id=telegram_id
        )

        # 🔥 связываем с Django User
        user, _ = User.objects.get_or_create(
            username=f"tg_{telegram_id}"
        )

        # 📰 получить новости
        news = (
            News.objects
            .filter(summary_status=News.SummaryStatus.DONE)
            .order_by("-published_at")[:10]
        )

        data = [
            {
                "id": n.id,
                "title": n.title,
                "summary_text": n.summary_text,
                "category": n.category.name,
                "source": n.source.name,
                "published_at": n.published_at,
                "is_favorite": Favorite.objects.filter(user=user, news=n).exists(),
            }
            for n in news
        ]

        return Response(data)


# =========================================
# ⭐ Получить избранные новости (для бота)
# =========================================
class UserFavoritesAPIView(APIView):
    def get(self, request):
        bot_secret = request.headers.get("X-BOT-SECRET")
        telegram_id = request.headers.get("X-Telegram-ID")

        # 🔐 проверка секрета
        if bot_secret != settings.BOT_SECRET:
            return Response({"error": "Forbidden"}, status=403)

        if not telegram_id:
            return Response({"error": "No telegram_id"}, status=400)


        # TelegramUser создаем (для логики)
        tg_user, _ = TelegramUser.objects.get_or_create(
            telegram_id=telegram_id
        )

        # 🔥 основной user для Favorite
        user, _ = User.objects.get_or_create(
            username=f"tg_{telegram_id}"
        )

        # ⭐ получаем только избранные
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
            }
            for n in news_list
        ]

        return Response(data)