"""
Category CRUD Views - Ultra Compact
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from products.models import Category
from core.models import Brand


@login_required
def category_list(request):
    """List all categories with search and filter"""
    search = request.GET.get('search', '').strip()
    brand_id = request.GET.get('brand', '')
    page = request.GET.get('page', 1)
    
    # Base queryset
    categories = Category.objects.select_related('brand', 'parent').annotate(
        product_count=Count('products')
    )
    
    # Apply search
    if search:
        categories = categories.filter(
            Q(name__icontains=search) |
            Q(brand__name__icontains=search)
        )
    
    # Apply brand filter
    if brand_id:
        categories = categories.filter(brand_id=brand_id)
    
    # Apply ordering
    categories = categories.order_by('sort_order', 'name')
    
    # Pagination
    paginator = Paginator(categories, 10)
    categories_page = paginator.get_page(page)
    
    # Get brands for filter
    brands = Brand.objects.filter(is_active=True).order_by('name')
    
    if request.headers.get('HX-Request'):
        return render(request, 'products/category/_table.html', {
            'categories': categories_page,
            'brands': brands
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
            brand_id = request.POST.get('brand_id')
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
    brands = Brand.objects.filter(is_active=True).order_by('name')
    categories = Category.objects.none()  # Empty queryset for create mode
    
    return render(request, 'products/category/_form.html', {
        'brands': brands,
        'categories': categories
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
    brands = Brand.objects.filter(is_active=True).order_by('name')
    categories = Category.objects.filter(brand=category.brand).exclude(pk=pk).order_by('name')
    
    return render(request, 'products/category/_form.html', {
        'category': category,
        'brands': brands,
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
