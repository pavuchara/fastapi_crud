import time
from app.celery_config import celery


@celery.task()
def call_background_task(message):
    time.sleep(2)
    print("Background Task called!")
    print(message)


@celery.task()
def schedule_task():
    print("Hi, from schedule task!")
