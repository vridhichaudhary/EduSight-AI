"""
Celery Configuration for EduSight AI.

Celery runs background tasks (ML analysis, AI agents)
so API endpoints don't time out on heavy computation.

Usage:
    Start worker: celery -A config worker --loglevel=info
    Monitor:      celery -A config flower
"""

import os
from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create Celery app
app = Celery('edusight')

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to verify Celery is working."""
    print(f'Request: {self.request!r}')
