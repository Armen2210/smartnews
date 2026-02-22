from django.urls import path
from .views import NewsListAPIView, NewsDetailAPIView

urlpatterns = [
    path("news/", NewsListAPIView.as_view(), name="api-news-list"),
    path("news/<int:pk>/", NewsDetailAPIView.as_view(), name="api-news-detail"),
]