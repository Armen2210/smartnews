from apps.news.models import Source


def load_active_sources():
    return Source.objects.filter(is_active=True).select_related("default_category")
