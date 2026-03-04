from django.urls import path
from .views import FavoriteToggleAPIView, FavoriteToggleBotAPIView, UserNewsAPIView, UserFavoritesAPIView  # NEW

urlpatterns = [
    path("favorites/toggle/", FavoriteToggleAPIView.as_view(), name="api-favorite-toggle"),
    path("favorites/toggle-bot/", FavoriteToggleBotAPIView.as_view()), # NEW для ТГ бота
    path("users/me/news/", UserNewsAPIView.as_view()),
    path("users/me/favorites/", UserFavoritesAPIView.as_view()), # NEW для ТГ бота
]