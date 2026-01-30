# Promotion Compiler - Quick Start Guide
## How to Use the Promotion Compiler

**Status:** ✅ READY TO USE  
**Files Created:** 5 files (1,400+ lines of code)  
**Test Coverage:** 20+ unit tests

---

## 🚀 What You Can Do Now

The **PromotionCompiler** is ready to use! It can convert your Django Promotion models into JSON format for POS devices.

---

## 📁 Files Created

```
promotions/
├── services/
│   ├── __init__.py
│   └── compiler.py                    ✅ 664 lines - Main compiler
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    ✅ 149 lines - Test fixtures
│   └── test_compiler.py               ✅ 383 lines - 20+ tests
│
└── management/
    └── commands/
        └── test_compiler.py           ✅ 131 lines - Manual testing tool
```

---

## 🎯 Quick Usage

### 1. Test with Django Shell

```bash
# Open Django shell
python manage.py shell
```

```python
# Import compiler
from promotions.services.compiler import PromotionCompiler, compile_promotion
from promotions.models import Promotion

# Method 1: Using the class
compiler = PromotionCompiler()

# Get a promotion
promo = Promotion.objects.first()

# Compile it
result = compiler.compile_promotion(promo)

# Print result
import json
print(json.dumps(result, indent=2, default=str))

# Method 2: Using convenience function
result = compile_promotion(promo)
```

---

### 2. Test All Promotions for a Store

```python
from promotions.services.compiler import compile_promotions_for_store

# Get store ID
from core.models import Store
store = Store.objects.first()

# Compile all promotions for this store
promotions = compile_promotions_for_store(str(store.id))

# Check how many promotions
print(f"Found {len(promotions)} promotions for store")

# Print first promotion
import json
print(json.dumps(promotions[0], indent=2, default=str))
```

---

### 3. Using Management Command

```bash
# Show promotion statistics
python manage.py test_compiler

# Test all active promotions
python manage.py test_compiler --all

# Test specific promotion
python manage.py test_compiler --promotion-id <uuid>

# Test promotions for store
python manage.py test_compiler --store-id <uuid>

# Pretty print output
python manage.py test_compiler --all --pretty
```

---

## 🧪 Running Tests

### Install pytest (if not already installed)

```bash
pip install pytest pytest-django pytest-cov factory-boy
```

### Run Tests

```bash
# Run all compiler tests
pytest promotions/tests/test_compiler.py -v

# Run with coverage
pytest promotions/tests/test_compiler.py --cov=promotions.services.compiler

# Run specific test
pytest promotions/tests/test_compiler.py::TestPromotionCompiler::test_compile_percent_discount -v

# Run all tests in promotions app
pytest promotions/tests/ -v
```

---

## 📖 Example Output

### Input: Django Promotion Model
```python
Promotion(
    code='WEEKEND20',
    name='Weekend Special 20% Off',
    promo_type='percent_discount',
    discount_percent=20.0,
    max_discount_amount=50000.0,
    start_date='2026-02-01',
    end_date='2026-02-28',
    is_active=True
)
```

### Output: Compiled JSON
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "code": "WEEKEND20",
  "name": "Weekend Special 20% Off",
  "promo_type": "percent_discount",
  "execution_stage": "item_level",
  "execution_priority": 500,
  "is_active": true,
  "is_auto_apply": true,
  "validity": {
    "start_date": "2026-02-01",
    "end_date": "2026-02-28",
    "time_start": null,
    "time_end": null,
    "days_of_week": [6, 7],
    "exclude_holidays": false
  },
  "scope": {
    "apply_to": "all",
    "exclude_categories": [],
    "exclude_products": []
  },
  "targeting": {
    "stores": "all",
    "brands": "all",
    "member_only": false,
    "customer_type": "all"
  },
  "rules": {
    "type": "percent",
    "discount_percent": 20.0,
    "max_discount_amount": 50000.0,
    "min_purchase": 0.0
  },
  "limits": {
    "max_uses": null,
    "max_uses_per_customer": null,
    "max_uses_per_day": null,
    "current_uses": 0
  },
  "compiled_at": "2026-01-27T15:30:00+07:00",
  "compiler_version": "1.0"
}
```

---

## ✅ What's Supported

### All 12 Promotion Types
- ✅ Percent Discount
- ✅ Amount Discount
- ✅ Buy X Get Y (BOGO)
- ✅ Combo Deal
- ✅ Free Item
- ✅ Happy Hour
- ✅ Cashback
- ✅ Payment Method Discount
- ✅ Package/Set Menu
- ✅ Mix & Match
- ✅ Upsell/Add-on
- ✅ Threshold/Tiered

### Features
- ✅ Category targeting
- ✅ Product targeting
- ✅ Store selection
- ✅ Brand selection
- ✅ Time-based rules
- ✅ Member-only promotions
- ✅ Usage limits
- ✅ Cross-brand support
- ✅ Batch compilation
- ✅ Error handling

---

## 🔍 Testing Each Promotion Type

### Test Percent Discount
```python
from decimal import Decimal
from promotions.models import Promotion
from promotions.services.compiler import compile_promotion

promo = Promotion.objects.create(
    company=your_company,
    code='TEST20',
    name='Test 20% Off',
    promo_type='percent_discount',
    discount_percent=Decimal('20.00'),
    start_date='2026-01-01',
    end_date='2026-12-31',
    created_by=your_user
)

result = compile_promotion(promo)
print(result['rules'])
# Output: {'type': 'percent', 'discount_percent': 20.0, ...}
```

### Test BOGO
```python
promo = Promotion.objects.create(
    company=your_company,
    code='BOGO21',
    name='Buy 2 Get 1 Free',
    promo_type='buy_x_get_y',
    buy_quantity=2,
    get_quantity=1,
    discount_percent=Decimal('100.00'),
    start_date='2026-01-01',
    end_date='2026-12-31',
    created_by=your_user
)

result = compile_promotion(promo)
print(result['rules'])
# Output: {'type': 'bogo', 'buy_quantity': 2, 'get_quantity': 1, ...}
```

### Test Happy Hour
```python
from datetime import time

promo = Promotion.objects.create(
    company=your_company,
    code='HAPPY50',
    name='Happy Hour 50% Off',
    promo_type='happy_hour',
    discount_percent=Decimal('50.00'),
    valid_time_start=time(14, 0),
    valid_time_end=time(17, 0),
    valid_days=[1, 2, 3, 4, 5],  # Mon-Fri
    start_date='2026-01-01',
    end_date='2026-12-31',
    created_by=your_user
)

result = compile_promotion(promo)
print(result['rules'])
# Output: {'type': 'happy_hour', 'discount_percent': 50.0, 'time_start': '14:00:00', ...}
```

---

## 🐛 Troubleshooting

### Issue: Module not found
```bash
# Make sure you're in the project directory
cd /path/to/FoodBeverages-CMS

# Make sure Django can find the module
python manage.py shell
>>> from promotions.services.compiler import PromotionCompiler
```

### Issue: No promotions found
```python
# Check if promotions exist
from promotions.models import Promotion
print(Promotion.objects.count())

# Check active promotions
print(Promotion.objects.filter(is_active=True).count())

# Create test promotion if needed
# (see examples above)
```

### Issue: Tests failing
```bash
# Check database
python manage.py migrate

# Make sure test database is clean
pytest promotions/tests/ --create-db

# Run with verbose output
pytest promotions/tests/test_compiler.py -v -s
```

---

## 📊 Performance

Expected performance:
- **Single promotion:** < 10ms
- **100 promotions:** < 500ms
- **Store sync (50 promotions):** < 200ms

Test performance:
```python
import time
from promotions.services.compiler import PromotionCompiler
from promotions.models import Promotion

compiler = PromotionCompiler()
promotions = Promotion.objects.filter(is_active=True)[:100]

start = time.time()
results = compiler.compile_multiple(promotions)
elapsed = time.time() - start

print(f"Compiled {len(results)} promotions in {elapsed:.3f}s")
print(f"Average: {elapsed/len(results)*1000:.2f}ms per promotion")
```

---

## 🎯 Next Steps

Now that the compiler is ready, you can proceed to:

1. **Create Sync API** - Build REST endpoints for POS to download promotions
2. **Add Validation** - Implement validation engine before compilation
3. **Build Dashboard** - Preview compiled JSON in admin interface
4. **Performance Optimization** - Add caching for frequently accessed promotions
5. **Integration Testing** - Test with real POS devices

Refer to **BACKEND_IMPLEMENTATION_ROADMAP.md** for the complete implementation plan.

---

## 💡 Tips

### Tip 1: Preview Compilation in Admin
You can add a preview button in Django admin:
```python
# promotions/admin.py
from django.contrib import admin
from promotions.models import Promotion
from promotions.services.compiler import compile_promotion
import json

class PromotionAdmin(admin.ModelAdmin):
    readonly_fields = ['preview_compiled']
    
    def preview_compiled(self, obj):
        if obj.id:
            result = compile_promotion(obj)
            return f"<pre>{json.dumps(result, indent=2, default=str)}</pre>"
        return "Save to preview"
    preview_compiled.short_description = "Compiled JSON"
    preview_compiled.allow_tags = True
```

### Tip 2: Export to File
```python
import json
from promotions.services.compiler import compile_promotions_for_store

# Compile and save to file
promotions = compile_promotions_for_store('store-uuid')
with open('promotions_export.json', 'w') as f:
    json.dump(promotions, f, indent=2, default=str)
```

### Tip 3: Validate JSON Schema
```python
import jsonschema

# Define schema (example)
schema = {
    "type": "object",
    "required": ["id", "code", "promo_type", "rules"],
    "properties": {
        "id": {"type": "string"},
        "code": {"type": "string"},
        "promo_type": {"type": "string"},
        "rules": {"type": "object"}
    }
}

# Validate
from promotions.services.compiler import compile_promotion
result = compile_promotion(promo)
jsonschema.validate(result, schema)
```

---

## 📞 Support

If you encounter issues:
1. Check this quick start guide
2. Review test cases in `test_compiler.py`
3. Check compiler source code comments
4. Run management command for debugging

---

**✅ Compiler is ready to use! Start testing with your promotion data!** 🚀

