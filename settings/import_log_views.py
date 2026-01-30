from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@login_required
def import_log_view(request):
    """Display detailed import logs"""
    return render(request, 'settings/import_log.html')

@login_required
@require_http_methods(["GET"])
def get_import_logs(request):
    """Get import logs from session or database"""
    # For now, we'll store logs in session during import
    # In production, you might want to store this in database
    logs = request.session.get('import_logs', [])
    
    return JsonResponse({
        'success': True,
        'logs': logs
    })

def save_import_log(request, stats):
    """Save import log to session"""
    try:
        if 'import_logs' not in request.session:
            request.session['import_logs'] = []
        
        log_entry = {
            'timestamp': str(timezone.now()),
            'user': request.user.username,
            'stats': stats,
            'summary': {
                'total_rows': stats.get('processed_rows', 0),
                'successful': stats.get('successful_rows', 0),
                'failed': len(stats.get('failed_rows', [])),
                'skipped': stats.get('products_skipped', 0)
            }
        }
        
        request.session['import_logs'].append(log_entry)
        request.session.modified = True
    except AttributeError:
        # Handle test requests that don't have session
        logger.info(f"Import log (no session): User {getattr(request.user, 'username', 'Unknown')}, Stats: {stats}")
