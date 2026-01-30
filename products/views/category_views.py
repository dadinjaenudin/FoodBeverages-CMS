"""
Category CRUD Views - Ultra Compact
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Count, Prefetch
from django.core.paginator import Paginator
from products.models import Category
from core.models import Brand


@login_required
def category_list(request):
    """List all categories with search and filter"""
    search = request.GET.get('search', '').strip()
    brand_id = request.GET.get('brand', '')
    page = request.GET.get('page', 1)
    
    # Get current brand from Global Filter (middleware)
    current_brand = getattr(request, 'current_brand', None)
    current_company = getattr(request, 'current_company', None)
    
    if search:
        # Flat list for search results
        categories = Category.objects.select_related('brand', 'parent').annotate(
            product_count=Count('products')
        )
        
        categories = categories.filter(
            Q(name__icontains=search) |
            Q(brand__name__icontains=search)
        )
        
        # Apply Global Brand Filter
        if current_brand:
            categories = categories.filter(brand=current_brand)
        elif current_company:
            categories = categories.filter(brand__company=current_company)
        elif brand_id:
            categories = categories.filter(brand_id=brand_id)
            
        categories = categories.order_by('sort_order', 'name')
        
    else:
        # Hierarchical list (Parent -> Children)
        # 1. Prepare children queryset with annotation
        children_queryset = Category.objects.select_related('brand').annotate(
            product_count=Count('products')
        ).order_by('sort_order', 'name')
        
        # 2. Fetch parents with prefetched children
        categories = Category.objects.filter(parent__isnull=True).select_related('brand').annotate(
            product_count=Count('products')
        ).prefetch_related(
            Prefetch('children', queryset=children_queryset)
        )
        
        # Apply Global Brand Filter
        if current_brand:
            categories = categories.filter(brand=current_brand)
        elif current_company:
            categories = categories.filter(brand__company=current_company)
        elif brand_id:
            categories = categories.filter(brand_id=brand_id)
            
        categories = categories.order_by('sort_order', 'name')

    # Pagination
    paginator = Paginator(categories, 10)
    categories_page = paginator.get_page(page)
    
    # Get brands for filter
    brands = Brand.objects.filter(is_active=True).order_by('name')
    
    if request.headers.get('HX-Request'):
        return render(request, 'products/category/_table.html', {
            'categories': categories_page,
            'brands': brands,
            'search': search  # Pass search to template to know render mode
        })
    
    return render(request, 'products/category/list.html', {
        'categories': categories_page,
        'brands': brands,
        'search': search,
        'selected_brand': brand_id
    })


@login_required
@require_http_methods(["GET", "POST"])
def category_create(request):
    """Create new category"""
    if request.method == 'POST':
        try:
            # Get brand from global filter or POST
            brand_id = request.POST.get('brand_id')
            if not brand_id and hasattr(request, 'current_brand') and request.current_brand:
                brand_id = request.current_brand.id
            
            name = request.POST.get('name', '').strip()
            parent_id = request.POST.get('parent_id', '').strip()
            sort_order = request.POST.get('sort_order', '0')
            icon = request.POST.get('icon', '').strip()
            is_active = request.POST.get('is_active') == 'on'
            
            if not brand_id or not name:
                return JsonResponse({
                    'success': False,
                    'message': 'Brand and Name are required'
                }, status=400)
            
            # Create category
            category = Category.objects.create(
                brand_id=brand_id,
                name=name,
                parent_id=parent_id if parent_id else None,
                sort_order=int(sort_order) if sort_order else 0,
                icon=icon,
                is_active=is_active
            )
            
            messages.success(request, f'Category "{category.name}" created successfully!')
            
            return JsonResponse({
                'success': True,
                'message': 'Category created successfully',
                'redirect': '/products/categories/'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    # GET request - return form
    # Check if creating subcategory (parent parameter)
    parent_id = request.GET.get('parent', '')
    parent_category = None
    
    # Get current brand from global filter
    current_brand = getattr(request, 'current_brand', None)
    
    if parent_id:
        parent_category = get_object_or_404(Category.objects.select_related('brand'), pk=parent_id)
        categories = Category.objects.filter(brand=parent_category.brand).order_by('name')
    elif current_brand:
        # For create mode, show categories from current brand for parent selection
        categories = Category.objects.filter(brand=current_brand, parent__isnull=True).order_by('name')
    else:
        categories = Category.objects.none()  # Empty queryset
    
    return render(request, 'products/category/_form.html', {
        'categories': categories,
        'parent_category': parent_category
    })


@login_required
@require_http_methods(["GET", "POST"])
def category_update(request, pk):
    """Update existing category"""
    category = get_object_or_404(Category.objects.select_related('brand', 'parent'), pk=pk)
    
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            parent_id = request.POST.get('parent_id', '').strip()
            sort_order = request.POST.get('sort_order', '0')
            icon = request.POST.get('icon', '').strip()
            is_active = request.POST.get('is_active') == 'on'
            
            if not name:
                return JsonResponse({
                    'success': False,
                    'message': 'Name is required'
                }, status=400)
            
            # Update category
            category.name = name
            category.parent_id = parent_id if parent_id else None
            category.sort_order = int(sort_order) if sort_order else 0
            category.icon = icon
            category.is_active = is_active
            category.save()
            
            messages.success(request, f'Category "{category.name}" updated successfully!')
            
            return JsonResponse({
                'success': True,
                'message': 'Category updated successfully',
                'redirect': '/products/categories/'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    # GET request - return form
    categories = Category.objects.filter(brand=category.brand, parent__isnull=True).exclude(pk=pk).order_by('name')
    
    return render(request, 'products/category/_form.html', {
        'category': category,
        'categories': categories
    })


@login_required
@require_http_methods(["POST", "DELETE"])
def category_delete(request, pk):
    """Delete category"""
    try:
        category = get_object_or_404(Category, pk=pk)
        category_name = category.name
        category.delete()
        
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        
        return JsonResponse({
            'success': True,
            'message': 'Category deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
