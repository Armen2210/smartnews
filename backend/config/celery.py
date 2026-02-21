import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("smartnews")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# гарантируем, что этот app станет current/default в процессе
app.set_current()
app.set_default()