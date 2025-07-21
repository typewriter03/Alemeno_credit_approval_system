# src/credit_approval_system/celery.py

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_approval_system.settings')

app = Celery('credit_approval_system')
app.config_from_object('django.conf:settings', namespace='CELERY')

# This is the standard and correct way to discover tasks.
app.autodiscover_tasks()