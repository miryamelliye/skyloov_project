from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
app = Celery("myproject",include=['products.tasks'])
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send_everyday_mail': {
        'task': 'products.tasks.send_everyday_mail',
        'schedule': crontab(hour=20, minute=54),
        # 'args' : ("it has to work plsssss",)
    }
} 