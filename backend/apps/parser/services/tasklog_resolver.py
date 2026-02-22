from django.apps import apps


def get_tasklog_model():
    for app_label in ("tasklog", "parser"):
        try:
            return apps.get_model(app_label, "TaskLog")
        except (LookupError, ValueError):
            continue
    return None
