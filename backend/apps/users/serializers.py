from rest_framework import serializers


class FavoriteToggleSerializer(serializers.Serializer):
    news_id = serializers.IntegerField()