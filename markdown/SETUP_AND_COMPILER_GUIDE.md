# Setup Environment + Implement Compiler
## Complete Step-by-Step Guide

**Duration:** Week 1-2 (10 working days)  
**Goal:** Production-ready Promotion Compiler that converts Django models to JSON  
**Status:** Ready to Start

---

## 📋 Overview

### What We'll Build
```
Input:  Django Promotion Model (Database)
         ↓
Process: PromotionCompiler Service
         ↓
Output: JSON Format (POS-compatible)
```

### Success Criteria
- ✅ Compiler handles all 12 promotion types
- ✅ JSON output validated and correct
- ✅ Unit tests pass (80%+ coverage)
- ✅ Performance < 100ms per promotion
- ✅ Works with real promotion data

---

## 🎯 Day-by-Day Plan

### **DAY 1: Environment Setup**

#### Morning (3-4 hours)
1. Install dependencies
2. Configure Django settings
3. Setup project structure
4. Verify current models

#### Afternoon (3-4 hours)
1. Create feature branch
2. Setup testing framework
3. Create initial files
4. Test basic setup

---

### **DAY 2-3: Core Compiler Structure**

#### Day 2 Morning
1. Create PromotionCompiler class
2. Implement main compile_promotion() method
3. Implement compile_time_rules()
4. Implement compile_scope()

#### Day 2 Afternoon
1. Implement compile_targeting()
2. Implement compile_limits()
3. Basic unit tests

#### Day 3 Full Day
1. Implement compile_rules() dispatcher
2. Test core structure
3. Handle edge cases
4. Code review

---

### **DAY 4-6: Type-Specific Compilers**

#### Day 4: Simple Types
1. _compile_percent_discount()
2. _compile_amount_discount()
3. _compile_payment_discount()
4. _compile_cashback()
5. Unit tests for each

#### Day 5: Medium Complexity
1. _compile_bogo()
2. _compile_combo()
3. _compile_free_item()
4. _compile_happy_hour()
5. Unit tests for each

#### Day 6: Complex Types
1. _compile_package()
2. _compile_mix_match()
3. _compile_upsell()
4. _compile_threshold()
5. Unit tests for each

---

### **DAY 7-8: Cross-Brand & Batch Operations**

#### Day 7
1. Implement compile_cross_brand()
2. Test cross-brand scenarios
3. Implement compile_multiple()
4. Implement compile_for_store()

#### Day 8
1. Batch operation optimization
2. Performance testing
3. Memory optimization
4. Edge case testing

---

### **DAY 9-10: Testing & Polish**

#### Day 9
1. Integration tests
2. Test with real promotion data
3. Performance benchmarks
4. Bug fixes

#### Day 10
1. Code review
2. Documentation
3. Final testing
4. Merge to main

---

## 🛠️ Implementation Steps

### STEP 1: Install Dependencies (30 minutes)

```bash
# Activate virtual environment
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Install required packages
pip install djangorestframework==3.14.0
pip install drf-spectacular==0.26.5
pip install django-filter==23.3
pip install python-dateutil==2.8.2

# For testing
pip install pytest==7.4.3
pip install pytest-django==4.7.0
pip install pytest-cov==4.1.0
pip install factory-boy==3.3.0

# Update requirements.txt
pip freeze > requirements.txt
```

---

### STEP 2: Update Django Settings (15 minutes)

**File:** `config/settings.py`

Add to INSTALLED_APPS:
```python
INSTALLED_APPS = [
    # ... existing apps
    'rest_framework',
    'drf_spectacular',
    'django_filters',
]
```

Add REST Framework configuration:
```python
# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'F&B Promotion System API',
    'DESCRIPTION': 'Promotion System API for POS Integration',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
```

---

### STEP 3: Create Directory Structure (10 minutes)

```bash
# Create services directory
mkdir promotions\services
New-Item promotions\services\__init__.py -ItemType File

# Create tests directory
mkdir promotions\tests
New-Item promotions\tests\__init__.py -ItemType File
mkdir promotions\tests\fixtures

# Create utils directory (optional)
mkdir promotions\utils
New-Item promotions\utils\__init__.py -ItemType File
```

**Directory structure:**
```
promotions/
├── services/
│   ├── __init__.py
│   └── compiler.py          # ← We'll create this
├── tests/
│   ├── __init__.py
│   ├── test_compiler.py     # ← We'll create this
│   └── fixtures/
│       └── sample_promotions.json
├── utils/
│   └── __init__.py
└── ... (existing files)
```

---

### STEP 4: Create pytest Configuration (10 minutes)

**File:** `pytest.ini` (in project root)

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --strict-markers
    --tb=short
    --cov=promotions
    --cov-report=html
    --cov-report=term-missing
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
```

**File:** `conftest.py` (in promotions/tests/)

```python
"""
Pytest configuration for promotions app
"""
import pytest
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta
from promotions.models import Promotion
from core.models import Company, Brand, Store, User
from products.models import Category, Product


@pytest.fixture
def sample_company(db):
    """Create sample company"""
    return Company.objects.create(
        name="Test Company",
        code="TEST-CO"
    )


@pytest.fixture
def sample_brand(db, sample_company):
    """Create sample brand"""
    return Brand.objects.create(
        company=sample_company,
        name="Test Brand",
        code="TEST-BRAND"
    )


@pytest.fixture
def sample_store(db, sample_company, sample_brand):
    """Create sample store"""
    return Store.objects.create(
        company=sample_company,
        brand=sample_brand,
        name="Test Store",
        code="TEST-STORE"
    )


@pytest.fixture
def sample_user(db, sample_company):
    """Create sample user"""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        company=sample_company,
        role_scope="company"
    )


@pytest.fixture
def sample_category(db, sample_company):
    """Create sample category"""
    return Category.objects.create(
        company=sample_company,
        name="Test Category",
        code="TEST-CAT"
    )


@pytest.fixture
def sample_product(db, sample_company, sample_brand, sample_category):
    """Create sample product"""
    return Product.objects.create(
        company=sample_company,
        brand=sample_brand,
        category=sample_category,
        name="Test Product",
        sku="TEST-SKU",
        price=Decimal('50000.00')
    )


@pytest.fixture
def base_promotion_data(sample_company, sample_user):
    """Base data for creating promotions"""
    today = timezone.now().date()
    return {
        'company': sample_company,
        'name': 'Test Promotion',
        'code': 'TEST-PROMO',
        'start_date': today,
        'end_date': today + timedelta(days=30),
        'created_by': sample_user,
        'is_active': True,
    }
```

---

### STEP 5: Verify Current Models (15 minutes)

Let's check if Promotion model is ready:

```bash
# Open Django shell
python manage.py shell
```

```python
# Test model access
from promotions.models import Promotion
from core.models import Company, User

# Check if models work
print(Promotion.objects.count())
print(Promotion.PROMO_TYPE_CHOICES)

# Exit
exit()
```

---

## 📝 Implementation Checklist

### Day 1: Setup ✅
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] settings.py updated
- [ ] Directory structure created
- [ ] pytest configured
- [ ] conftest.py created
- [ ] Models verified
- [ ] Feature branch created (`git checkout -b feature/promotion-compiler`)

### Day 2-3: Core Structure
- [ ] PromotionCompiler class created
- [ ] compile_promotion() implemented
- [ ] compile_time_rules() implemented
- [ ] compile_scope() implemented
- [ ] compile_targeting() implemented
- [ ] compile_limits() implemented
- [ ] Basic tests written

### Day 4: Simple Types
- [ ] _compile_percent_discount() ✅
- [ ] _compile_amount_discount() ✅
- [ ] _compile_payment_discount() ✅
- [ ] _compile_cashback() ✅
- [ ] Tests for simple types ✅

### Day 5: Medium Types
- [ ] _compile_bogo() ✅
- [ ] _compile_combo() ✅
- [ ] _compile_free_item() ✅
- [ ] _compile_happy_hour() ✅
- [ ] Tests for medium types ✅

### Day 6: Complex Types
- [ ] _compile_package() ✅
- [ ] _compile_mix_match() ✅
- [ ] _compile_upsell() ✅
- [ ] _compile_threshold() ✅
- [ ] Tests for complex types ✅

### Day 7-8: Advanced Features
- [ ] compile_cross_brand() ✅
- [ ] compile_multiple() ✅
- [ ] compile_for_store() ✅
- [ ] Batch optimization ✅
- [ ] Performance tests ✅

### Day 9-10: Polish
- [ ] Integration tests ✅
- [ ] Real data testing ✅
- [ ] Performance benchmarks ✅
- [ ] Code review ✅
- [ ] Documentation ✅
- [ ] Merge to main ✅

---

## 🧪 Testing Strategy

### Unit Tests (Per Type)
```python
# Example test structure
def test_compile_percent_discount():
    # 1. Create promotion
    # 2. Compile
    # 3. Assert JSON structure
    # 4. Assert values
    pass
```

### Integration Tests
```python
def test_compile_for_store():
    # 1. Create multiple promotions
    # 2. Compile for specific store
    # 3. Assert correct filtering
    pass
```

### Performance Tests
```python
def test_compilation_performance():
    # 1. Create 100 promotions
    # 2. Time compilation
    # 3. Assert < 100ms per promotion
    pass
```

---

## ⚡ Quick Commands

### Run Tests
```bash
# All tests
pytest promotions/tests/

# Specific test file
pytest promotions/tests/test_compiler.py

# With coverage
pytest promotions/tests/ --cov=promotions --cov-report=html

# Verbose
pytest promotions/tests/ -v

# Stop on first failure
pytest promotions/tests/ -x
```

### Check Code
```bash
# Check for issues
python manage.py check

# Run migrations (if any)
python manage.py makemigrations
python manage.py migrate

# Shell for manual testing
python manage.py shell
```

---

## 📊 Expected Outcomes

After Week 1-2, you will have:

✅ **Working Compiler Service**
- Handles all 12 promotion types
- Converts Django models to JSON
- Optimized for batch operations

✅ **Comprehensive Tests**
- 80%+ code coverage
- Unit tests for each type
- Integration tests
- Performance tests

✅ **Production Ready**
- Error handling
- Logging
- Performance optimized
- Well documented

---

## 🚀 Ready to Start?

Next, I will:
1. ✅ Create the complete `compiler.py` file
2. ✅ Create test files
3. ✅ Create sample fixtures
4. ✅ Help you run and test everything

**Should I proceed with creating the compiler.py file now?** 🎯

