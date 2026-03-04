from django.conf import settings
from rest_framework.permissions import BasePermission


class BotSecretPermission(BasePermission):
    message = "Forbidden"

    def has_permission(self, request, view):
        bot_secret = request.headers.get("X-BOT-SECRET")
        return bool(bot_secret) and bot_secret == settings.BOT_SECRET