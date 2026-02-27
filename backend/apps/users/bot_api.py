from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.news.models import News


def _check_bot_secret(request) -> bool:
    secret = request.headers.get("X-BOT-SECRET")
    expected = getattr(settings, "BOT_SECRET", None)
    return bool(secret) and bool(expected) and secret == expected


class TelegramAuthAPIView(APIView):
    """
    POST /api/users/telegram-auth/
    Body: {"telegram_id": 123456789}
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        if not _check_bot_secret(request):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        telegram_id = request.data.get("telegram_id")
        if not telegram_id:
            return Response({"detail": "telegram_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        username = f"tg_{telegram_id}"
        User.objects.get_or_create(username=username)

        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class UserMeNewsAPIView(APIView):
    """
    GET /api/users/me/news/
    Headers: X-Telegram-ID, X-BOT-SECRET
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        if not _check_bot_secret(request):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        telegram_id = request.headers.get("X-Telegram-ID")
        if not telegram_id:
            return Response({"detail": "X-Telegram-ID header is required"}, status=status.HTTP_400_BAD_REQUEST)

        # MVP: гарантируем пользователя
        username = f"tg_{telegram_id}"
        User.objects.get_or_create(username=username)

        # MVP: фильтры персонализации добавим позже (когда будет UserPreferences)
        qs = News.objects.filter(summary_text__isnull=False).order_by("-published_at")[:10]

        data = [
            {
                "id": n.id,
                "title": n.title,
                "summary_text": n.summary_text,
                "category": str(n.category), 
                "published_at": n.published_at,
                "url": getattr(n, "url", None),
            }
            for n in qs
        ]
        return Response(data, status=status.HTTP_200_OK)