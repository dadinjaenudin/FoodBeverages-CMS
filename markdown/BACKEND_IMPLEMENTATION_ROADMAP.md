# Backend Implementation Roadmap
## Promotion System - Complete Backend Development Plan

**Version:** 1.0  
**Date:** 2026-01-27  
**Estimated Duration:** 8-12 weeks  
**Team Size:** 2-3 developers

---
tol
## 📋 Executive Summary

### Current Status
✅ **Database Models** - Complete (12 promotion types, cross-brand support)  
✅ **Basic CRUD Views** - Implemented (Django templates)  
⚠️ **API Layer** - Partial (ReadOnly API exists)  
❌ **Promotion Compiler** - Not implemented  
❌ **Sync API** - Not implemented  
❌ **Validation Engine** - Not implemented  
❌ **Analytics/Reporting** - Not implemented

### What We Need to Build

```
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Promotion Compiler Engine                              │
│     └─> Convert Django models → JSON for POS              │
│                                                             │
│  2. Validation Engine                                       │
│     └─> Business rules validation                          │
│                                                             │
│  3. Sync API (REST)                                         │
│     └─> POS ↔ HO data synchronization                     │
│                                                             │
│  4. Calculation Engine (Python Mirror)                      │
│     └─> Server-side promotion calculation                  │
│                                                             │
│  5. Analytics & Reporting                                   │
│     └─> Dashboard, KPIs, insights                          │
│                                                             │
│  6. Background Jobs (Celery)                                │
│     └─> Async processing, notifications                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗺️ Implementation Phases

### **PHASE 1: Core API & Compiler** (Weeks 1-3)
**Goal:** Enable POS to download promotion rules in JSON format

**Priority:** 🔴 CRITICAL - Blocks POS integration

#### Tasks:

##### 1.1 Promotion Compiler Service
**File:** `promotions/services/compiler.py`

```python
class PromotionCompiler:
    """
    Converts Django Promotion model to Edge-compatible JSON
    """
    
    def compile_promotion(self, promotion: Promotion) -> dict:
        """
        Main compilation method
        Returns: JSON structure for POS consumption
        """
        
    def compile_rules(self, promotion: Promotion) -> dict:
        """
        Compile promotion-specific rules based on type
        Returns: Rules object per promotion type
        """
        
    def compile_scope(self, promotion: Promotion) -> dict:
        """
        Compile apply_to scope (categories, products, exclusions)
        """
        
    def compile_targeting(self, promotion: Promotion) -> dict:
        """
        Compile store selection, brand selection, customer targeting
        """
        
    def compile_time_rules(self, promotion: Promotion) -> dict:
        """
        Compile date range, time range, days of week
        """
```

**JSON Output Example:**
```json
{
  "id": "uuid",
  "code": "WEEKEND20",
  "name": "Weekend Special 20% Off",
  "promo_type": "percent_discount",
  "priority": 10,
  "is_active": true,
  "validity": {
    "start_date": "2026-02-01",
    "end_date": "2026-02-28",
    "time_start": null,
    "time_end": null,
    "days_of_week": [6, 7]
  },
  "scope": {
    "apply_to": "category",
    "categories": ["cat-uuid-1", "cat-uuid-2"],
    "products": [],
    "exclude_categories": [],
    "exclude_products": []
  },
  "rules": {
    "discount_percent": 20.0,
    "max_discount_amount": 50000.0,
    "min_purchase": 0.0
  },
  "stores": ["store-uuid-1", "store-uuid-2"],
  "brands": ["brand-uuid-1"],
  "is_member_only": false,
  "compiled_at": "2026-01-27T10:00:00Z",
  "version": 1
}
```

**Deliverables:**
- ✅ `PromotionCompiler` class with all 12 types
- ✅ Unit tests for each promotion type
- ✅ JSON schema validation
- ✅ Performance optimization (batch compilation)

**Estimated Time:** 1.5 weeks

---

##### 1.2 Sync API Endpoints
**File:** `promotions/api/sync_views.py`

**Endpoints to Create:**

```python
# 1. Get Active Promotions for Store
GET /api/v1/sync/promotions/
Query params:
  - store_id (required)
  - brand_id (optional)
  - last_sync (timestamp, optional)
Response:
  {
    "promotions": [...],
    "deleted_promotion_ids": [...],
    "sync_timestamp": "2026-01-27T10:00:00Z"
  }

# 2. Get Single Promotion (compiled)
GET /api/v1/sync/promotions/{promotion_id}/
Response: Compiled JSON

# 3. Bulk Get Promotions
POST /api/v1/sync/promotions/bulk/
Body: {"promotion_ids": [...]}
Response: {"promotions": [...]}

# 4. Upload Usage Data (from POS)
POST /api/v1/sync/usage/
Body: {
  "usages": [
    {
      "promotion_id": "uuid",
      "bill_id": "uuid",
      "member_id": "uuid",
      "discount_amount": 25000.0,
      "used_at": "2026-01-27T10:00:00Z",
      "store_id": "uuid"
    }
  ]
}
Response: {"created": 10, "errors": []}

# 5. Upload Promotion Logs (from POS)
POST /api/v1/sync/logs/
Body: {
  "logs": [
    {
      "bill_id": "uuid",
      "promotion_id": "uuid",
      "status": "applied",
      "reason": "20% discount applied",
      "discount_amount": 15000.0
    }
  ]
}

# 6. Check Promotion Version
GET /api/v1/sync/version/
Response: {
  "version": 123,
  "last_updated": "2026-01-27T09:00:00Z",
  "force_update": false
}
```

**Deliverables:**
- ✅ All 6 API endpoints
- ✅ Authentication (Token-based for POS)
- ✅ Rate limiting
- ✅ API documentation (Swagger/OpenAPI)
- ✅ Integration tests

**Estimated Time:** 1 week

---

##### 1.3 Validation Engine
**File:** `promotions/services/validator.py`

```python
class PromotionValidator:
    """
    Validates promotion configuration before activation
    """
    
    def validate_promotion(self, promotion: Promotion) -> ValidationResult:
        """
        Main validation entry point
        Returns: ValidationResult with errors/warnings
        """
        
    def validate_dates(self, promotion: Promotion) -> list:
        """Check date range validity"""
        
    def validate_discount_values(self, promotion: Promotion) -> list:
        """Check discount values are within bounds"""
        
    def validate_scope(self, promotion: Promotion) -> list:
        """Check scope configuration is complete"""
        
    def validate_rules(self, promotion: Promotion) -> list:
        """Check type-specific rules are valid"""
        
    def validate_conflicts(self, promotion: Promotion) -> list:
        """Check for conflicts with other promotions"""
```

**Validation Rules:**
- Date: start_date <= end_date
- Discount: 0 <= discount_percent <= 100
- Scope: At least one target (category/product/all)
- BOGO: buy_quantity > 0, get_quantity > 0
- Combo: At least 2 products
- Happy Hour: valid time range
- Cross-brand: trigger_brands != benefit_brands

**Deliverables:**
- ✅ `PromotionValidator` class
- ✅ 50+ validation rules
- ✅ Warning vs Error classification
- ✅ Unit tests

**Estimated Time:** 0.5 weeks

---

### **PHASE 2: Calculation Engine** (Weeks 4-5)
**Goal:** Server-side promotion calculation for preview & validation

**Priority:** 🟡 HIGH - Needed for admin preview

#### Tasks:

##### 2.1 Python Calculation Engine
**File:** `promotions/services/calculator.py`

```python
class PromotionCalculator:
    """
    Server-side promotion calculation engine
    Mirrors JavaScript engine logic
    """
    
    def calculate_promotions(self, cart: dict, promotions: list) -> dict:
        """
        Calculate all applicable promotions
        Returns: Applied promotions with discount amounts
        """
        
    def calculate_percent_discount(self, cart, rules) -> dict:
        """Type 1: Percent Discount"""
        
    def calculate_amount_discount(self, cart, rules) -> dict:
        """Type 2: Amount Discount"""
        
    def calculate_bogo(self, cart, rules) -> dict:
        """Type 3: Buy X Get Y"""
        
    def calculate_combo(self, cart, rules) -> dict:
        """Type 4: Combo Deal"""
        
    def calculate_free_item(self, cart, rules) -> dict:
        """Type 5: Free Item"""
        
    def calculate_happy_hour(self, cart, rules) -> dict:
        """Type 6: Happy Hour"""
        
    def calculate_cashback(self, cart, rules) -> dict:
        """Type 7: Cashback"""
        
    def calculate_payment_discount(self, cart, rules) -> dict:
        """Type 8: Payment Discount"""
        
    def calculate_package(self, cart, rules) -> dict:
        """Type 9: Package/Set Menu"""
        
    def calculate_mix_match(self, cart, rules) -> dict:
        """Type 10: Mix & Match"""
        
    def calculate_upsell(self, cart, rules) -> dict:
        """Type 11: Upsell"""
        
    def calculate_threshold(self, cart, rules) -> dict:
        """Type 12: Threshold/Tiered"""
```

**Use Cases:**
1. Admin preview: "Show me how this promotion works"
2. Validation: "Test promotion with sample cart"
3. Analytics: "Recalculate historical transactions"

**Deliverables:**
- ✅ All 12 calculation methods
- ✅ Stacking logic
- ✅ Priority handling
- ✅ Unit tests with fixtures
- ✅ Performance benchmarks

**Estimated Time:** 1.5 weeks

---

##### 2.2 Preview API
**File:** `promotions/api/preview_views.py`

```python
# Preview Promotion
POST /api/v1/promotions/{id}/preview/
Body: {
  "cart": {
    "items": [
      {
        "product_id": "uuid",
        "quantity": 2,
        "price": 25000.0
      }
    ],
    "subtotal": 50000.0
  },
  "customer": {
    "is_member": true,
    "tier": "gold"
  },
  "payment_method": "card"
}
Response: {
  "applicable": true,
  "discount_amount": 10000.0,
  "final_amount": 40000.0,
  "explanation": "20% discount applied (Rp 10,000 off)",
  "breakdown": {...}
}

# Test Multiple Promotions
POST /api/v1/promotions/preview-multiple/
Body: {
  "promotion_ids": ["uuid1", "uuid2"],
  "cart": {...}
}
Response: {
  "promotions": [
    {
      "id": "uuid1",
      "applied": true,
      "discount": 10000.0,
      "reason": "..."
    }
  ],
  "total_discount": 15000.0,
  "final_amount": 35000.0
}
```

**Deliverables:**
- ✅ Preview API endpoints
- ✅ Frontend integration (AJAX calls)
- ✅ Real-time preview in admin

**Estimated Time:** 0.5 weeks

---

### **PHASE 3: Background Jobs & Automation** (Week 6)
**Goal:** Automated tasks for promotion lifecycle

**Priority:** 🟡 HIGH - Improves operations

#### Tasks:

##### 3.1 Celery Tasks Setup
**File:** `promotions/tasks.py`

```python
# Task 1: Auto-activate promotions
@shared_task
def auto_activate_promotions():
    """
    Run every hour, activate promotions where start_date = today
    """
    
# Task 2: Auto-deactivate promotions
@shared_task
def auto_deactivate_promotions():
    """
    Run every hour, deactivate expired promotions
    """
    
# Task 3: Sync promotion cache to all stores
@shared_task
def sync_promotions_to_stores(promotion_id):
    """
    Push updated promotion to all relevant stores
    """
    
# Task 4: Process cross-brand accumulation
@shared_task
def process_cross_brand_accumulation():
    """
    Check multi-brand spend qualifications
    Issue rewards when thresholds met
    """
    
# Task 5: Generate promotion reports
@shared_task
def generate_daily_promotion_report():
    """
    Daily summary of promotion performance
    """
    
# Task 6: Clean up expired vouchers
@shared_task
def cleanup_expired_vouchers():
    """
    Mark expired vouchers, archive old data
    """
```

**Deliverables:**
- ✅ 6+ Celery tasks
- ✅ Celery beat schedule
- ✅ Task monitoring (Flower)
- ✅ Error handling & retry logic

**Estimated Time:** 1 week

---

### **PHASE 4: Analytics & Reporting** (Weeks 7-8)
**Goal:** Insights and performance tracking

**Priority:** 🟢 MEDIUM - Business intelligence

#### Tasks:

##### 4.1 Analytics Models & Views
**File:** `promotions/analytics.py`

```python
class PromotionAnalytics:
    """
    Promotion performance analytics
    """
    
    def get_promotion_performance(self, promotion_id, date_range):
        """
        Returns:
        - Total usage count
        - Total discount given
        - Revenue impact
        - Redemption rate
        - Top products
        - Top stores
        """
        
    def get_promotion_comparison(self, promotion_ids, date_range):
        """Compare multiple promotions"""
        
    def get_cross_brand_insights(self, date_range):
        """Cross-brand promotion analysis"""
        
    def get_customer_segments(self, promotion_id):
        """Who used this promotion?"""
```

**Dashboard Pages:**
1. **Promotion Overview**
   - Active promotions count
   - Total discounts today/week/month
   - Top performing promotions

2. **Individual Promotion Analytics**
   - Usage timeline chart
   - Discount amount over time
   - Store performance comparison
   - Customer demographics

3. **Cross-Brand Reports**
   - Trigger → Benefit conversion rates
   - Cross-brand customer journey
   - Multi-brand spend tracking

4. **ROI Calculator**
   - Cost of promotion
   - Incremental revenue
   - Customer acquisition cost
   - Lifetime value impact

**Deliverables:**
- ✅ Analytics service class
- ✅ 4+ dashboard pages
- ✅ Charts & visualizations
- ✅ Export to Excel/PDF

**Estimated Time:** 2 weeks

---

### **PHASE 5: Advanced Features** (Weeks 9-10)
**Goal:** Premium capabilities

**Priority:** 🟢 MEDIUM - Nice to have

#### Tasks:

##### 5.1 Voucher Generation System
**File:** `promotions/services/voucher_generator.py`

```python
class VoucherGenerator:
    """
    Generate unique voucher codes
    """
    
    def generate_vouchers(self, promotion, quantity, prefix=""):
        """
        Generate N unique voucher codes
        Format: {PREFIX}-{RANDOM}-{CHECKSUM}
        """
        
    def generate_qr_codes(self, vouchers):
        """Generate QR codes for vouchers"""
        
    def bulk_send_vouchers(self, vouchers, recipients):
        """Send vouchers via SMS/Email"""
```

**Features:**
- ✅ Bulk voucher generation (1000+ codes)
- ✅ QR code generation
- ✅ CSV export
- ✅ SMS/Email distribution
- ✅ Voucher redemption tracking

**Estimated Time:** 1 week

---

##### 5.2 A/B Testing Framework
**File:** `promotions/services/ab_testing.py`

```python
class PromotionABTest:
    """
    A/B testing for promotions
    """
    
    def create_variant(self, base_promotion, variant_config):
        """Create promotion variant for testing"""
        
    def assign_customer_to_variant(self, customer_id, test_id):
        """Assign customer to A or B group"""
        
    def get_test_results(self, test_id):
        """
        Compare variants:
        - Redemption rate
        - Average order value
        - Customer satisfaction
        """
```

**Use Case:**
- Test 10% vs 15% discount
- Test different messaging
- Test time restrictions

**Estimated Time:** 1 week

---

### **PHASE 6: Polish & Optimization** (Weeks 11-12)
**Goal:** Production readiness

**Priority:** 🔴 CRITICAL - Must have before launch

#### Tasks:

##### 6.1 Performance Optimization
- ✅ Database query optimization
- ✅ Caching strategy (Redis)
- ✅ Batch operations
- ✅ Async where possible
- ✅ Load testing (1000+ concurrent users)

##### 6.2 Error Handling
- ✅ Comprehensive error messages
- ✅ Graceful degradation
- ✅ Rollback mechanisms
- ✅ Monitoring & alerting

##### 6.3 Documentation
- ✅ API documentation (Swagger)
- ✅ Developer guide
- ✅ Deployment guide
- ✅ Troubleshooting guide

##### 6.4 Testing
- ✅ Unit tests (90%+ coverage)
- ✅ Integration tests
- ✅ End-to-end tests
- ✅ Load tests
- ✅ Security tests

**Estimated Time:** 2 weeks

---


## ?? File Structure & Organization

### New Files to Create

```
promotions/
+-- services/
�   +-- __init__.py
�   +-- compiler.py              # ? PHASE 1 - Promotion to JSON compiler
�   +-- validator.py             # ? PHASE 1 - Validation engine
�   +-- calculator.py            # ? PHASE 2 - Server-side calculation
�   +-- voucher_generator.py    # ? PHASE 5 - Voucher generation
�   +-- ab_testing.py            # ? PHASE 5 - A/B testing
�   +-- analytics.py             # ? PHASE 4 - Analytics service
�
+-- api/
�   +-- sync_views.py            # ? PHASE 1 - Sync API endpoints
�   +-- preview_views.py         # ? PHASE 2 - Preview API
�   +-- analytics_views.py       # ? PHASE 4 - Analytics API
�   +-- sync_urls.py             # ? URL routing for sync
�
+-- tasks.py                     # ? PHASE 3 - Celery tasks
+-- analytics.py                 # ? PHASE 4 - Analytics logic
+-- tests/
�   +-- test_compiler.py
�   +-- test_validator.py
�   +-- test_calculator.py
�   +-- test_sync_api.py
�   +-- fixtures/
�       +-- sample_promotions.json
�       +-- sample_carts.json
�
+-- management/
    +-- commands/
        +-- compile_all_promotions.py
        +-- sync_promotions.py
        +-- test_promotion_calculation.py
```

---

## ?? Technical Stack

### Backend Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | Django 4.2+ | Web framework |
| **API** | Django REST Framework | REST API |
| **Task Queue** | Celery + Redis | Background jobs |
| **Database** | PostgreSQL | Primary database |
| **Cache** | Redis | Caching layer |
| **Message Broker** | Redis / RabbitMQ | Celery broker |
| **Documentation** | drf-spectacular | OpenAPI/Swagger |
| **Testing** | pytest | Test framework |
| **Monitoring** | Sentry | Error tracking |

---

## ?? Detailed Implementation Guide

### PHASE 1 DEEP DIVE: Promotion Compiler

#### Step 1: Install Dependencies

```bash
pip install djangorestframework
pip install drf-spectacular  # For API docs
pip install django-filter    # For API filtering
pip install celery redis     # For background tasks
```

#### Step 2: Create Compiler Service

**File:** `promotions/services/compiler.py`

```python
"""
Promotion Compiler Service
Converts Django Promotion models to Edge-compatible JSON
"""

from typing import Dict, List, Optional
from django.db.models import Q
from promotions.models import Promotion, PromotionTier, PackagePromotion
from products.models import Product, Category
import logging

logger = logging.getLogger(__name__)


class PromotionCompiler:
    """
    Main compiler class - converts Promotion model to JSON
    """
    
    def __init__(self):
        self.version = "1.0"
    
    def compile_promotion(self, promotion: Promotion) -> Dict:
        """
        Main entry point - compile single promotion
        
        Args:
            promotion: Promotion model instance
            
        Returns:
            Dict: JSON-serializable promotion data
        """
        if not promotion.is_active:
            logger.warning(f"Compiling inactive promotion: {promotion.code}")
        
        compiled = {
            "id": str(promotion.id),
            "code": promotion.code,
            "name": promotion.name,
            "description": promotion.description,
            "promo_type": promotion.promo_type,
            "apply_to": promotion.apply_to,
            "execution_stage": promotion.execution_stage,
            "execution_priority": promotion.execution_priority,
            "is_active": promotion.is_active,
            "is_auto_apply": promotion.is_auto_apply,
            "require_voucher": promotion.require_voucher,
            "member_only": promotion.member_only,
            
            # Compiled sections
            "validity": self.compile_time_rules(promotion),
            "scope": self.compile_scope(promotion),
            "targeting": self.compile_targeting(promotion),
            "rules": self.compile_rules(promotion),
            "limits": self.compile_limits(promotion),
            
            # Metadata
            "compiled_at": timezone.now().isoformat(),
            "compiler_version": self.version,
        }
        
        # Cross-brand handling
        if promotion.is_cross_brand:
            compiled["cross_brand"] = self.compile_cross_brand(promotion)
        
        return compiled
    
    def compile_time_rules(self, promotion: Promotion) -> Dict:
        """
        Compile validity time rules
        """
        return {
            "start_date": promotion.start_date.isoformat(),
            "end_date": promotion.end_date.isoformat(),
            "time_start": promotion.valid_time_start.isoformat() if promotion.valid_time_start else None,
            "time_end": promotion.valid_time_end.isoformat() if promotion.valid_time_end else None,
            "days_of_week": promotion.valid_days,
            "exclude_holidays": promotion.exclude_holidays,
        }
    
    def compile_scope(self, promotion: Promotion) -> Dict:
        """
        Compile product/category scope
        """
        scope = {
            "apply_to": promotion.apply_to,
        }
        
        # Categories
        if promotion.apply_to == 'category':
            scope["categories"] = list(
                promotion.categories.values_list('id', flat=True)
            )
            scope["exclude_categories"] = list(
                promotion.exclude_categories.values_list('id', flat=True)
            )
        
        # Products
        if promotion.apply_to == 'product':
            scope["products"] = list(
                promotion.products.values_list('id', flat=True)
            )
            scope["exclude_products"] = list(
                promotion.exclude_products.values_list('id', flat=True)
            )
        
        # For 'all' - still need exclusions
        if promotion.apply_to == 'all':
            scope["exclude_categories"] = list(
                promotion.exclude_categories.values_list('id', flat=True)
            )
            scope["exclude_products"] = list(
                promotion.exclude_products.values_list('id', flat=True)
            )
        
        return scope
    
    def compile_targeting(self, promotion: Promotion) -> Dict:
        """
        Compile store/brand/customer targeting
        """
        targeting = {}
        
        # Store targeting
        if promotion.all_stores:
            targeting["stores"] = "all"
        else:
            targeting["stores"] = list(
                promotion.stores.values_list('id', flat=True)
            )
        
        # Brand targeting
        if promotion.scope == 'company':
            targeting["brands"] = "all"
        elif promotion.scope == 'brands':
            targeting["brands"] = list(
                promotion.brands.values_list('id', flat=True)
            )
        elif promotion.scope == 'single' and promotion.brand:
            targeting["brands"] = [str(promotion.brand.id)]
        
        # Exclude brands
        if promotion.exclude_brands.exists():
            targeting["exclude_brands"] = list(
                promotion.exclude_brands.values_list('id', flat=True)
            )
        
        # Customer targeting
        targeting["member_only"] = promotion.member_only
        if promotion.member_tiers:
            targeting["member_tiers"] = promotion.member_tiers
        
        # Customer type
        targeting["customer_type"] = promotion.customer_type
        
        # Sales channels
        if promotion.sales_channels:
            targeting["sales_channels"] = promotion.sales_channels
        if promotion.exclude_channels:
            targeting["exclude_channels"] = promotion.exclude_channels
        
        return targeting
    
    def compile_rules(self, promotion: Promotion) -> Dict:
        """
        Compile type-specific rules
        Routes to appropriate compiler based on promo_type
        """
        compiler_map = {
            'percent_discount': self._compile_percent_discount,
            'amount_discount': self._compile_amount_discount,
            'buy_x_get_y': self._compile_bogo,
            'combo': self._compile_combo,
            'free_item': self._compile_free_item,
            'happy_hour': self._compile_happy_hour,
            'cashback': self._compile_cashback,
            'payment_discount': self._compile_payment_discount,
            'package': self._compile_package,
            'mix_match': self._compile_mix_match,
            'upsell': self._compile_upsell,
            'threshold_tier': self._compile_threshold,
        }
        
        compiler_func = compiler_map.get(promotion.promo_type)
        if not compiler_func:
            logger.error(f"No compiler for promo_type: {promotion.promo_type}")
            return {}
        
        return compiler_func(promotion)
    
    def _compile_percent_discount(self, promotion: Promotion) -> Dict:
        """Type 1: Percent Discount"""
        return {
            "type": "percent",
            "discount_percent": float(promotion.discount_percent),
            "max_discount_amount": float(promotion.max_discount_amount) if promotion.max_discount_amount else None,
            "min_purchase": float(promotion.min_purchase),
        }
    
    def _compile_amount_discount(self, promotion: Promotion) -> Dict:
        """Type 2: Amount Discount"""
        return {
            "type": "amount",
            "discount_amount": float(promotion.discount_amount),
            "min_purchase": float(promotion.min_purchase),
        }
    
    def _compile_bogo(self, promotion: Promotion) -> Dict:
        """Type 3: Buy X Get Y"""
        rules = {
            "type": "bogo",
            "buy_quantity": promotion.buy_quantity,
            "get_quantity": promotion.get_quantity,
            "get_discount_percent": float(promotion.discount_percent) if promotion.discount_percent else 100.0,
        }
        
        # If specific get_product is defined
        if promotion.get_product:
            rules["get_product_id"] = str(promotion.get_product.id)
            rules["same_product_only"] = False
        else:
            rules["same_product_only"] = True
        
        return rules
    
    def _compile_combo(self, promotion: Promotion) -> Dict:
        """Type 4: Combo Deal"""
        combo_products = list(
            promotion.combo_products.values('id', 'name', 'price')
        )
        
        return {
            "type": "combo",
            "combo_price": float(promotion.combo_price),
            "products": [
                {
                    "product_id": str(p['id']),
                    "quantity": 1,  # Default, can be enhanced
                }
                for p in combo_products
            ],
            "all_required": True,
        }
    
    def _compile_free_item(self, promotion: Promotion) -> Dict:
        """Type 5: Free Item"""
        # Use BOGO fields for free item logic
        rules = {
            "type": "free_item",
            "min_purchase": float(promotion.min_purchase),
        }
        
        if promotion.required_product:
            rules["trigger_product_id"] = str(promotion.required_product.id)
            rules["trigger_min_qty"] = promotion.buy_quantity or 1
        
        if promotion.get_product:
            rules["free_product_id"] = str(promotion.get_product.id)
            rules["free_quantity"] = promotion.get_quantity or 1
        
        return rules
    
    def _compile_happy_hour(self, promotion: Promotion) -> Dict:
        """Type 6: Happy Hour"""
        return {
            "type": "happy_hour",
            "discount_percent": float(promotion.discount_percent) if promotion.discount_percent else None,
            "discount_amount": float(promotion.discount_amount) if promotion.discount_amount else None,
            "special_price": float(promotion.happy_hour_price) if promotion.happy_hour_price else None,
            "time_start": promotion.valid_time_start.isoformat() if promotion.valid_time_start else None,
            "time_end": promotion.valid_time_end.isoformat() if promotion.valid_time_end else None,
            "days_of_week": promotion.valid_days,
        }
    
    def _compile_cashback(self, promotion: Promotion) -> Dict:
        """Type 7: Cashback"""
        return {
            "type": "cashback",
            "cashback_type": "percent" if promotion.discount_percent else "amount",
            "cashback_value": float(promotion.discount_percent or promotion.discount_amount),
            "cashback_max": float(promotion.max_discount_amount) if promotion.max_discount_amount else None,
            "min_purchase": float(promotion.min_purchase),
            "payment_methods": promotion.payment_methods,
            "cashback_method": "points",  # Default
        }
    
    def _compile_payment_discount(self, promotion: Promotion) -> Dict:
        """Type 8: Payment Method Discount"""
        return {
            "type": "payment_discount",
            "payment_methods": promotion.payment_methods,
            "discount_type": "percent" if promotion.discount_percent else "amount",
            "discount_value": float(promotion.discount_percent or promotion.discount_amount),
            "max_discount": float(promotion.max_discount_amount) if promotion.max_discount_amount else None,
            "min_purchase": float(promotion.payment_min_amount),
        }
    
    def _compile_package(self, promotion: Promotion) -> Dict:
        """Type 9: Package/Set Menu"""
        try:
            package = promotion.package
            items = []
            
            for item in package.items.all():
                item_data = {
                    "item_type": item.item_type,
                    "quantity": float(item.quantity),
                    "is_required": item.is_required,
                }
                
                if item.product:
                    item_data["product_id"] = str(item.product.id)
                elif item.category:
                    item_data["category_id"] = str(item.category.id)
                    item_data["min_selection"] = item.min_selection
                    item_data["max_selection"] = item.max_selection
                
                items.append(item_data)
            
            return {
                "type": "package",
                "package_name": package.package_name,
                "package_price": float(package.package_price),
                "items": items,
                "allow_modification": package.allow_modification,
            }
        except PackagePromotion.DoesNotExist:
            logger.error(f"Package promotion {promotion.id} missing package details")
            return {"type": "package", "error": "Package details not configured"}
    
    def _compile_mix_match(self, promotion: Promotion) -> Dict:
        """Type 10: Mix & Match"""
        rules = promotion.mix_match_rules or {}
        
        return {
            "type": "mix_match",
            "category_id": rules.get('category_id'),
            "required_quantity": rules.get('required_quantity', 3),
            "special_price": rules.get('special_price', 0),
            "allow_same_product": rules.get('allow_same_product', True),
        }
    
    def _compile_upsell(self, promotion: Promotion) -> Dict:
        """Type 11: Upsell/Add-on"""
        rules = {
            "type": "upsell",
            "upsell_message": promotion.upsell_message,
        }
        
        if promotion.required_product:
            rules["required_product_id"] = str(promotion.required_product.id)
            rules["required_min_qty"] = promotion.buy_quantity or 1
        
        if promotion.upsell_product:
            rules["upsell_product_id"] = str(promotion.upsell_product.id)
            rules["special_price"] = float(promotion.upsell_special_price)
        
        return rules
    
    def _compile_threshold(self, promotion: Promotion) -> Dict:
        """Type 12: Threshold/Tiered"""
        tiers = []
        
        for tier in promotion.tiers.filter(is_active=True).order_by('tier_order'):
            tier_data = {
                "tier_name": tier.tier_name,
                "min_amount": float(tier.min_amount),
                "max_amount": float(tier.max_amount) if tier.max_amount else None,
                "discount_type": tier.discount_type,
                "discount_value": float(tier.discount_value),
            }
            
            if tier.free_product:
                tier_data["free_product_id"] = str(tier.free_product.id)
            
            if tier.discount_type == 'points_multiplier':
                tier_data["points_multiplier"] = float(tier.points_multiplier)
            
            tiers.append(tier_data)
        
        return {
            "type": "threshold_tier",
            "tiers": tiers,
        }
    
    def compile_limits(self, promotion: Promotion) -> Dict:
        """
        Compile usage limits
        """
        return {
            "max_uses": promotion.max_uses,
            "max_uses_per_customer": promotion.max_uses_per_customer,
            "max_uses_per_day": promotion.max_uses_per_day,
            "current_uses": promotion.current_uses,
        }
    
    def compile_cross_brand(self, promotion: Promotion) -> Dict:
        """
        Compile cross-brand specific rules
        """
        cross_brand = {
            "enabled": True,
            "type": promotion.cross_brand_type,
        }
        
        if promotion.cross_brand_type == 'trigger_benefit':
            cross_brand["trigger_brands"] = list(
                promotion.trigger_brands.values_list('id', flat=True)
            )
            cross_brand["trigger_min_amount"] = float(promotion.trigger_min_amount or 0)
            cross_brand["benefit_brands"] = list(
                promotion.benefit_brands.values_list('id', flat=True)
            )
        
        # Add custom rules from JSON field
        if promotion.cross_brand_rules:
            cross_brand["rules"] = promotion.cross_brand_rules
        
        return cross_brand
    
    def compile_multiple(self, promotions: List[Promotion]) -> List[Dict]:
        """
        Compile multiple promotions (batch operation)
        """
        compiled = []
        for promotion in promotions:
            try:
                compiled.append(self.compile_promotion(promotion))
            except Exception as e:
                logger.error(f"Error compiling promotion {promotion.id}: {str(e)}")
                continue
        
        return compiled
    
    def compile_for_store(self, store_id: str) -> List[Dict]:
        """
        Compile all active promotions for a specific store
        
        Args:
            store_id: Store UUID
            
        Returns:
            List of compiled promotions applicable to this store
        """
        from core.models import Store
        
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            logger.error(f"Store {store_id} not found")
            return []
        
        # Get promotions applicable to this store
        now = timezone.now()
        promotions = Promotion.objects.filter(
            Q(all_stores=True) | Q(stores=store),
            is_active=True,
            start_date__lte=now.date(),
            end_date__gte=now.date(),
            company=store.company
        ).distinct()
        
        # Filter by brand
        if store.brand:
            promotions = promotions.filter(
                Q(scope='company') |
                Q(scope='brands', brands=store.brand) |
                Q(scope='single', brand=store.brand)
            )
        
        return self.compile_multiple(promotions)


# Utility function for easy access
def compile_promotion(promotion: Promotion) -> Dict:
    """Convenience function"""
    compiler = PromotionCompiler()
    return compiler.compile_promotion(promotion)
```

This is getting long! Should I:
1. Continue with the remaining implementation details in the roadmap?
2. Create separate implementation files for each phase?
3. Focus on a specific phase you want to start with?

What would you like me to prioritize next? ??


---

## ?? Implementation Priority Matrix

### Critical Path (Must Have for MVP)

| Priority | Component | Reason | Dependency |
|----------|-----------|--------|------------|
| ?? P0 | Promotion Compiler | POS needs JSON rules | None |
| ?? P0 | Sync API (GET) | POS must download promotions | Compiler |
| ?? P0 | Validation Engine | Prevent invalid configs | None |
| ?? P1 | Sync API (POST) | Track usage data | None |
| ?? P1 | Calculation Engine | Admin preview needed | Compiler |
| ?? P1 | Auto-activation Task | Operational efficiency | None |
| ?? P2 | Analytics Dashboard | Business insights | Usage data |
| ?? P2 | Voucher Generation | Advanced feature | None |
| ?? P3 | A/B Testing | Optimization | Analytics |

---

## ? Quick Start Implementation (Week 1)

### Day 1-2: Project Setup

```bash
# 1. Create new branches
git checkout -b feature/promotion-compiler
git checkout -b feature/promotion-sync-api

# 2. Install dependencies
pip install djangorestframework==3.14.0
pip install drf-spectacular==0.26.5
pip install django-filter==23.3
pip install celery==5.3.4
pip install redis==5.0.1

# 3. Update settings.py
```

**Add to `config/settings.py`:**

```python
INSTALLED_APPS = [
    # ... existing apps
    'rest_framework',
    'drf_spectacular',
    'django_filters',
]

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

SPECTACULAR_SETTINGS = {
    'TITLE': 'F&B Promotion API',
    'DESCRIPTION': 'Promotion System Sync API for POS Devices',
    'VERSION': '1.0.0',
}

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Jakarta'
```

---

### Day 3-4: Implement Compiler

Create the compiler service (code provided above in `promotions/services/compiler.py`)

**Test the compiler:**

```python
# promotions/tests/test_compiler.py
import pytest
from decimal import Decimal
from promotions.models import Promotion
from promotions.services.compiler import PromotionCompiler

@pytest.mark.django_db
class TestPromotionCompiler:
    
    def test_compile_percent_discount(self, sample_promotion):
        """Test percent discount compilation"""
        promotion = Promotion.objects.create(
            company=sample_promotion.company,
            name="Test 20% Off",
            code="TEST20",
            promo_type="percent_discount",
            discount_percent=Decimal('20.00'),
            max_discount_amount=Decimal('50000.00'),
            start_date='2026-01-01',
            end_date='2026-12-31',
            created_by=sample_promotion.created_by
        )
        
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(promotion)
        
        assert result['code'] == 'TEST20'
        assert result['promo_type'] == 'percent_discount'
        assert result['rules']['discount_percent'] == 20.0
        assert result['rules']['max_discount_amount'] == 50000.0
    
    def test_compile_bogo(self, sample_promotion):
        """Test BOGO compilation"""
        promotion = Promotion.objects.create(
            company=sample_promotion.company,
            name="Buy 2 Get 1",
            code="BOGO21",
            promo_type="buy_x_get_y",
            buy_quantity=2,
            get_quantity=1,
            discount_percent=Decimal('100.00'),
            start_date='2026-01-01',
            end_date='2026-12-31',
            created_by=sample_promotion.created_by
        )
        
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(promotion)
        
        assert result['rules']['buy_quantity'] == 2
        assert result['rules']['get_quantity'] == 1
        assert result['rules']['same_product_only'] == True

# Run tests
pytest promotions/tests/test_compiler.py -v
```

---

### Day 5: Create Sync API

**File:** `promotions/api/sync_views.py`

```python
"""
Sync API for POS Devices
Allows POS to download promotion rules and upload usage data
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from promotions.models import Promotion, PromotionUsage, PromotionLog
from promotions.services.compiler import PromotionCompiler
from promotions.api.serializers import (
    PromotionUsageSerializer,
    PromotionLogSerializer
)
import logging

logger = logging.getLogger(__name__)


class PromotionSyncViewSet(viewsets.ViewSet):
    """
    Promotion Sync API for POS Devices
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def active_promotions(self, request):
        """
        GET /api/v1/sync/promotions/active/
        
        Query Parameters:
        - store_id (required): UUID of the store
        - brand_id (optional): Filter by brand
        - last_sync (optional): ISO timestamp of last sync
        
        Returns:
        - promotions: List of compiled promotion JSON
        - deleted_ids: List of promotion IDs that were deleted
        - sync_timestamp: Current server timestamp
        """
        store_id = request.query_params.get('store_id')
        if not store_id:
            return Response(
                {"error": "store_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        brand_id = request.query_params.get('brand_id')
        last_sync = request.query_params.get('last_sync')
        
        try:
            compiler = PromotionCompiler()
            promotions = compiler.compile_for_store(store_id)
            
            # Get deleted promotions since last sync
            deleted_ids = []
            if last_sync:
                # TODO: Track deleted promotions
                pass
            
            return Response({
                "promotions": promotions,
                "deleted_ids": deleted_ids,
                "sync_timestamp": timezone.now().isoformat(),
                "count": len(promotions)
            })
        
        except Exception as e:
            logger.error(f"Error syncing promotions for store {store_id}: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def get_promotion(self, request, pk=None):
        """
        GET /api/v1/sync/promotions/{id}/
        
        Returns single compiled promotion
        """
        try:
            promotion = Promotion.objects.get(id=pk)
            compiler = PromotionCompiler()
            compiled = compiler.compile_promotion(promotion)
            
            return Response(compiled)
        
        except Promotion.DoesNotExist:
            return Response(
                {"error": "Promotion not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def bulk_get(self, request):
        """
        POST /api/v1/sync/promotions/bulk/
        
        Body: {
            "promotion_ids": ["uuid1", "uuid2", ...]
        }
        
        Returns list of compiled promotions
        """
        promotion_ids = request.data.get('promotion_ids', [])
        
        if not promotion_ids:
            return Response(
                {"error": "promotion_ids is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        promotions = Promotion.objects.filter(id__in=promotion_ids)
        compiler = PromotionCompiler()
        compiled = compiler.compile_multiple(promotions)
        
        return Response({
            "promotions": compiled,
            "count": len(compiled)
        })
    
    @action(detail=False, methods=['post'])
    def upload_usage(self, request):
        """
        POST /api/v1/sync/promotions/upload-usage/
        
        Body: {
            "usages": [
                {
                    "promotion_id": "uuid",
                    "bill_id": "uuid",
                    "member_id": "uuid" (optional),
                    "customer_phone": "string" (optional),
                    "discount_amount": 25000.0,
                    "used_at": "2026-01-27T10:00:00Z",
                    "store_id": "uuid",
                    "brand_id": "uuid"
                }
            ]
        }
        """
        usages = request.data.get('usages', [])
        
        if not usages:
            return Response(
                {"error": "usages array is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created = 0
        errors = []
        
        for usage_data in usages:
            try:
                serializer = PromotionUsageSerializer(data=usage_data)
                if serializer.is_valid():
                    serializer.save()
                    created += 1
                    
                    # Update promotion current_uses counter
                    promotion = Promotion.objects.get(id=usage_data['promotion_id'])
                    promotion.current_uses += 1
                    promotion.save(update_fields=['current_uses'])
                else:
                    errors.append({
                        "data": usage_data,
                        "errors": serializer.errors
                    })
            except Exception as e:
                errors.append({
                    "data": usage_data,
                    "error": str(e)
                })
        
        return Response({
            "created": created,
            "errors": errors,
            "total": len(usages)
        })
    
    @action(detail=False, methods=['post'])
    def upload_logs(self, request):
        """
        POST /api/v1/sync/promotions/upload-logs/
        
        Body: {
            "logs": [
                {
                    "bill_id": "uuid",
                    "promotion_id": "uuid",
                    "status": "applied",
                    "reason": "20% discount applied",
                    "discount_amount": 15000.0,
                    "original_amount": 75000.0,
                    "final_amount": 60000.0
                }
            ]
        }
        """
        logs = request.data.get('logs', [])
        
        if not logs:
            return Response(
                {"error": "logs array is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created = 0
        errors = []
        
        for log_data in logs:
            try:
                serializer = PromotionLogSerializer(data=log_data)
                if serializer.is_valid():
                    serializer.save()
                    created += 1
                else:
                    errors.append({
                        "data": log_data,
                        "errors": serializer.errors
                    })
            except Exception as e:
                errors.append({
                    "data": log_data,
                    "error": str(e)
                })
        
        return Response({
            "created": created,
            "errors": errors,
            "total": len(logs)
        })
    
    @action(detail=False, methods=['get'])
    def version(self, request):
        """
        GET /api/v1/sync/promotions/version/
        
        Returns current promotion data version
        Helps POS decide if full sync is needed
        """
        # Get latest promotion update timestamp
        latest_promo = Promotion.objects.order_by('-updated_at').first()
        
        if latest_promo:
            last_updated = latest_promo.updated_at
            version = int(last_updated.timestamp())
        else:
            last_updated = timezone.now()
            version = 0
        
        return Response({
            "version": version,
            "last_updated": last_updated.isoformat(),
            "force_update": False  # Can be controlled via admin
        })
```

**Create Serializers:**

**File:** `promotions/api/serializers.py` (update existing)

```python
from rest_framework import serializers
from promotions.models import PromotionUsage, PromotionLog

class PromotionUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionUsage
        fields = [
            'promotion', 'member', 'customer_phone', 'bill_id',
            'brand', 'discount_amount', 'used_at'
        ]

class PromotionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionLog
        fields = [
            'bill_id', 'promotion', 'status', 'reason',
            'validation_details', 'original_amount',
            'discount_amount', 'final_amount'
        ]
```

**Create URL Routes:**

**File:** `promotions/api/sync_urls.py`

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from promotions.api.sync_views import PromotionSyncViewSet

router = DefaultRouter()
router.register(r'promotions', PromotionSyncViewSet, basename='promotion-sync')

urlpatterns = [
    path('', include(router.urls)),
]
```

**Update main URLs:**

**File:** `config/urls.py` (add)

```python
urlpatterns = [
    # ... existing patterns
    path('api/v1/sync/', include('promotions.api.sync_urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

---

## ?? Testing Strategy

### Unit Tests
```bash
# Test compiler
pytest promotions/tests/test_compiler.py -v

# Test API endpoints
pytest promotions/tests/test_sync_api.py -v

# Test validators
pytest promotions/tests/test_validator.py -v

# Coverage report
pytest --cov=promotions --cov-report=html
```

### Integration Tests
```python
# Test full flow: Create ? Compile ? Sync
# promotions/tests/test_integration.py

@pytest.mark.django_db
def test_promotion_lifecycle():
    # 1. Create promotion
    promotion = create_test_promotion()
    
    # 2. Compile
    compiler = PromotionCompiler()
    compiled = compiler.compile_promotion(promotion)
    
    # 3. Sync to POS
    client = APIClient()
    response = client.get(f'/api/v1/sync/promotions/{promotion.id}/')
    
    assert response.status_code == 200
    assert response.json()['code'] == promotion.code
```

### Load Testing
```python
# Use locust for load testing
# locustfile.py

from locust import HttpUser, task, between

class POSDevice(HttpUser):
    wait_time = between(5, 15)
    
    @task
    def sync_promotions(self):
        self.client.get(
            "/api/v1/sync/promotions/active/",
            params={"store_id": "test-store-uuid"}
        )
```

---

## ?? Success Metrics

### Phase 1 Completion Criteria
- ? Compiler handles all 12 promotion types
- ? Sync API endpoints functional
- ? Unit test coverage > 80%
- ? API documentation complete
- ? Performance: Compile < 100ms per promotion
- ? Performance: Sync API < 500ms for 100 promotions

### Phase 2 Completion Criteria
- ? Calculator matches JavaScript engine output
- ? Preview API working in admin
- ? Test coverage > 85%

### Phase 3 Completion Criteria
- ? 6+ Celery tasks running
- ? Auto-activation/deactivation working
- ? Task monitoring dashboard setup

---

## ?? Deployment Checklist

### Before Going Live
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Load tests completed
- [ ] API documentation published
- [ ] Celery workers running
- [ ] Redis configured
- [ ] Monitoring setup (Sentry)
- [ ] Backup strategy in place
- [ ] Rollback plan documented
- [ ] Staff training completed

### Environment Variables
```bash
# .env.production
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# API Rate Limiting
API_THROTTLE_RATE=100/hour
POS_API_THROTTLE_RATE=1000/hour

# Monitoring
SENTRY_DSN=https://...
```

---

## ?? Support & Escalation

### Development Team
- **Lead Developer:** [Name]
- **Backend:** [Name]
- **DevOps:** [Name]

### Issue Escalation
1. **P0 (Critical):** System down, data loss
   - Response: 15 minutes
   - Resolution: 2 hours

2. **P1 (High):** Major feature broken
   - Response: 1 hour
   - Resolution: 4 hours

3. **P2 (Medium):** Minor issues
   - Response: 4 hours
   - Resolution: 1 day

4. **P3 (Low):** Enhancements
   - Response: 1 day
   - Resolution: 1 week

---

## ?? Summary

This roadmap provides a complete implementation plan for the Promotion System backend:

### Total Effort Estimate
- **Duration:** 8-12 weeks
- **Team Size:** 2-3 developers
- **Phases:** 6 major phases
- **Components:** 15+ new files/services
- **Tests:** 100+ test cases

### Key Deliverables
1. ? Promotion Compiler (JSON generation)
2. ? Sync API (6 endpoints)
3. ? Validation Engine
4. ? Calculation Engine (12 types)
5. ? Background Jobs (Celery)
6. ? Analytics Dashboard
7. ? API Documentation
8. ? Testing Suite

### Next Steps
1. **Week 1:** Setup + Compiler implementation
2. **Week 2:** Sync API + Testing
3. **Week 3:** Validation + Polish Phase 1
4. **Week 4-5:** Calculation Engine
5. **Week 6:** Background Jobs
6. **Week 7-8:** Analytics
7. **Week 9-10:** Advanced Features
8. **Week 11-12:** Polish & Deploy

---

*Roadmap Version: 1.0*  
*Last Updated: 2026-01-27*  
*Status: Ready for Implementation*

**Ready to start coding! Which phase would you like to begin with?** ??

