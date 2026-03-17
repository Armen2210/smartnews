from rest_framework import serializers


class FavoriteToggleSerializer(serializers.Serializer):
    news_id = serializers.IntegerField()


class PreferenceToggleSerializer(serializers.Serializer):
    category_slug = serializers.CharField(max_length=140)


class CategoryPreferenceSerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.CharField()
    selected = serializers.BooleanField()