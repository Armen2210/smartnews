from rest_framework.generics import ListAPIView

from apps.parser.services.tasklog_resolver import get_tasklog_model

from .serializers import TaskLogListSerializer


class TaskLogListApiView(ListAPIView):
    serializer_class = TaskLogListSerializer

    def get_queryset(self):
        tasklog_model = get_tasklog_model()
        if tasklog_model is None:
            return []
        return tasklog_model.objects.order_by("-created_at")[:20]