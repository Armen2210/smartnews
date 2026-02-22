from django.urls import path

from .views import TaskLogListApiView

urlpatterns = [
    path("tasklog/", TaskLogListApiView.as_view(), name="tasklog-list"),
]