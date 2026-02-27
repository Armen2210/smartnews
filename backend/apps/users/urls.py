from django.urls import path
from .views import FavoriteToggleAPIView
from .bot_api import TelegramAuthAPIView, UserMeNewsAPIView

urlpatterns = [
    path("favorites/toggle/", FavoriteToggleAPIView.as_view(), name="api-favorite-toggle"),
    path("users/telegram-auth/", TelegramAuthAPIView.as_view(), name="tg-auth"),
    path("users/me/news/", UserMeNewsAPIView.as_view(), name="me-news"),
]