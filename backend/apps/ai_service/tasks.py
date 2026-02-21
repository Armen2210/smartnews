from celery import shared_task


@shared_task
def summarize_stub():
    print("🤖 ai stub executed")
    return "ok"