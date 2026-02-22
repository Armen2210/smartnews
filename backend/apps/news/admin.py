from django.contrib import admin
from .models import Category, Source, News


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "url", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "url")


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "source", "published_at", "summary_status")
    list_filter = ("category", "source", "summary_status")
    search_fields = ("title", "url")
    ordering = ("-published_at",)