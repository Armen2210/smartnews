from celery import shared_task


@shared_task
def parse_news_stub():
    print("🔥 parser stub executed")
    return "ok"