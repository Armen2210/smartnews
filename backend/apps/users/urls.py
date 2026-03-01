from django.urls import path
from .views import FavoriteToggleAPIView, UserNewsAPIView  # NEW

urlpatterns = [
    path("favorites/toggle/", FavoriteToggleAPIView.as_view(), name="api-favorite-toggle"),
    path("users/me/news/", UserNewsAPIView.as_view()),  # NEW
]