from rest_framework import serializers
from .models import News


class NewsListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.slug")
    source = serializers.CharField(source="source.name")

    class Meta:
        model = News
        fields = [
            "id",
            "title",
            "summary_text",
            "category",
            "source",
            "published_at",
        ]


class NewsDetailSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.slug")
    source = serializers.CharField(source="source.name")

    class Meta:
        model = News
        fields = [
            "id",
            "title",
            "original_text",
            "summary_text",
            "category",
            "source",
            "published_at",
            "url",
        ]