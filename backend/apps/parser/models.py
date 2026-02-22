from django.db import models


class TaskLog(models.Model):
    task_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50)

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    meta = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.task_name} ({self.status})"
