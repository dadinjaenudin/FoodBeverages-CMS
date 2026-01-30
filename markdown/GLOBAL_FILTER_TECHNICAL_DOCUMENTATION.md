# Global Filter System - Technical Documentation
**Created:** 2026-01-26  
**Version:** 2.0  
**System:** FoodBeverages CMS

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Hierarchy Structure](#hierarchy-structure)
4. [Implementation Details](#implementation-details)
5. [Auto-Fill Logic](#auto-fill-logic)
6. [Frontend Integration](#frontend-integration)
7. [Backend Processing](#backend-processing)
8. [Session Management](#session-management)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The **Global Filter System** is a multi-level hierarchical filter that allows users to select their working context across the entire application. It consists of three levels:

```
Company → Brand → Store
```

### **Purpose**
- Provide context-aware data filtering throughout the application
- Reduce redundant filtering in every view
- Improve user experience with persistent selection
- Enable multi-tenancy support

### **Key Features**
- ✅ **Auto-Fill Intelligence**: Selecting a higher level auto-fills lower levels
- ✅ **Session Persistence**: Selections persist across page navigations
- ✅ **Real-time Updates**: Changes reflect immediately via HTMX
- ✅ **Validation**: Ensures data consistency and access control
- ✅ **Flexible Access**: Support for all hierarchy levels

---

## 🏗️ Architecture

### **System Components**

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (Header)                   │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ Company  │ -> │  Brand   │ -> │  Store   │              │
│  │ Dropdown │    │ Dropdown │    │ Dropdown │              │
│  └──────────┘    └──────────┘    └──────────┘              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              HTMX POST: /global/set-filter/                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│           Backend: global_filter_views.set_global_filter()   │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  1. Receive: company_id / brand_id / store_id      │    │
│  │  2. Process Auto-Fill Logic                        │    │
│  │  3. Update Session Variables                       │    │
│  │  4. Return HX-Redirect                             │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Session Storage (Server-Side)               │
│  • global_company_id                                         │
│  • global_brand_id                                           │
│  • global_store_id                                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│            Context Processor: global_filters()               │
│  Makes session data available to all templates               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              All Views and Templates Access                  │
│  • request.session['global_company_id']                      │
│  • request.session['global_brand_id']                        │
│  • request.session['global_store_id']                        │
│                                                              │
│  • {{ current_company }}                                     │
│  • {{ current_brand }}                                       │
│  • {{ current_store }}                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Hierarchy Structure

### **Data Model Relationships**

```python
Company (1)
    ├── Brand (N)
    │   ├── Store (N)
    │   ├── Product (N)
    │   ├── Category (N)
    │   └── ... other brand-level data
    │
    └── TableArea (N)
        └── Store (1) - Optional
```

### **Database Schema**

```sql
-- Company Table
CREATE TABLE company (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE
);

-- Brand Table
CREATE TABLE brand (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES company(id),
    name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE
);

-- Store Table
CREATE TABLE store (
    id UUID PRIMARY KEY,
    brand_id UUID REFERENCES brand(id),
    store_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE
);
```

### **Django Models**

```python
class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

class Brand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

class Store(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    store_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
```

---

## 🔧 Implementation Details

### **File Structure**

```
FoodBeverages-CMS/
├── core/
│   ├── views/
│   │   └── global_filter_views.py          # Main filter logic
│   ├── context_processors.py               # Template context
│   ├── middleware.py                       # Validation middleware
│   ├── urls_global.py                      # URL routing
│   └── models.py                           # Company, Brand, Store models
│
├── templates/
│   └── base.html                           # Global filter UI in header
│
└── config/
    └── settings.py                         # Context processor registration
```

---

## 🧠 Auto-Fill Logic (Version 2.0)

### **Decision Flow**

The auto-fill logic follows a priority-based approach:

```
Priority 1: Store Selection
    ↓
    If store_id is provided:
        → Auto-fill: Store ✓
        → Auto-fill: Brand (from Store.brand) ✓
        → Auto-fill: Company (from Brand.company) ✓
        → Result: All 3 levels filled

Priority 2: Brand Selection
    ↓
    If brand_id is provided (and no store_id):
        → Auto-fill: Brand ✓
        → Auto-fill: Company (from Brand.company) ✓
        → Clear: Store (brand changed, need new selection)
        → Result: Company + Brand filled

Priority 3: Company Selection
    ↓
    If company_id is provided (and no brand_id or store_id):
        → Auto-fill: Company ✓
        → Auto-fill: Brand (first active brand alphabetically) ✓
        → Clear: Store (company changed, need new selection)
        → Result: Company + Default Brand filled
```

### **Backend Implementation**

**File:** `core/views/global_filter_views.py`

```python
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from core.models import Company, Brand, Store

@login_required
@require_POST
def set_global_filter(request):
    company_id = request.POST.get('company_id')
    brand_id = request.POST.get('brand_id')
    store_id = request.POST.get('store_id')
    
    # Priority 1: Store selection
    if store_id:
        try:
            store = Store.objects.select_related('brand', 'brand__company').get(
                id=store_id, is_active=True
            )
            request.session['global_store_id'] = store_id
            request.session['global_brand_id'] = str(store.brand.id)
            request.session['global_company_id'] = str(store.brand.company.id)
        except Store.DoesNotExist:
            pass
    
    # Priority 2: Brand selection
    elif brand_id:
        request.session['global_brand_id'] = brand_id
        try:
            brand = Brand.objects.select_related('company').get(
                id=brand_id, is_active=True
            )
            request.session['global_company_id'] = str(brand.company.id)
        except Brand.DoesNotExist:
            pass
        request.session.pop('global_store_id', None)
    
    # Priority 3: Company selection
    elif company_id:
        request.session['global_company_id'] = company_id
        try:
            first_brand = Brand.objects.filter(
                company_id=company_id, is_active=True
            ).order_by('name').first()
            
            if first_brand:
                request.session['global_brand_id'] = str(first_brand.id)
            else:
                request.session.pop('global_brand_id', None)
        except Exception:
            pass
        request.session.pop('global_store_id', None)
    
    next_url = request.META.get('HTTP_REFERER', '/')
    return redirect(next_url)
```

---

## 💾 Session Management

### **Session Variables**

The global filter uses Django's session framework to store user selections:

```python
# Session Keys
'global_company_id'  # UUID string of selected company
'global_brand_id'    # UUID string of selected brand
'global_store_id'    # UUID string of selected store
```

### **Session Lifecycle**

```
User Login
    ↓
Session Created (empty filters)
    ↓
User Selects Company
    ↓
Session Updated: global_company_id, global_brand_id (auto-filled)
    ↓
User Navigates to Different Pages
    ↓
Session Persists (filters remain active)
    ↓
User Selects Different Store
    ↓
Session Updated: All 3 IDs updated
    ↓
User Logs Out
    ↓
Session Destroyed (filters cleared)
```

### **Accessing Session Data**

**In Views:**
```python
def my_view(request):
    company_id = request.session.get('global_company_id')
    brand_id = request.session.get('global_brand_id')
    store_id = request.session.get('global_store_id')
    
    # Use filters in queries
    products = Product.objects.filter(brand_id=brand_id)
    return render(request, 'template.html', {'products': products})
```

**In Templates:**
```django
<!-- Access via context processor -->
<p>Current Company: {{ current_company.name }}</p>
<p>Current Brand: {{ current_brand.name }}</p>
<p>Current Store: {{ current_store.store_name }}</p>
```

---

## 🔄 Context Processor

### **Purpose**

The context processor makes global filter data available to ALL templates automatically, without needing to pass it in every view.

### **Implementation**

**File:** `core/context_processors.py`

```python
from core.models import Company, Brand, Store

def global_filters(request):
    """
    Context processor to add global filter data to all templates
    """
    context = {
        'current_company': None,
        'current_brand': None,
        'current_store': None,
        'available_companies': [],
        'available_brands': [],
        'available_stores': [],
    }
    
    if not request.user.is_authenticated:
        return context
    
    # Get current selections from session
    company_id = request.session.get('global_company_id')
    brand_id = request.session.get('global_brand_id')
    store_id = request.session.get('global_store_id')
    
    # Load current company
    if company_id:
        try:
            context['current_company'] = Company.objects.get(
                id=company_id, 
                is_active=True
            )
        except Company.DoesNotExist:
            request.session.pop('global_company_id', None)
    
    # Load current brand
    if brand_id:
        try:
            context['current_brand'] = Brand.objects.select_related('company').get(
                id=brand_id, 
                is_active=True
            )
        except Brand.DoesNotExist:
            request.session.pop('global_brand_id', None)
    
    # Load current store
    if store_id:
        try:
            context['current_store'] = Store.objects.select_related('brand').get(
                id=store_id, 
                is_active=True
            )
        except Store.DoesNotExist:
            request.session.pop('global_store_id', None)
    
    # Get available options based on user permissions
    if request.user.is_superuser:
        context['available_companies'] = Company.objects.filter(is_active=True)
        context['available_brands'] = Brand.objects.filter(is_active=True)
        context['available_stores'] = Store.objects.filter(is_active=True)
    else:
        # Filter based on user's company/brand assignment
        if hasattr(request.user, 'company'):
            context['available_companies'] = [request.user.company]
            context['available_brands'] = Brand.objects.filter(
                company=request.user.company, 
                is_active=True
            )
            context['available_stores'] = Store.objects.filter(
                brand__company=request.user.company, 
                is_active=True
            )
    
    return context
```

### **Registration**

**File:** `config/settings.py`

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.global_filters',  # ✅ Add this
            ],
        },
    },
]
```

---

## 🎯 Best Practices

### **1. Using Global Filter in Views**

✅ **DO:**
```python
def product_list(request):
    brand_id = request.session.get('global_brand_id')
    
    if not brand_id:
        messages.warning(request, 'Please select a brand first')
        return redirect('dashboard')
    
    products = Product.objects.filter(brand_id=brand_id, is_active=True)
    return render(request, 'products/list.html', {'products': products})
```

❌ **DON'T:**
```python
def product_list(request):
    # Don't query all products without filter
    products = Product.objects.all()  # ❌ Performance issue!
    return render(request, 'products/list.html', {'products': products})
```

### **2. Form Integration**

✅ **DO - Auto-assign from global filter:**
```python
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            # Auto-assign from global filter
            product.brand_id = request.session.get('global_brand_id')
            product.save()
            return redirect('product:list')
```

❌ **DON'T - Require manual selection:**
```python
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)  # Form includes brand dropdown
        # User has to select brand again even though global filter is set ❌
        if form.is_valid():
            form.save()
```

### **3. Validation**

✅ **DO - Validate access:**
```python
def edit_product(request, product_id):
    brand_id = request.session.get('global_brand_id')
    
    try:
        # Ensure product belongs to current brand
        product = Product.objects.get(
            id=product_id, 
            brand_id=brand_id,  # ✅ Security check
            is_active=True
        )
    except Product.DoesNotExist:
        messages.error(request, 'Product not found or access denied')
        return redirect('product:list')
    
    # ... rest of view
```

### **4. API Endpoints**

✅ **DO - Include in API filters:**
```python
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        brand_id = self.request.session.get('global_brand_id')
        
        if not brand_id:
            return Product.objects.none()
        
        return Product.objects.filter(
            brand_id=brand_id,
            is_active=True
        )
```

### **5. Testing**

✅ **DO - Mock session in tests:**
```python
from django.test import TestCase, RequestFactory

class ProductViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.company = Company.objects.create(name='Test Co')
        self.brand = Brand.objects.create(name='Test Brand', company=self.company)
    
    def test_product_list_with_filter(self):
        request = self.factory.get('/products/')
        # Mock session
        request.session = {'global_brand_id': str(self.brand.id)}
        
        response = product_list(request)
        self.assertEqual(response.status_code, 200)
```

---

## 🐛 Troubleshooting

### **Common Issues**

#### **Issue 1: Brand Not Auto-Filling When Company Selected**

**Symptom:**
```
User selects Company → Brand dropdown remains empty
```

**Cause:**
Company form includes hidden `brand_id` input

**Solution:**
Remove hidden input from Company form
```html
<!-- Remove this: -->
<input type="hidden" name="brand_id" value="{{ current_brand.id }}">
```

#### **Issue 2: Filters Not Persisting**

**Symptom:**
```
User selects filter → Navigates to another page → Filter resets
```

**Cause:**
Session middleware not configured or session backend issue

**Solution:**
Check `settings.py`:
```python
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',  # ✅ Must be present
    # ... other middleware
]

SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # or 'cache', 'file'
```

#### **Issue 3: Context Processor Not Working**

**Symptom:**
```
{{ current_company }} is empty in templates
```

**Cause:**
Context processor not registered

**Solution:**
Add to `settings.py`:
```python
'context_processors': [
    # ... other processors
    'core.context_processors.global_filters',  # ✅ Add this
]
```

#### **Issue 4: Filters Showing Wrong Data**

**Symptom:**
```
User A sees User B's filters
```

**Cause:**
Session data cached or shared between users

**Solution:**
1. Check session backend is not shared
2. Clear sessions: `python manage.py clearsessions`
3. Use database or secure cache for sessions

---

## 📊 Performance Optimization

### **1. Use Select Related**

```python
# ✅ Good - One query
store = Store.objects.select_related('brand', 'brand__company').get(id=store_id)

# ❌ Bad - Multiple queries
store = Store.objects.get(id=store_id)
brand = store.brand  # Additional query
company = brand.company  # Another query
```

### **2. Cache Available Options**

```python
from django.core.cache import cache

def global_filters(request):
    # Cache companies list for 1 hour
    cache_key = f'available_companies_{request.user.id}'
    companies = cache.get(cache_key)
    
    if companies is None:
        companies = Company.objects.filter(is_active=True)
        cache.set(cache_key, companies, 3600)
    
    return {'available_companies': companies}
```

### **3. Prefetch for Lists**

```python
# ✅ Good - Prefetch related data
brands = Brand.objects.filter(is_active=True).select_related('company')

# ❌ Bad - N+1 queries
brands = Brand.objects.filter(is_active=True)
for brand in brands:
    print(brand.company.name)  # Query for each brand
```

---

## 🔐 Security Considerations

### **1. Validate User Access**

```python
def set_global_filter(request):
    brand_id = request.POST.get('brand_id')
    
    # ✅ Validate user has access to this brand
    if not request.user.is_superuser:
        if not Brand.objects.filter(
            id=brand_id,
            company=request.user.company  # Check user's company
        ).exists():
            messages.error(request, 'Access denied')
            return redirect('dashboard')
    
    # ... proceed with setting filter
```

### **2. Sanitize Session Data**

```python
# ✅ Always validate IDs from session
brand_id = request.session.get('global_brand_id')
if brand_id:
    try:
        uuid.UUID(brand_id)  # Validate UUID format
    except ValueError:
        request.session.pop('global_brand_id', None)
```

### **3. Prevent Session Fixation**

```python
def set_global_filter(request):
    # ... update session
    
    # Regenerate session ID for security
    if not request.session.session_key:
        request.session.create()
```

---

## 📚 Related Documentation

- **Floor Plan System:** `FLOOR_PLAN_TECHNICAL_DOCUMENTATION.md`
- **Project Summary:** `PROJECT_SUMMARY.md`
- **API Documentation:** `API_DOCUMENTATION.md`

---

## 🎓 Learning Resources

### **For New Developers**

1. **Understand the Hierarchy:**
   - Company owns Brands
   - Brand owns Stores
   - Data flows top-down

2. **Session Management:**
   - Django Sessions documentation
   - How middleware works
   - Context processors explained

3. **Auto-Fill Logic:**
   - Read the priority flow diagram
   - Test with different scenarios
   - Understand why we avoid hidden inputs

### **Testing Checklist**

- [ ] Select Company → Brand auto-fills
- [ ] Select different Brand → Works correctly
- [ ] Select Store → Brand and Company auto-fill
- [ ] Navigate to different pages → Filters persist
- [ ] Logout and login → Filters reset
- [ ] Multiple users → Each has own filters

---

## 📝 Changelog

### **Version 2.0** (2026-01-26)
- ✅ Fixed auto-fill logic with proper priority
- ✅ Removed hidden brand_id from Company form
- ✅ Added Company auto-fill when Brand selected
- ✅ Improved documentation

### **Version 1.0** (Previous)
- Initial global filter implementation
- Basic session management
- Context processor setup

---

**Last Updated:** 2026-01-26  
**Maintained By:** Development Team  
**Status:** ✅ Production Ready
