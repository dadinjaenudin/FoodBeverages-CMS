"""
Store CRUD Views - Ultra compact UI
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from core.models import Store, Brand, Company


@login_required
def store_list(request):
    """Store list with search and pagination"""
    search = request.GET.get('search', '')
    brand_id = request.GET.get('brand', '')
    company_id = request.GET.get('company', '')
    
    stores = Store.objects.select_related('brand', 'brand__company')
    
    if search:
        stores = stores.filter(
            Q(store_code__icontains=search) |
            Q(store_name__icontains=search) |
            Q(address__icontains=search)
        )
    
    if brand_id:
        stores = stores.filter(brand_id=brand_id)
    
    if company_id:
        stores = stores.filter(brand__company_id=company_id)
    
    paginator = Paginator(stores, 10)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    
    companies = Company.objects.filter(is_active=True).order_by('name')
    brands = Brand.objects.filter(is_active=True).select_related('company').order_by('name')
    
    context = {
        'stores': page_obj,
        'companies': companies,
        'brands': brands,
        'search': search,
        'selected_brand': brand_id,
        'selected_company': company_id,
        'total_count': stores.count(),
    }
    
    if request.htmx:
        return render(request, 'core/store/_table.html', context)
    
    return render(request, 'core/store/list.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def store_create(request):
    """Create new store"""
    if request.method == 'POST':
        try:
            brand_id = request.POST.get('brand_id')
            store_code = request.POST.get('store_code', '').strip()
            store_name = request.POST.get('store_name', '').strip()
            address = request.POST.get('address', '').strip()
            phone = request.POST.get('phone', '').strip()
            timezone = request.POST.get('timezone', 'Asia/Jakarta')
            latitude = request.POST.get('latitude', '')
            longitude = request.POST.get('longitude', '')
            is_active = request.POST.get('is_active') == 'on'
            
            if not brand_id or not store_code or not store_name or not address or not phone:
                return JsonResponse({
                    'success': False,
                    'message': 'Brand, Code, Name, Address and Phone are required'
                }, status=400)
            
            if Store.objects.filter(store_code=store_code).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'Store code "{store_code}" already exists'
                }, status=400)
            
            brand = get_object_or_404(Brand, pk=brand_id)
            
            store = Store.objects.create(
                brand=brand,
                store_code=store_code,
                store_name=store_name,
                address=address,
                phone=phone,
                timezone=timezone,
                latitude=float(latitude) if latitude else None,
                longitude=float(longitude) if longitude else None,
                is_active=is_active
            )
            
            messages.success(request, f'Store "{store.store_name}" created successfully!')
            
            return JsonResponse({
                'success': True,
                'message': 'Store created successfully',
                'redirect': '/store/'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    brands = Brand.objects.filter(is_active=True).select_related('company').order_by('name')
    context = {'brands': brands}
    return render(request, 'core/store/_form.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def store_update(request, pk):
    """Update existing store"""
    store = get_object_or_404(Store.objects.select_related('brand', 'brand__company'), pk=pk)
    
    if request.method == 'POST':
        try:
            store_code = request.POST.get('store_code', '').strip()
            store_name = request.POST.get('store_name', '').strip()
            address = request.POST.get('address', '').strip()
            phone = request.POST.get('phone', '').strip()
            timezone = request.POST.get('timezone', 'Asia/Jakarta')
            latitude = request.POST.get('latitude', '')
            longitude = request.POST.get('longitude', '')
            is_active = request.POST.get('is_active') == 'on'
            
            if not store_code or not store_name or not address or not phone:
                return JsonResponse({
                    'success': False,
                    'message': 'Code, Name, Address and Phone are required'
                }, status=400)
            
            if Store.objects.filter(store_code=store_code).exclude(pk=pk).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'Store code "{store_code}" already exists'
                }, status=400)
            
            store.store_code = store_code
            store.store_name = store_name
            store.address = address
            store.phone = phone
            store.timezone = timezone
            store.latitude = float(latitude) if latitude else None
            store.longitude = float(longitude) if longitude else None
            store.is_active = is_active
            store.save()
            
            messages.success(request, f'Store "{store.store_name}" updated successfully!')
            
            return JsonResponse({
                'success': True,
                'message': 'Store updated successfully',
                'redirect': '/store/'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    brands = Brand.objects.filter(is_active=True).select_related('company').order_by('name')
    context = {
        'store': store,
        'brands': brands
    }
    return render(request, 'core/store/_form.html', context)


@login_required
@require_http_methods(["POST", "DELETE"])
def store_delete(request, pk):
    """Delete store"""
    store = get_object_or_404(Store, pk=pk)
    
    try:
        store_name = store.store_name
        store.delete()
        
        messages.success(request, f'Store "{store_name}" deleted successfully!')
        
        return JsonResponse({
            'success': True,
            'message': 'Store deleted successfully',
            'redirect': '/store/'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
