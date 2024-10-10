"""
Запуск можно осуществить след. способами:
    - Просто запустить воркер:
        celery -A app.celery_config worker
    - Воркер с подробной лог инфой и пулом процессов:
        celery -A app.celery_config worker --loglevel=info -P gevent
    - Чисто beat процесс:
        celery -A app.celery_config beat --loglevel=info
    - Воркер вместе с beat процессом:
        celery -A app.celery_config worker --beat --loglevel=info

    Мониторинг flower (http://localhost:5555/):
        celery -A main.celery flower
"""

from celery import Celery
from celery.schedules import crontab

celery = Celery(
    __name__,
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0",
    broker_connection_retry_on_startup=True,
)


celery.autodiscover_tasks(['app.tasks'])

celery.conf.beat_schedule = {
    "some_schedule_task": {
        "task": "app.tasks.schedule_task",
        "schedule": crontab(),
    }
}
