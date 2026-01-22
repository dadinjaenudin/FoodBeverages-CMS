# 🚀 Celery Setup Guide

## Overview

Celery is configured for scheduled tasks (Celery Beat) and async task processing.

## Scheduled Tasks

### 1. **Expire Member Points** (Daily at 00:00)
- **Task**: `config.tasks.expire_member_points_task`
- **Schedule**: Midnight (00:00) every day
- **Purpose**: Expire member points based on `company.point_expiry_months`
- **Command Equivalent**: `python manage.py expire_member_points`

### 2. **Generate Daily Reports** (Daily at 23:00)
- **Task**: `config.tasks.generate_daily_reports_task`
- **Schedule**: 11 PM (23:00) every day
- **Purpose**: Generate daily sales summary
- **Future**: Email report to management

### 3. **Sync Health Check** (Hourly)
- **Task**: `config.tasks.sync_health_check_task`
- **Schedule**: Every hour at :00
- **Purpose**: Check if Edge servers are syncing (last 24h)
- **Future**: Alert if store offline > 24h

### 4. **Cleanup Old Logs** (Weekly - Sunday 02:00 AM)
- **Task**: `config.tasks.cleanup_old_logs_task`
- **Schedule**: Sunday at 02:00 AM
- **Purpose**: Delete promotion logs older than 90 days
- **Storage Optimization**: Free up database space

---

## Development Setup

### 1. Start Redis (Required for Celery)

```bash
# Using Docker
docker-compose up -d redis

# Or local Redis
redis-server
```

### 2. Start Celery Worker

```bash
cd /home/user/webapp
source venv/bin/activate
celery -A config worker --loglevel=info
```

### 3. Start Celery Beat (Scheduler)

```bash
cd /home/user/webapp
source venv/bin/activate
celery -A config beat --loglevel=info
```

### 4. Combined (Worker + Beat)

```bash
celery -A config worker --beat --loglevel=info
```

---

## Production Setup

### Using Supervisor (Recommended)

Create `/etc/supervisor/conf.d/celery.conf`:

```ini
[program:celery_worker]
command=/home/user/webapp/venv/bin/celery -A config worker --loglevel=info
directory=/home/user/webapp
user=www-data
numprocs=1
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker_error.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
killasgroup=true
priority=998

[program:celery_beat]
command=/home/user/webapp/venv/bin/celery -A config beat --loglevel=info
directory=/home/user/webapp
user=www-data
numprocs=1
stdout_logfile=/var/log/celery/beat.log
stderr_logfile=/var/log/celery/beat_error.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=10
killasgroup=true
priority=999
```

Then:

```bash
sudo mkdir -p /var/log/celery
sudo chown www-data:www-data /var/log/celery
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start celery_worker
sudo supervisorctl start celery_beat
```

### Using Systemd

Create `/etc/systemd/system/celery.service`:

```ini
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/home/user/webapp
ExecStart=/home/user/webapp/venv/bin/celery -A config worker --beat --loglevel=info --detach --pidfile=/var/run/celery.pid --logfile=/var/log/celery/celery.log
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl start celery
sudo systemctl enable celery
sudo systemctl status celery
```

---

## Monitoring

### View Celery Logs

```bash
# Worker logs
tail -f /var/log/celery/worker.log

# Beat logs
tail -f /var/log/celery/beat.log
```

### Check Celery Status

```bash
celery -A config status
celery -A config inspect active
celery -A config inspect scheduled
```

### Flower (Web Monitoring UI)

```bash
pip install flower
celery -A config flower
```

Then visit: `http://localhost:5555`

---

## Manual Task Execution (Testing)

```python
from config.tasks import expire_member_points_task

# Execute immediately
result = expire_member_points_task.delay()
print(result.id)

# Check result
result.get(timeout=60)
```

---

## Environment Variables

Update `.env`:

```env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

For production (with password):

```env
CELERY_BROKER_URL=redis://:password@redis-server:6379/0
CELERY_RESULT_BACKEND=redis://:password@redis-server:6379/0
```

---

## Task Retention

- Results stored in Redis with TTL
- Old results expire automatically
- Promotion logs cleaned weekly (90+ days)

---

## Troubleshooting

### Problem: Tasks not running

**Solution**:
1. Check Redis is running: `redis-cli ping`
2. Check Celery worker is running: `celery -A config status`
3. Check Celery beat is running: `ps aux | grep celery`
4. Check logs: `tail -f /var/log/celery/*.log`

### Problem: Task timeout

**Solution**:
- Increase `CELERY_TASK_TIME_LIMIT` in settings.py
- Default: 30 minutes (1800 seconds)

### Problem: Memory leak

**Solution**:
- Set `CELERYD_MAX_TASKS_PER_CHILD = 1000` in settings.py
- Worker restarts after 1000 tasks

---

## Adding New Scheduled Tasks

1. Create task in `config/tasks.py`:

```python
@shared_task
def my_new_task():
    # Task logic here
    return {'status': 'success'}
```

2. Add schedule in `config/celery.py`:

```python
app.conf.beat_schedule = {
    'my-new-task': {
        'task': 'config.tasks.my_new_task',
        'schedule': crontab(hour=3, minute=30),  # Daily at 03:30
    },
}
```

3. Restart Celery Beat:

```bash
sudo supervisorctl restart celery_beat
# or
sudo systemctl restart celery
```

---

## Crontab Schedule Examples

```python
from celery.schedules import crontab

# Every minute
crontab()

# Every hour at :15
crontab(minute=15)

# Every day at 02:00 AM
crontab(hour=2, minute=0)

# Every Monday at 08:00 AM
crontab(hour=8, minute=0, day_of_week=1)

# First day of month at 00:00
crontab(hour=0, minute=0, day_of_month=1)
```

---

## Best Practices

1. ✅ Use `@shared_task` decorator (not `@app.task`)
2. ✅ Set task timeouts (`expires` in beat schedule)
3. ✅ Log task execution (start/end/errors)
4. ✅ Use try-except for error handling
5. ✅ Return structured results (dict with status)
6. ✅ Test tasks manually before scheduling
7. ✅ Monitor task execution (Flower)
8. ✅ Set up alerting for failed tasks

---

For more info: https://docs.celeryproject.org/
