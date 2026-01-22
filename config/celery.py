"""
Celery configuration for F&B HO Project
Includes Celery Beat scheduler for periodic tasks
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create Celery app
app = Celery('fnb_ho')

# Load configuration from Django settings with 'CELERY_' prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'expire-member-points-daily': {
        'task': 'config.tasks.expire_member_points_task',
        'schedule': crontab(hour=0, minute=0),  # Daily at 00:00 (midnight)
        'options': {
            'expires': 3600,  # Task expires after 1 hour
        }
    },
    'generate-daily-reports': {
        'task': 'config.tasks.generate_daily_reports_task',
        'schedule': crontab(hour=23, minute=0),  # Daily at 23:00 (11 PM)
        'options': {
            'expires': 3600,
        }
    },
    'sync-health-check-hourly': {
        'task': 'config.tasks.sync_health_check_task',
        'schedule': crontab(minute=0),  # Every hour at :00
        'options': {
            'expires': 300,  # Task expires after 5 minutes
        }
    },
    'cleanup-old-logs-weekly': {
        'task': 'config.tasks.cleanup_old_logs_task',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Sunday 02:00 AM
        'options': {
            'expires': 7200,  # Task expires after 2 hours
        }
    },
}

# Celery Beat timezone
app.conf.timezone = 'Asia/Jakarta'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')
