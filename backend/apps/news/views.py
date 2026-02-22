from rest_framework import generics
from .models import News
from .serializers import NewsListSerializer, NewsDetailSerializer


class NewsListAPIView(generics.ListAPIView):
    serializer_class = NewsListSerializer

    def get_queryset(self):
        qs = News.objects.select_related("category", "source").all().order_by("-published_at")

        category_slug = self.request.query_params.get("category")
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        return qs


class NewsDetailAPIView(generics.RetrieveAPIView):
    queryset = News.objects.select_related("category", "source").all()
    serializer_class = NewsDetailSerializer