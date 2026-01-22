"""
Celery Tasks - Scheduled & Async Tasks
"""
from celery import shared_task
from django.core.management import call_command
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task
def expire_member_points_task():
    """
    Scheduled task to expire member points daily
    Run daily at 00:00 (midnight)
    """
    logger.info(f"Starting member points expiry job at {timezone.now()}")
    
    try:
        call_command('expire_member_points')
        logger.info("Member points expiry job completed successfully")
        return {'status': 'success', 'timestamp': timezone.now().isoformat()}
    except Exception as e:
        logger.error(f"Member points expiry job failed: {str(e)}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def generate_daily_reports_task():
    """
    Generate daily sales reports
    Run daily at 23:00 (11 PM)
    """
    logger.info(f"Starting daily reports generation at {timezone.now()}")
    
    from transactions.models import Bill
    from django.db.models import Sum, Count, Avg
    from datetime import date
    
    try:
        today = date.today()
        
        # Generate daily summary
        summary = Bill.objects.filter(
            status='PAID',
            created_at__date=today
        ).aggregate(
            total_bills=Count('id'),
            total_sales=Sum('total'),
            avg_bill_value=Avg('total')
        )
        
        logger.info(f"Daily report for {today}: {summary}")
        
        # TODO: Send email report to management
        # TODO: Store report in database for historical tracking
        
        return {
            'status': 'success',
            'date': today.isoformat(),
            'summary': summary
        }
    except Exception as e:
        logger.error(f"Daily reports generation failed: {str(e)}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def sync_health_check_task():
    """
    Check sync health from Edge servers
    Run every hour
    """
    logger.info(f"Starting sync health check at {timezone.now()}")
    
    from transactions.models import Bill
    from datetime import timedelta
    from django.db.models import Max
    
    try:
        # Check for bills synced in last 24 hours per store
        yesterday = timezone.now() - timedelta(days=1)
        
        recent_syncs = Bill.objects.filter(
            synced_at__gte=yesterday
        ).values('store_id').annotate(
            bill_count=Count('id'),
            last_sync=Max('synced_at')
        )
        
        logger.info(f"Sync health check: {recent_syncs.count()} stores active")
        
        # TODO: Alert if no sync from a store for > 24h
        # TODO: Store health metrics
        
        return {
            'status': 'success',
            'active_stores': recent_syncs.count(),
            'timestamp': timezone.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Sync health check failed: {str(e)}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def cleanup_old_logs_task():
    """
    Cleanup old promotion logs & audit trails
    Run weekly (Sunday 02:00 AM)
    """
    logger.info(f"Starting log cleanup at {timezone.now()}")
    
    from promotions.models import PromotionLog
    from datetime import timedelta
    
    try:
        # Delete logs older than 90 days
        ninety_days_ago = timezone.now() - timedelta(days=90)
        
        deleted_count = PromotionLog.objects.filter(
            created_at__lt=ninety_days_ago
        ).delete()[0]
        
        logger.info(f"Deleted {deleted_count} old promotion logs")
        
        return {
            'status': 'success',
            'deleted_count': deleted_count,
            'timestamp': timezone.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Log cleanup failed: {str(e)}")
        return {'status': 'failed', 'error': str(e)}
