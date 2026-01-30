"""
Promotion Sync Settings Views
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from promotions.models_settings import PromotionSyncSettings


@login_required
def sync_settings(request):
    """
    Sync Settings Page
    Configure how promotions are synced to Edge Servers
    """
    # Check if user has a company
    if not request.user.company:
        messages.error(request, 'Your account is not associated with a company. Please contact administrator.')
        return redirect('dashboard:index')
    
    # Get or create settings for company
    settings = PromotionSyncSettings.get_for_company(request.user.company)
    
    if request.method == 'POST':
        # Update settings
        try:
            settings.sync_strategy = request.POST.get('sync_strategy')
            settings.future_days = int(request.POST.get('future_days', 7))
            settings.past_days = int(request.POST.get('past_days', 1))
            settings.include_inactive = request.POST.get('include_inactive') == 'on'
            settings.auto_sync_enabled = request.POST.get('auto_sync_enabled') == 'on'
            settings.sync_interval_hours = int(request.POST.get('sync_interval_hours', 6))
            settings.max_promotions_per_sync = int(request.POST.get('max_promotions_per_sync', 100))
            settings.enable_compression = request.POST.get('enable_compression') == 'on'
            settings.updated_by = request.user
            settings.save()
            
            messages.success(request, 'Sync settings updated successfully!')
            return redirect('promotion:sync_settings')
            
        except Exception as e:
            messages.error(request, f'Error updating settings: {str(e)}')
    
    context = {
        'settings': settings,
        'page_title': 'Sync Settings',
    }
    
    return render(request, 'promotions/sync_settings.html', context)


@login_required
def preview_sync_query(request):
    """
    Preview what promotions would be synced with current settings
    AJAX endpoint
    """
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Q
    from promotions.models import Promotion
    
    # Check if user has a company
    if not request.user.company:
        return JsonResponse({
            'success': False,
            'error': 'Your account is not associated with a company.'
        }, status=400)
    
    settings = PromotionSyncSettings.get_for_company(request.user.company)
    now = timezone.now()
    
    # Build query based on strategy
    if settings.sync_strategy == 'current_only':
        query = Q(
            company=request.user.company,
            is_active=True,
            start_date__lte=now.date(),
            end_date__gte=now.date()
        )
        description = "Promotions valid today only"
        
    elif settings.sync_strategy == 'include_future':
        query = Q(
            company=request.user.company,
            is_active=True,
            start_date__lte=now.date() + timedelta(days=settings.future_days),
            end_date__gte=now.date() - timedelta(days=settings.past_days)
        )
        description = f"Promotions valid from {settings.past_days} days ago to {settings.future_days} days ahead"
        
    else:  # all_active
        query = Q(
            company=request.user.company,
            is_active=True
        )
        description = "All active promotions (no date filtering)"
    
    if not settings.include_inactive:
        query &= Q(is_active=True)
    
    promotions = Promotion.objects.filter(query)
    count = promotions.count()
    
    # Get sample promotions
    samples = []
    for promo in promotions[:5]:
        samples.append({
            'code': promo.code,
            'name': promo.name,
            'start_date': str(promo.start_date),
            'end_date': str(promo.end_date),
            'is_active': promo.is_active,
        })
    
    return JsonResponse({
        'success': True,
        'count': count,
        'description': description,
        'strategy': settings.get_sync_strategy_display(),
        'samples': samples,
    })
