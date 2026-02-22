from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.news.models import News
from .models import Favorite
from .serializers import FavoriteToggleSerializer


class FavoriteToggleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FavoriteToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        news_id = serializer.validated_data["news_id"]
        news = get_object_or_404(News, id=news_id)

        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            news=news
        )

        if created:
            return Response({"status": "added"}, status=status.HTTP_200_OK)

        favorite.delete()
        return Response({"status": "removed"}, status=status.HTTP_200_OK)