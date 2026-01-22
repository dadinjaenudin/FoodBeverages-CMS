"""
Product CRUD Views - Ultra Compact with Image Upload
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from products.models import Product, ProductPhoto, Category
from core.models import Brand


@login_required
def product_list(request):
    """List all products with search and filter"""
    search = request.GET.get('search', '').strip()
    brand_id = request.GET.get('brand', '')
    category_id = request.GET.get('category', '')
    page = request.GET.get('page', 1)
    
    # Base queryset
    products = Product.objects.select_related('brand', 'category').prefetch_related('photos')
    
    # Apply search
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(sku__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Apply brand filter
    if brand_id:
        products = products.filter(brand_id=brand_id)
    
    # Apply category filter
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Apply ordering
    products = products.order_by('sort_order', 'name')
    
    # Pagination
    paginator = Paginator(products, 10)
    products_page = paginator.get_page(page)
    
    # Get brands and categories for filter
    brands = Brand.objects.filter(is_active=True).order_by('name')
    categories = Category.objects.filter(is_active=True).select_related('brand').order_by('brand__name', 'name')
    
    if request.headers.get('HX-Request'):
        return render(request, 'products/product/_table.html', {
            'products': products_page,
            'brands': brands,
            'categories': categories
        })
    
    return render(request, 'products/product/list.html', {
        'products': products_page,
        'brands': brands,
        'categories': categories,
        'search': search,
        'selected_brand': brand_id,
        'selected_category': category_id
    })


@login_required
@require_http_methods(["GET", "POST"])
def product_create(request):
    """Create new product with image upload"""
    if request.method == 'POST':
        try:
            brand_id = request.POST.get('brand_id')
            category_id = request.POST.get('category_id')
            sku = request.POST.get('sku', '').strip()
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            price = request.POST.get('price', '0')
            cost = request.POST.get('cost', '0')
            printer_target = request.POST.get('printer_target', 'kitchen')
            track_stock = request.POST.get('track_stock') == 'on'
            stock_quantity = request.POST.get('stock_quantity', '0')
            sort_order = request.POST.get('sort_order', '0')
            is_active = request.POST.get('is_active') == 'on'
            
            if not all([brand_id, category_id, sku, name, price]):
                return JsonResponse({
                    'success': False,
                    'message': 'Brand, Category, SKU, Name and Price are required'
                }, status=400)
            
            # Check SKU uniqueness per brand
            if Product.objects.filter(brand_id=brand_id, sku=sku).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'SKU "{sku}" already exists for this brand'
                }, status=400)
            
            # Create product
            product = Product.objects.create(
                brand_id=brand_id,
                category_id=category_id,
                sku=sku,
                name=name,
                description=description,
                price=float(price),
                cost=float(cost) if cost else 0,
                printer_target=printer_target,
                track_stock=track_stock,
                stock_quantity=float(stock_quantity) if stock_quantity else 0,
                sort_order=int(sort_order) if sort_order else 0,
                is_active=is_active
            )
            
            # Handle image upload
            images = request.FILES.getlist('images')
            for idx, image in enumerate(images):
                ProductPhoto.objects.create(
                    product=product,
                    photo=image,
                    is_primary=(idx == 0)  # First image is primary
                )
            
            messages.success(request, f'Product "{product.name}" created successfully!')
            
            return JsonResponse({
                'success': True,
                'message': 'Product created successfully',
                'redirect': '/products/'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    # GET request - return form
    brands = Brand.objects.filter(is_active=True).order_by('name')
    categories = Category.objects.filter(is_active=True).select_related('brand').order_by('brand__name', 'name')
    
    return render(request, 'products/product/_form.html', {
        'brands': brands,
        'categories': categories
    })


@login_required
@require_http_methods(["GET", "POST"])
def product_update(request, pk):
    """Update existing product"""
    product = get_object_or_404(
        Product.objects.select_related('brand', 'category').prefetch_related('photos'),
        pk=pk
    )
    
    if request.method == 'POST':
        try:
            category_id = request.POST.get('category_id')
            sku = request.POST.get('sku', '').strip()
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            price = request.POST.get('price', '0')
            cost = request.POST.get('cost', '0')
            printer_target = request.POST.get('printer_target', 'kitchen')
            track_stock = request.POST.get('track_stock') == 'on'
            stock_quantity = request.POST.get('stock_quantity', '0')
            sort_order = request.POST.get('sort_order', '0')
            is_active = request.POST.get('is_active') == 'on'
            
            if not all([category_id, sku, name, price]):
                return JsonResponse({
                    'success': False,
                    'message': 'Category, SKU, Name and Price are required'
                }, status=400)
            
            # Check SKU uniqueness per brand (exclude current product)
            if Product.objects.filter(brand=product.brand, sku=sku).exclude(pk=pk).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'SKU "{sku}" already exists for this brand'
                }, status=400)
            
            # Update product
            product.category_id = category_id
            product.sku = sku
            product.name = name
            product.description = description
            product.price = float(price)
            product.cost = float(cost) if cost else 0
            product.printer_target = printer_target
            product.track_stock = track_stock
            product.stock_quantity = float(stock_quantity) if stock_quantity else 0
            product.sort_order = int(sort_order) if sort_order else 0
            product.is_active = is_active
            product.save()
            
            # Handle new image uploads
            images = request.FILES.getlist('images')
            if images:
                # Get current primary photo status
                has_primary = product.photos.filter(is_primary=True).exists()
                
                for idx, image in enumerate(images):
                    ProductPhoto.objects.create(
                        product=product,
                        photo=image,
                        is_primary=(idx == 0 and not has_primary)  # First image is primary if no primary exists
                    )
            
            messages.success(request, f'Product "{product.name}" updated successfully!')
            
            return JsonResponse({
                'success': True,
                'message': 'Product updated successfully',
                'redirect': '/products/'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    # GET request - return form
    brands = Brand.objects.filter(is_active=True).order_by('name')
    categories = Category.objects.filter(brand=product.brand, is_active=True).order_by('name')
    
    return render(request, 'products/product/_form.html', {
        'product': product,
        'brands': brands,
        'categories': categories
    })


@login_required
@require_http_methods(["POST", "DELETE"])
def product_delete(request, pk):
    """Delete product"""
    try:
        product = get_object_or_404(Product, pk=pk)
        product_name = product.name
        product.delete()
        
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        
        return JsonResponse({
            'success': True,
            'message': 'Product deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST", "DELETE"])
def product_photo_delete(request, pk):
    """Delete product photo"""
    try:
        photo = get_object_or_404(ProductPhoto, pk=pk)
        photo.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Photo deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
