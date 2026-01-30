"""
Kitchen Station CRUD Views - Ultra Compact
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from products.models import KitchenStation
from core.models import Brand


@login_required
def kitchenstation_list(request):
    """List all kitchen stations with search, brand, and store filters"""
    search = request.GET.get('search', '').strip()
    brand_id = request.GET.get('brand_id', '').strip()
    store_id = request.GET.get('store_id', '').strip()
    page = request.GET.get('page', 1)
    
    # Base queryset with related data - filter by global context
    kitchenstations = KitchenStation.objects.select_related('brand', 'store', 'brand__company')
    
    # Apply global filters from middleware
    if hasattr(request, 'current_company') and request.current_company:
        kitchenstations = kitchenstations.filter(company=request.current_company)
    
    if hasattr(request, 'current_brand') and request.current_brand:
        kitchenstations = kitchenstations.filter(brand=request.current_brand)
    
    # Apply search
    if search:
        kitchenstations = kitchenstations.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(brand__name__icontains=search) |
            Q(store__store_name__icontains=search) |
            Q(brand__company__name__icontains=search)
        )
    
    # Apply store filter from global context or URL parameter
    if hasattr(request, 'current_store') and request.current_store:
        kitchenstations = kitchenstations.filter(store=request.current_store)
    elif store_id:
        kitchenstations = kitchenstations.filter(store_id=store_id)
    else:
        # Show empty result if no store selected
        kitchenstations = kitchenstations.none()
    
    # Apply ordering
    kitchenstations = kitchenstations.order_by('brand__name', 'store__store_name', 'sort_order', 'name')
    
    # Pagination
    paginator = Paginator(kitchenstations, 10)
    kitchenstations_page = paginator.get_page(page)
    
    if request.headers.get('HX-Request'):
        return render(request, 'products/kitchenstation/_table.html', {
            'kitchenstations': kitchenstations_page
        })
    
    return render(request, 'products/kitchenstation/list.html', {
        'kitchenstations': kitchenstations_page,
        'search': search
    })


@login_required
@require_http_methods(["GET", "POST"])
def kitchenstation_create(request):
    """Create new kitchen station"""
    if request.method == 'POST':
        try:
            store_id = request.POST.get('store_id', '').strip()
            code = request.POST.get('code', '').strip()
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            sort_order = request.POST.get('sort_order', '0').strip()
            is_active = request.POST.get('is_active') == 'on'
            
            if not store_id or not code or not name:
                return JsonResponse({
                    'success': False,
                    'message': 'Store, Code and Name are required'
                }, status=400)
            
            # Use global context brand and get company from store
            from core.models import Store
            try:
                store = Store.objects.get(id=store_id)
                # Validate store belongs to current brand from global filter
                if hasattr(request, 'current_brand') and request.current_brand:
                    if store.brand != request.current_brand:
                        return JsonResponse({
                            'success': False,
                            'message': 'Store does not belong to selected brand'
                        }, status=400)
                    brand_id = request.current_brand.id
                    company_id = request.current_brand.company_id
                else:
                    brand_id = store.brand_id
                    company_id = store.brand.company_id
            except Store.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid store selected'
                }, status=400)
            
            # Check code uniqueness per store
            filters = {'store_id': store_id, 'code': code}
                
            if KitchenStation.objects.filter(**filters).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'Code "{code}" already exists for this store'
                }, status=400)
            
            # Create kitchen station with auto company assignment
            kitchenstation = KitchenStation.objects.create(
                company_id=company_id,
                brand_id=brand_id,
                store_id=store_id,
                code=code,
                name=name,
                description=description,
                sort_order=int(sort_order) if sort_order else 0,
                is_active=is_active
            )
            
            messages.success(request, f'Kitchen Station "{kitchenstation.name}" created successfully!')
            
            return JsonResponse({
                'success': True,
                'message': 'Kitchen Station created successfully',
                'redirect': '/products/kitchenstations/'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    # GET request - return form (store comes from global filter context)
    return render(request, 'products/kitchenstation/_form.html')


@login_required
@require_http_methods(["GET", "POST"])
def kitchenstation_update(request, pk):
    """Update existing kitchen station"""
    print(f"🚨 EDIT VIEW CALLED! PK: {pk}, Method: {request.method}")
    kitchenstation = get_object_or_404(KitchenStation.objects.select_related('brand', 'store'), pk=pk)
    print(f"🚨 FOUND STATION: {kitchenstation.name} - {kitchenstation.code}")
    
    if request.method == 'POST':
        print(f"🚨 POST METHOD DETECTED - Processing update")
        print(f"🚨 POST Data Keys: {list(request.POST.keys())}")
        print(f"🚨 POST Data Values: {dict(request.POST)}")
        try:
            brand_id = request.POST.get('brand_id', '').strip()
            store_id = request.POST.get('store_id', '').strip()
            code = request.POST.get('code', '').strip()
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            sort_order = request.POST.get('sort_order', '0').strip()
            is_active = request.POST.get('is_active') == 'on'
            
            if not brand_id or not code or not name:
                return JsonResponse({
                    'success': False,
                    'message': 'Store, Code and Name are required'
                }, status=400)
            
            # Get company and brand from store
            from core.models import Store
            try:
                store = Store.objects.get(id=store_id)
                company_id = store.brand.company_id
                brand_id = store.brand_id
                print(f"🚨 STORE FOUND: {store.store_name} - Brand: {store.brand.name}")
            except Store.DoesNotExist:
                print(f"🚨 STORE NOT FOUND: {store_id}")
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid store selected'
                }, status=400)
            
            # Check code uniqueness per store (exclude current)
            filters = {'store_id': store_id, 'code': code}
                
            if KitchenStation.objects.filter(**filters).exclude(pk=pk).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'Code "{code}" already exists for this store'
                }, status=400)
            
            # Update kitchen station
            kitchenstation.company_id = company_id
            kitchenstation.brand_id = brand_id  
            kitchenstation.store_id = store_id
            kitchenstation.code = code
            kitchenstation.name = name
            kitchenstation.description = description
            kitchenstation.sort_order = int(sort_order) if sort_order else 0
            kitchenstation.is_active = is_active
            kitchenstation.save()
            
            print(f"🚨 UPDATE SUCCESS: {kitchenstation.name}")
            
            messages.success(request, f'Kitchen Station "{kitchenstation.name}" updated successfully!')
            
            return JsonResponse({
                'success': True,
                'message': 'Kitchen Station updated successfully',
                'redirect': '/products/kitchenstations/'
            })
            
        except Exception as e:
            print(f"🚨 EXCEPTION in UPDATE: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    # GET request - return form (store comes from global filter context)
    print(f"🔍 DEBUG: Edit view GET - Kitchen Station: {kitchenstation.name} (ID: {kitchenstation.id})")
    
    return render(request, 'products/kitchenstation/_form.html', {
        'kitchenstation': kitchenstation
    })


@login_required
@require_http_methods(["POST", "DELETE"])
def kitchenstation_delete(request, pk):
    """Delete kitchen station"""
    try:
        kitchenstation = get_object_or_404(KitchenStation, pk=pk)
        kitchenstation_name = kitchenstation.name
        kitchenstation.delete()
        
        messages.success(request, f'Kitchen Station "{kitchenstation_name}" deleted successfully!')
        
        return JsonResponse({
            'success': True,
            'message': 'Kitchen Station deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
