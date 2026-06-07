from celery import Celery

celery_app = Celery(
    'notifications',
    broker='redis://localhost:6379/0', #queue broker
    backend='redis://localhost:6379/0',
    include=['tasks']
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    result_serializer='json',
)

from models.user import User
from models.notification import Notification

