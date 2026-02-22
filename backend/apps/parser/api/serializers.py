from rest_framework import serializers


class TaskLogListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    task_name = serializers.CharField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    meta = serializers.SerializerMethodField()

    def get_meta(self, obj):
        raw = getattr(obj, "meta", None) or {}
        keys = [
            "sources_total",
            "sources_active",
            "entries_found",
            "news_created",
            "duplicates",
            "errors_count",
        ]
        return {key: raw.get(key) for key in keys}