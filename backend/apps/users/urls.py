from django.urls import path
from .views import FavoriteToggleAPIView

urlpatterns = [
    path("favorites/toggle/", FavoriteToggleAPIView.as_view(), name="api-favorite-toggle"),
]