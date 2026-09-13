from celery import Celery

from app.core.config import settings

celery = Celery(
    "kwarihub",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Lagos",
    enable_utc=True,
)

celery.autodiscover_tasks(
    [
        "app.tasks",
    ]
)