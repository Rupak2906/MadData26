# Defines Celery worker and background tasks (analysis, reminders, plan generation).

from celery import Celery
from celery.schedules import crontab
import os

app = Celery('celery_worker')

app.config_from_object({
    'broker_url': os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379'),
    'result_backend': os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379'),
    'task_serializer': 'json',
    'accept_content': ['json'],
    'timezone': 'UTC',
    'enable_utc': True,
})

app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Result: {self.result}')