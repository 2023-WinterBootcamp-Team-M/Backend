import os
from celery import Celery
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_back.settings')

app = Celery('django_back', broker='amqp://guest:guest@rabbitmq:5672/')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'send_alarm_for_unread_bookmarks': {
        'task': 'bookmark.tasks.send_alarm_for_unread_bookmarks',
        'schedule': crontab(hour=9, minute=0),
    },
}

app.autodiscover_tasks()
app.autodiscover_tasks()

app.conf.task_ack_late = True

app.log.setup_logging_subsystem()
logger = logging.getLogger('django_back')
logger.setLevel(logging.DEBUG)

def revoke_task(task_id):
    app.control.revoke(task_id, terminate=True)
