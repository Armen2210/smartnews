from django.contrib import admin
from .models import UserPreferences, Favorite


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    search_fields = ("user__username", "user__email")
    filter_horizontal = ("categories",)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "news", "created_at")
    search_fields = ("user__username", "news__title")
    list_filter = ("created_at",)