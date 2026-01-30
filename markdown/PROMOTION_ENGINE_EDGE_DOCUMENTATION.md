# Promotion Engine - Edge/POS Implementation Guide
**Version:** 2.0  
**Date:** 2026-01-27  
**Target:** Offline-first POS System (Separate Database & Application)
**Updated:** Added all 12 promotion types from models.py

---

## 📋 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Database Schema (POS Edge)](#database-schema-pos-edge)
3. [Sync Process](#sync-process)
4. [Promotion Evaluation Engine](#promotion-evaluation-engine)
5. [Calculation Logic per Promotion Type](#calculation-logic-per-promotion-type)
6. [Code Examples](#code-examples)
7. [Performance Optimization](#performance-optimization)
8. [Error Handling](#error-handling)
9. [Testing Scenarios](#testing-scenarios)

---

## 🏗️ Architecture Overview

### **System Separation**

```
┌──────────────────────────────────────────────────────────────┐
│                    HEAD OFFICE (HO)                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Django CMS                                            │  │
│  │  - Database: PostgreSQL (Complex Schema)              │  │
│  │  - 7 Tables: Promotion, PackagePromotion, etc         │  │
│  │  - Compiler: Converts to flat JSON                    │  │
│  │  - API: Provides compiled promotions                  │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS/REST API
                              │ Sync Every 1 Hour
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    EDGE/STORE POS                             │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  POS Application (Electron/Desktop)                    │  │
│  │  - Database: SQLite/PostgreSQL (Simple Schema)        │  │
│  │  - 1 Main Table: promotion_cache                      │  │
│  │  - Engine: Evaluates promotions offline               │  │
│  │  - Fast: < 100ms per bill evaluation                  │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### **Key Principles**

1. **Offline-First**: POS must work without internet
2. **Fast Evaluation**: < 100ms for promotion calculation
3. **Deterministic**: Same input → Same output
4. **Explainable**: Log why promo applied/skipped
5. **Safe**: Never over-discount

---

## 💾 Database Schema (POS Edge)

### **Main Table: `promotion_cache`**

```sql
CREATE TABLE promotion_cache (
    -- Identity
    id TEXT PRIMARY KEY,                    -- UUID from HO
    code TEXT UNIQUE NOT NULL,              -- Promo code
    name TEXT NOT NULL,                     -- Display name
    description TEXT,                       -- For UI display
    
    -- Type & Stage
    promo_type TEXT NOT NULL,               -- 'percent_discount', 'buy_x_get_y', etc
    execution_stage TEXT NOT NULL,          -- 'item_level', 'subtotal', 'payment', etc
    
    -- Compiled Rules (ALL RULES IN ONE JSON)
    promotion_data TEXT NOT NULL,           -- JSON string with all rules
    
    -- Quick Filters (for fast pre-screening)
    valid_from DATE NOT NULL,
    valid_until DATE NOT NULL,
    valid_days TEXT,                        -- JSON: [0,1,2,3,4,5,6]
    valid_hours_start TIME,
    valid_hours_end TIME,
    
    -- Scope
    store_id TEXT NOT NULL,
    
    -- Flags (for quick checks)
    is_active INTEGER DEFAULT 1,            -- Boolean
    is_member_only INTEGER DEFAULT 0,
    require_voucher INTEGER DEFAULT 0,
    is_auto_apply INTEGER DEFAULT 1,
    
    -- Execution Priority
    priority INTEGER DEFAULT 0,             -- Higher = execute first
    execution_priority INTEGER DEFAULT 500, -- 1-999, lower = execute first
    
    -- Stacking
    is_stackable INTEGER DEFAULT 0,
    cannot_combine_with TEXT,               -- JSON: ["promo_id_1", "promo_id_2"]
    
    -- Sync Metadata
    version INTEGER NOT NULL,
    synced_at TIMESTAMP NOT NULL,
    checksum TEXT NOT NULL,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Performance
CREATE INDEX idx_promo_active ON promotion_cache(is_active, valid_from, valid_until);
CREATE INDEX idx_promo_priority ON promotion_cache(priority DESC, execution_priority ASC);
CREATE INDEX idx_promo_type ON promotion_cache(promo_type);
CREATE INDEX idx_promo_store ON promotion_cache(store_id, is_active);
CREATE INDEX idx_promo_sync ON promotion_cache(version);
```

### **Logging Table: `promotion_log_local`**

```sql
CREATE TABLE promotion_log_local (
    id TEXT PRIMARY KEY,
    bill_id TEXT NOT NULL,
    promotion_id TEXT NOT NULL,
    promotion_code TEXT NOT NULL,
    
    -- Result
    status TEXT NOT NULL,                   -- 'applied', 'skipped', 'failed'
    reason TEXT,                            -- Why applied/skipped
    
    -- Amounts
    original_amount REAL DEFAULT 0,
    discount_amount REAL DEFAULT 0,
    final_amount REAL DEFAULT 0,
    
    -- Details
    validation_details TEXT,                -- JSON with condition checks
    affected_items TEXT,                    -- JSON: item IDs affected
    
    -- Audit
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    synced_to_ho INTEGER DEFAULT 0,         -- Boolean: sent to HO?
    
    FOREIGN KEY (bill_id) REFERENCES bill(id)
);

CREATE INDEX idx_promo_log_bill ON promotion_log_local(bill_id);
CREATE INDEX idx_promo_log_sync ON promotion_log_local(synced_to_ho);
```

### **Optional: Voucher Cache**

```sql
CREATE TABLE voucher_cache (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    promotion_id TEXT NOT NULL,
    status TEXT DEFAULT 'active',           -- 'active', 'used', 'expired'
    expires_at TIMESTAMP NOT NULL,
    customer_phone TEXT,
    
    -- Usage
    used_at TIMESTAMP,
    used_bill_id TEXT,
    
    -- Sync
    version INTEGER,
    synced_at TIMESTAMP,
    
    FOREIGN KEY (promotion_id) REFERENCES promotion_cache(id)
);

CREATE INDEX idx_voucher_code ON voucher_cache(code, status);
CREATE INDEX idx_voucher_promo ON voucher_cache(promotion_id);
```

---

## 🔄 Sync Process

### **Step 1: Request Sync from HO**

**POS Request:**
```http
GET /api/promotions/sync/?store_id=xxx&since_version=123
Authorization: Bearer {token}
```

**HO Response:**
```json
{
  "store_id": "uuid-store-123",
  "store_name": "Yogya Surabaya",
  "current_version": 150,
  "synced_at": "2026-01-26T10:30:00Z",
  "total_promotions": 15,
  "promotions": [
    {
      "id": "promo-uuid-1",
      "code": "DISC10",
      "name": "10% Discount All Items",
      "description": "Get 10% off on all purchases",
      "promo_type": "percent_discount",
      "execution_stage": "subtotal",
      
      "rules": {
        "discount": {
          "type": "percent",
          "value": 10.0,
          "max_cap": 50000.0
        },
        "requirements": {
          "min_purchase": 50000.0,
          "min_quantity": 0,
          "min_items": 0
        },
        "eligibility": {
          "valid_days": [0, 1, 2, 3, 4, 5, 6],
          "valid_hours": {
            "start": "00:00:00",
            "end": "23:59:59"
          },
          "channels": ["dine_in", "takeaway"],
          "member_only": false,
          "member_tiers": []
        },
        "filters": {
          "product_ids": [],
          "category_ids": [],
          "exclude_product_ids": [],
          "exclude_category_ids": []
        }
      },
      
      "stacking": {
        "is_stackable": false,
        "cannot_combine_with": [],
        "priority": 100,
        "execution_priority": 500
      },
      
      "validity": {
        "valid_from": "2026-01-01",
        "valid_until": "2026-12-31"
      },
      
      "flags": {
        "is_active": true,
        "is_member_only": false,
        "require_voucher": false,
        "is_auto_apply": true
      },
      
      "version": 150,
      "compiled_at": "2026-01-26T10:00:00Z"
    }
    // ... more promotions
  ]
}
```

### **Step 2: Store in Local Database**

**Pseudo-code:**
```javascript
function syncPromotions(syncData) {
    const db = getDatabase();
    
    db.transaction(() => {
        for (const promo of syncData.promotions) {
            // Upsert (Insert or Update)
            db.execute(`
                INSERT INTO promotion_cache (
                    id, code, name, description, promo_type, execution_stage,
                    promotion_data, valid_from, valid_until, valid_days,
                    valid_hours_start, valid_hours_end, store_id,
                    is_active, is_member_only, require_voucher, is_auto_apply,
                    priority, execution_priority, is_stackable, cannot_combine_with,
                    version, synced_at, checksum
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    code = excluded.code,
                    name = excluded.name,
                    promotion_data = excluded.promotion_data,
                    version = excluded.version,
                    synced_at = excluded.synced_at,
                    updated_at = CURRENT_TIMESTAMP
            `, [
                promo.id,
                promo.code,
                promo.name,
                promo.description,
                promo.promo_type,
                promo.execution_stage,
                JSON.stringify(promo.rules),
                promo.validity.valid_from,
                promo.validity.valid_until,
                JSON.stringify(promo.rules.eligibility.valid_days),
                promo.rules.eligibility.valid_hours.start,
                promo.rules.eligibility.valid_hours.end,
                syncData.store_id,
                promo.flags.is_active ? 1 : 0,
                promo.flags.is_member_only ? 1 : 0,
                promo.flags.require_voucher ? 1 : 0,
                promo.flags.is_auto_apply ? 1 : 0,
                promo.stacking.priority,
                promo.stacking.execution_priority,
                promo.stacking.is_stackable ? 1 : 0,
                JSON.stringify(promo.stacking.cannot_combine_with),
                promo.version,
                syncData.synced_at,
                generateChecksum(promo)
            ]);
        }
    });
    
    console.log(`Synced ${syncData.total_promotions} promotions successfully`);
}
```

---

## 🎯 Promotion Evaluation Engine

### **Engine Architecture**

```
┌────────────────────────────────────────────────────────────┐
│  INPUT: Bill Draft + Customer Context + Payment Context    │
└────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 1: Load Active Promotions                            │
│  - Query from promotion_cache                              │
│  - Filter: is_active=1, valid dates                        │
│  - Sort by: priority DESC, execution_priority ASC          │
└────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 2: Pre-screening (Fast Filter)                       │
│  - Check valid_days (today's day of week)                  │
│  - Check valid_hours (current time)                        │
│  - Check channel (dine_in/takeaway/etc)                    │
│  - Check member_only flag                                  │
│  → Result: Eligible promotions for detailed check          │
└────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 3: Detailed Eligibility Check                        │
│  For each eligible promotion:                              │
│  - Parse promotion_data JSON                               │
│  - Check requirements (min_purchase, min_qty, etc)         │
│  - Check product/category filters                          │
│  - Check usage limits (if tracked locally)                 │
│  → Result: Qualified promotions                            │
└────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 4: Conflict Resolution                               │
│  - Group by execution_stage                                │
│  - Handle cannot_combine_with rules                        │
│  - Apply stacking logic                                    │
│  - Select best promotions to apply                         │
│  → Result: Final promotions to apply                       │
└────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 5: Calculate Discounts                               │
│  Execute in order: item → subtotal → payment               │
│  - Call type-specific calculator                           │
│  - Apply max_cap if exists                                 │
│  - Update bill draft with discounts                        │
│  → Result: Bill with applied discounts                     │
└────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│  STEP 6: Create Logs                                       │
│  - Log applied promotions                                  │
│  - Log skipped promotions with reasons                     │
│  - Save to promotion_log_local                             │
│  → Result: Audit trail                                     │
└────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│  OUTPUT: Updated Bill + Applied Promotions + Logs          │
└────────────────────────────────────────────────────────────┘
```

---

## 💰 Calculation Logic per Promotion Type

This section provides detailed implementation for all **12 promotion types** supported by the system:

| # | Type | Code | Execution Stage | Description |
|---|------|------|----------------|-------------|
| 1 | Percent Discount | `percent_discount` | item_level / subtotal | Percentage off on items or bill |
| 2 | Amount Discount | `amount_discount` | item_level / subtotal | Fixed amount off |
| 3 | Buy X Get Y | `buy_x_get_y` | item_level | BOGO - Buy 2 Get 1 Free |
| 4 | Combo Deal | `combo` | item_level | Bundle multiple items at special price |
| 5 | Free Item | `free_item` | item_level | Get free product with purchase |
| 6 | Happy Hour | `happy_hour` | item_level | Time-based special pricing |
| 7 | Cashback | `cashback` | post_payment | Post-payment reward/points |
| 8 | Payment Discount | `payment_discount` | payment | Discount for specific payment method |
| 9 | Package/Set Menu | `package` | item_level | Pre-defined set menu with fixed price |
| 10 | Mix & Match | `mix_match` | item_level | Choose N items from category at special price |
| 11 | Upsell/Add-on | `upsell` | item_level | Special price when buying specific item |
| 12 | Threshold/Tiered | `threshold_tier` | subtotal | Discount based on total spend |

---

### **1. PERCENT DISCOUNT**

**Input Data Structure:**
```json
{
  \"promo_type\": \"percent_discount\",
  \"rules\": {
    \"discount\": {
      \"type\": \"percent\",
      \"value\": 10.0,
      \"max_cap\": 50000.0
    },
    \"requirements\": {
      \"min_purchase\": 100000.0
    }
  }
}
```

**Calculation Logic:**
```javascript
function calculatePercentDiscount(bill, promotion) {
    const rules = promotion.rules;
    
    // 1. Check minimum purchase
    if (bill.subtotal < rules.requirements.min_purchase) {
        return {
            status: 'skipped',
            reason: \Minimum purchase Rp \ not met\,
            discount: 0
        };
    }
    
    // 2. Calculate discount
    let discountAmount = bill.subtotal * (rules.discount.value / 100);
    
    // 3. Apply max cap
    if (rules.discount.max_cap && discountAmount > rules.discount.max_cap) {
        discountAmount = rules.discount.max_cap;
    }
    
    // 4. Ensure discount doesn't exceed subtotal
    if (discountAmount > bill.subtotal) {
        discountAmount = bill.subtotal;
    }
    
    return {
        status: 'applied',
        reason: \\% discount applied\,
        discount: discountAmount,
        original: bill.subtotal,
        final: bill.subtotal - discountAmount
    };
}
```

**Example:**
```
Bill Subtotal: Rp 150,000
Promo: 10% discount, max cap Rp 50,000
Calculation: 150,000 × 10% = Rp 15,000
Max Cap Check: 15,000 < 50,000 ✓
Final Discount: Rp 15,000
Final Total: Rp 135,000
```

---

### **2. AMOUNT DISCOUNT**

**Input Data Structure:**
```json
{
  \"promo_type\": \"amount_discount\",
  \"rules\": {
    \"discount\": {
      \"type\": \"amount\",
      \"value\": 20000.0
    },
    \"requirements\": {
      \"min_purchase\": 100000.0
    }
  }
}
```

**Calculation Logic:**
```javascript
function calculateAmountDiscount(bill, promotion) {
    const rules = promotion.rules;
    
    // 1. Check minimum purchase
    if (bill.subtotal < rules.requirements.min_purchase) {
        return {
            status: 'skipped',
            reason: \Minimum purchase Rp \ not met\,
            discount: 0
        };
    }
    
    // 2. Get discount amount
    let discountAmount = rules.discount.value;
    
    // 3. Ensure discount doesn't exceed subtotal
    if (discountAmount > bill.subtotal) {
        discountAmount = bill.subtotal;
    }
    
    return {
        status: 'applied',
        reason: \Rp \ discount applied\,
        discount: discountAmount,
        original: bill.subtotal,
        final: bill.subtotal - discountAmount
    };
}
```

**Example:**
```
Bill Subtotal: Rp 150,000
Promo: Rp 20,000 off, min purchase Rp 100,000
Check: 150,000 >= 100,000 ✓
Final Discount: Rp 20,000
Final Total: Rp 130,000
```

---

### **3. BUY X GET Y (BOGO)**

**Input Data Structure:**
```json
{
  \"promo_type\": \"buy_x_get_y\",
  \"rules\": {
    \"bogo\": {
      \"buy_qty\": 2,
      \"get_qty\": 1,
      \"get_product_id\": \"product-uuid-cola\",
      \"discount_type\": \"free\"
    },
    \"filters\": {
      \"product_ids\": [\"product-uuid-burger\"]
    }
  }
}
```

**Calculation Logic:**
```javascript
function calculateBOGO(bill, promotion) {
    const rules = promotion.rules;
    const bogo = rules.bogo;
    
    // 1. Find qualifying items (buy items)
    const buyItems = bill.items.filter(item => 
        rules.filters.product_ids.includes(item.product_id)
    );
    
    if (buyItems.length === 0) {
        return {
            status: 'skipped',
            reason: 'No qualifying products in bill',
            discount: 0
        };
    }
    
    // 2. Calculate total quantity of buy items
    const totalBuyQty = buyItems.reduce((sum, item) => sum + item.quantity, 0);
    
    // 3. Calculate how many free items customer gets
    const freeItemsCount = Math.floor(totalBuyQty / bogo.buy_qty) * bogo.get_qty;
    
    if (freeItemsCount === 0) {
        return {
            status: 'skipped',
            reason: \Need to buy \ items to qualify\,
            discount: 0
        };
    }
    
    // 4. Find get_product price
    const getProduct = getProductById(bogo.get_product_id);
    if (!getProduct) {
        return {
            status: 'failed',
            reason: 'Free product not found',
            discount: 0
        };
    }
    
    // 5. Calculate discount (free items value)
    const discountAmount = getProduct.price * freeItemsCount;
    
    // 6. Add free items to bill (with price = 0)
    addFreeToBill(bill, getProduct, freeItemsCount, promotion.id);
    
    return {
        status: 'applied',
        reason: \Buy \ Get \ applied: \ free item(s)\,
        discount: discountAmount,
        free_items: freeItemsCount,
        affected_items: buyItems.map(i => i.id)
    };
}
```

**Example:**
```
Promo: Buy 2 Burgers Get 1 Cola Free
Bill Items:
  - 3 × Burger @ Rp 25,000 = Rp 75,000
  
Calculation:
  - Total burgers: 3
  - Free items: floor(3 / 2) × 1 = 1 free Cola
  - Cola price: Rp 10,000
  - Discount value: Rp 10,000

Result:
  - Add: 1 × Cola (FREE) @ Rp 0
  - Discount logged: Rp 10,000
  - Final total: Rp 75,000 (burgers) + Rp 0 (cola) = Rp 75,000
```

---

### **4. PACKAGE/SET MENU**

**Input Data Structure:**
```json
{
  \"promo_type\": \"package\",
  \"rules\": {
    \"package\": {
      \"name\": \"Paket Hemat A\",
      \"price\": 35000.0,
      \"items\": [
        {
          \"type\": \"fixed\",
          \"product_id\": \"product-uuid-nasi\",
          \"quantity\": 1,
          \"is_required\": true
        },
        {
          \"type\": \"choice\",
          \"category_id\": \"category-uuid-ayam\",
          \"quantity\": 1,
          \"is_required\": true,
          \"min_selection\": 1,
          \"max_selection\": 1
        },
        {
          \"type\": \"choice\",
          \"category_id\": \"category-uuid-drinks\",
          \"quantity\": 1,
          \"is_required\": true,
          \"min_selection\": 1,
          \"max_selection\": 1
        }
      ],
      \"allow_modification\": false
    }
  }
}
```

**Calculation Logic:**
```javascript
function calculatePackage(selectedItems, promotion) {
    const rules = promotion.rules;
    const packageDef = rules.package;
    
    // 1. Validate all required items selected
    for (const packageItem of packageDef.items) {
        if (packageItem.is_required) {
            const found = selectedItems.find(si => 
                (packageItem.type === 'fixed' && si.product_id === packageItem.product_id) ||
                (packageItem.type === 'choice' && si.category_id === packageItem.category_id)
            );
            
            if (!found) {
                return {
                    status: 'skipped',
                    reason: 'Required package items not selected',
                    discount: 0
                };
            }
        }
    }
    
    // 2. Calculate original total price of components
    let originalTotal = 0;
    const componentPrices = [];
    
    for (const selectedItem of selectedItems) {
        const product = getProductById(selectedItem.product_id);
        const itemTotal = product.price * selectedItem.quantity;
        originalTotal += itemTotal;
        componentPrices.push({
            product: product.name,
            price: product.price,
            quantity: selectedItem.quantity,
            subtotal: itemTotal
        });
    }
    
    // 3. Calculate discount (difference between original and package price)
    const discountAmount = originalTotal - packageDef.price;
    
    if (discountAmount <= 0) {
        return {
            status: 'skipped',
            reason: 'Package price higher than components',
            discount: 0
        };
    }
    
    // 4. Create package bill item
    const packageBillItem = {
        type: 'package',
        promotion_id: promotion.id,
        package_name: packageDef.name,
        price: packageDef.price,
        quantity: 1,
        components: componentPrices,
        original_total: originalTotal,
        discount: discountAmount
    };
    
    return {
        status: 'applied',
        reason: \Package \ applied\,
        discount: discountAmount,
        original: originalTotal,
        final: packageDef.price,
        package_item: packageBillItem
    };
}
```

**Example:**
```
Package: Paket Hemat A = Rp 35,000
Components selected:
  - 1 × Nasi Putih @ Rp 10,000
  - 1 × Ayam Goreng @ Rp 18,000
  - 1 × Es Teh @ Rp 8,000
  
Original Total: Rp 36,000
Package Price: Rp 35,000
Discount: Rp 36,000 - Rp 35,000 = Rp 1,000

Bill shows:
  - Paket Hemat A (Nasi, Ayam Goreng, Es Teh) = Rp 35,000
  - Discount Applied: Rp 1,000
```

---

### **5. TIERED/THRESHOLD PROMOTION**

**Input Data Structure:**
```json
{
  \"promo_type\": \"threshold_tier\",
  \"rules\": {
    \"tiers\": [
      {
        \"name\": \"Tier 1\",
        \"min_amount\": 100000.0,
        \"max_amount\": 199999.0,
        \"discount_type\": \"amount\",
        \"discount_value\": 10000.0
      },
      {
        \"name\": \"Tier 2\",
        \"min_amount\": 200000.0,
        \"max_amount\": 299999.0,
        \"discount_type\": \"amount\",
        \"discount_value\": 25000.0
      },
      {
        \"name\": \"Tier 3\",
        \"min_amount\": 300000.0,
        \"max_amount\": null,
        \"discount_type\": \"amount\",
        \"discount_value\": 50000.0
      }
    ]
  }
}
```

**Calculation Logic:**
```javascript
function calculateTiered(bill, promotion) {
    const rules = promotion.rules;
    const tiers = rules.tiers;
    
    // 1. Find applicable tier based on subtotal
    let applicableTier = null;
    
    for (const tier of tiers) {
        if (bill.subtotal >= tier.min_amount) {
            if (tier.max_amount === null || bill.subtotal <= tier.max_amount) {
                applicableTier = tier;
                break;
            }
        }
    }
    
    if (!applicableTier) {
        return {
            status: 'skipped',
            reason: \Subtotal Rp \ doesn't qualify for any tier\,
            discount: 0
        };
    }
    
    // 2. Calculate discount based on tier
    let discountAmount = 0;
    
    if (applicableTier.discount_type === 'amount') {
        discountAmount = applicableTier.discount_value;
    } else if (applicableTier.discount_type === 'percent') {
        discountAmount = bill.subtotal * (applicableTier.discount_value / 100);
    }
    
    // 3. Ensure doesn't exceed subtotal
    if (discountAmount > bill.subtotal) {
        discountAmount = bill.subtotal;
    }
    
    return {
        status: 'applied',
        reason: \\ applied: Rp \ off\,
        discount: discountAmount,
        tier: applicableTier.name,
        original: bill.subtotal,
        final: bill.subtotal - discountAmount
    };
}
```

**Example:**
```
Promo: Tiered Discount
  - Tier 1: Rp 100k-199k → Rp 10k off
  - Tier 2: Rp 200k-299k → Rp 25k off
  - Tier 3: Rp 300k+     → Rp 50k off

Bill Subtotal: Rp 250,000

Check:
  - 250,000 >= 200,000 ✓
  - 250,000 <= 299,999 ✓
  - Tier 2 applies

Discount: Rp 25,000
Final: Rp 225,000
```

---

### **6. HAPPY HOUR**

**Input Data Structure:**
```json
{
  \"promo_type\": \"happy_hour\",
  \"rules\": {
    \"discount\": {
      \"type\": \"special_price\",
      \"value\": 15000.0
    },
    \"eligibility\": {
      \"valid_hours\": {
        \"start\": \"14:00:00\",
        \"end\": \"17:00:00\"
      }
    },
    \"filters\": {
      \"category_ids\": [\"category-uuid-beverages\"]
    }
  }
}
```

**Calculation Logic:**
```javascript
function calculateHappyHour(bill, promotion, currentTime) {
    const rules = promotion.rules;
    
    // 1. Check if current time is within happy hour
    const startTime = parseTime(rules.eligibility.valid_hours.start);
    const endTime = parseTime(rules.eligibility.valid_hours.end);
    
    if (currentTime < startTime || currentTime > endTime) {
        return {
            status: 'skipped',
            reason: \Happy hour only valid between \-\\,
            discount: 0
        };
    }
    
    // 2. Find qualifying items
    const qualifyingItems = bill.items.filter(item =>
        rules.filters.category_ids.includes(item.category_id)
    );
    
    if (qualifyingItems.length === 0) {
        return {
            status: 'skipped',
            reason: 'No qualifying items in bill',
            discount: 0
        };
    }
    
    // 3. Calculate discount (difference from special price)
    let totalDiscount = 0;
    const affectedItems = [];
    
    for (const item of qualifyingItems) {
        const originalPrice = item.price * item.quantity;
        const specialPrice = rules.discount.value * item.quantity;
        const itemDiscount = originalPrice - specialPrice;
        
        if (itemDiscount > 0) {
            totalDiscount += itemDiscount;
            affectedItems.push({
                item_id: item.id,
                product: item.product_name,
                quantity: item.quantity,
                original_price: item.price,
                special_price: rules.discount.value,
                discount: itemDiscount
            });
        }
    }
    
    return {
        status: 'applied',
        reason: \Happy hour pricing applied to \ item(s)\,
        discount: totalDiscount,
        affected_items: affectedItems
    };
}
```

**Example:**
```
Promo: Happy Hour Beverages (14:00-17:00)
Special Price: Rp 15,000 (normally Rp 20,000)
Current Time: 15:30

Bill Items:
  - 2 × Iced Coffee @ Rp 20,000 = Rp 40,000
  - 1 × Burger @ Rp 25,000 = Rp 25,000

Qualifying: 2 × Iced Coffee
Calculation:
  - Original: 2 × 20,000 = Rp 40,000
  - Special: 2 × 15,000 = Rp 30,000
  - Discount: Rp 10,000

Final Bill:
  - 2 × Iced Coffee (Happy Hour) = Rp 30,000
  - 1 × Burger = Rp 25,000
  - Total: Rp 55,000
```

---

### **7. PAYMENT METHOD PROMOTION**

**Input Data Structure:**
```json
{
  \"promo_type\": \"payment_discount\",
  \"rules\": {
    \"discount\": {
      \"type\": \"percent\",
      \"value\": 5.0,
      \"max_cap\": 20000.0
    },
    \"payment\": {
      \"methods\": [\"gopay\", \"ovo\"],
      \"min_amount\": 50000.0
    }
  }
}
```

**Calculation Logic:**
```javascript
function calculatePaymentPromo(bill, promotion, paymentMethod) {
    const rules = promotion.rules;
    
    // 1. Check payment method
    if (!rules.payment.methods.includes(paymentMethod)) {
        return {
            status: 'skipped',
            reason: \Payment method '\' not eligible\,
            discount: 0
        };
    }
    
    // 2. Check minimum amount
    if (bill.total < rules.payment.min_amount) {
        return {
            status: 'skipped',
            reason: \Minimum payment Rp \ not met\,
            discount: 0
        };
    }
    
    // 3. Calculate discount
    let discountAmount = bill.total * (rules.discount.value / 100);
    
    // 4. Apply max cap
    if (rules.discount.max_cap && discountAmount > rules.discount.max_cap) {
        discountAmount = rules.discount.max_cap;
    }
    
    return {
        status: 'applied',
        reason: \\% discount for \ payment\,
        discount: discountAmount,
        payment_method: paymentMethod,
        original: bill.total,
        final: bill.total - discountAmount
    };
}
```

---

### **8. COMBO DEAL**

**Input Data Structure:**
```json
{
  "promo_type": "combo",
  "rules": {
    "combo": {
      "products": [
        {"product_id": "product-uuid-burger", "quantity": 1},
        {"product_id": "product-uuid-fries", "quantity": 1},
        {"product_id": "product-uuid-coke", "quantity": 1}
      ],
      "combo_price": 45000.0
    },
    "requirements": {
      "all_items_required": true
    }
  }
}
```

**Calculation Logic:**
```javascript
function calculateComboPromo(bill, promotion) {
    const rules = promotion.rules;
    const comboProducts = rules.combo.products;
    
    // 1. Check if all combo items are in bill
    const billItems = bill.items;
    let hasAllItems = true;
    let comboItemsInBill = [];
    let originalTotal = 0;
    
    for (const comboItem of comboProducts) {
        const billItem = billItems.find(item => 
            item.product_id === comboItem.product_id && 
            item.quantity >= comboItem.quantity
        );
        
        if (!billItem) {
            hasAllItems = false;
            break;
        }
        
        comboItemsInBill.push({
            ...billItem,
            required_qty: comboItem.quantity
        });
        originalTotal += billItem.price * comboItem.quantity;
    }
    
    // 2. Check if combo can be applied
    if (!hasAllItems) {
        return {
            status: 'skipped',
            reason: 'Not all combo items in cart',
            discount: 0
        };
    }
    
    // 3. Calculate discount
    const discountAmount = originalTotal - rules.combo.combo_price;
    
    if (discountAmount <= 0) {
        return {
            status: 'skipped',
            reason: 'Combo price higher than original price',
            discount: 0
        };
    }
    
    return {
        status: 'applied',
        reason: `Combo applied: ${comboProducts.length} items for Rp ${rules.combo.combo_price}`,
        discount: discountAmount,
        combo_items: comboItemsInBill,
        original: originalTotal,
        final: rules.combo.combo_price
    };
}
```

**Example:**
```
Promo: Paket Hemat Combo
  - 1 × Burger + 1 × Fries + 1 × Coke = Rp 45,000

Bill Items:
  - 1 × Burger @ Rp 25,000
  - 1 × Fries @ Rp 15,000
  - 1 × Coke @ Rp 10,000

Original Total: Rp 50,000
Combo Price: Rp 45,000
Discount: Rp 5,000
```

---

### **9. FREE ITEM**

**Input Data Structure:**
```json
{
  "promo_type": "free_item",
  "rules": {
    "free_item": {
      "trigger_product_id": "product-uuid-main-dish",
      "trigger_min_qty": 1,
      "free_product_id": "product-uuid-dessert",
      "free_qty": 1
    },
    "requirements": {
      "min_purchase": 100000.0
    }
  }
}
```

**Calculation Logic:**
```javascript
function calculateFreeItem(bill, promotion) {
    const rules = promotion.rules;
    
    // 1. Check minimum purchase
    if (bill.subtotal < rules.requirements.min_purchase) {
        return {
            status: 'skipped',
            reason: `Minimum purchase Rp ${rules.requirements.min_purchase} not met`,
            discount: 0
        };
    }
    
    // 2. Check if trigger product is in bill
    const triggerItem = bill.items.find(item => 
        item.product_id === rules.free_item.trigger_product_id &&
        item.quantity >= rules.free_item.trigger_min_qty
    );
    
    if (!triggerItem) {
        return {
            status: 'skipped',
            reason: 'Trigger product not in cart',
            discount: 0
        };
    }
    
    // 3. Get free product price
    const freeProduct = getProductById(rules.free_item.free_product_id);
    const discountAmount = freeProduct.price * rules.free_item.free_qty;
    
    return {
        status: 'applied',
        reason: `Free ${freeProduct.name} × ${rules.free_item.free_qty}`,
        discount: discountAmount,
        free_items: [{
            product_id: freeProduct.id,
            name: freeProduct.name,
            quantity: rules.free_item.free_qty,
            original_price: freeProduct.price,
            discount_price: 0
        }],
        original: bill.subtotal,
        final: bill.subtotal
    };
}
```

**Example:**
```
Promo: Buy Main Dish, Get Free Dessert
  - Min Purchase: Rp 100,000
  - Trigger: Buy 1 × Main Dish
  - Free: 1 × Ice Cream

Bill:
  - 2 × Steak @ Rp 75,000 = Rp 150,000

Result:
  - Trigger met ✓
  - Add: 1 × Ice Cream (FREE) @ Rp 0
  - Discount value: Rp 15,000 (ice cream price)
```

---

### **10. CASHBACK**

**Input Data Structure:**
```json
{
  "promo_type": "cashback",
  "rules": {
    "cashback": {
      "type": "percent",
      "value": 10.0,
      "max_amount": 50000.0,
      "method": "points"
    },
    "requirements": {
      "min_purchase": 100000.0,
      "payment_methods": ["gopay", "ovo", "card"]
    }
  }
}
```

**Calculation Logic:**
```javascript
function calculateCashback(bill, promotion, paymentMethod) {
    const rules = promotion.rules;
    
    // 1. Check minimum purchase
    if (bill.total < rules.requirements.min_purchase) {
        return {
            status: 'skipped',
            reason: `Minimum purchase Rp ${rules.requirements.min_purchase} not met`,
            cashback: 0
        };
    }
    
    // 2. Check payment method
    if (rules.requirements.payment_methods && 
        !rules.requirements.payment_methods.includes(paymentMethod)) {
        return {
            status: 'skipped',
            reason: `Payment method '${paymentMethod}' not eligible`,
            cashback: 0
        };
    }
    
    // 3. Calculate cashback
    let cashbackAmount = 0;
    if (rules.cashback.type === 'percent') {
        cashbackAmount = bill.total * (rules.cashback.value / 100);
    } else if (rules.cashback.type === 'amount') {
        cashbackAmount = rules.cashback.value;
    }
    
    // 4. Apply max cap
    if (rules.cashback.max_amount && cashbackAmount > rules.cashback.max_amount) {
        cashbackAmount = rules.cashback.max_amount;
    }
    
    return {
        status: 'applied',
        reason: `${rules.cashback.value}% cashback (max Rp ${rules.cashback.max_amount})`,
        cashback: cashbackAmount,
        cashback_method: rules.cashback.method, // 'points', 'wallet', 'voucher'
        payment_method: paymentMethod,
        bill_total: bill.total
    };
}
```

**Example:**
```
Promo: 10% Cashback via GoPay
  - Min Purchase: Rp 100,000
  - Max Cashback: Rp 50,000
  - Payment: GoPay/OVO/Card

Bill Total: Rp 250,000
Payment: GoPay

Cashback Calculation:
  - 250,000 × 10% = Rp 25,000
  - Max cap: Rp 50,000 ✓
  - Cashback: Rp 25,000

Result:
  - Customer pays: Rp 250,000
  - Gets back: Rp 25,000 (as points/wallet)
```

---

### **11. MIX & MATCH**

**Input Data Structure:**
```json
{
  "promo_type": "mix_match",
  "rules": {
    "mix_match": {
      "category_id": "category-uuid-beverages",
      "required_quantity": 3,
      "special_price": 50000.0,
      "allow_same_product": true
    },
    "requirements": {
      "min_items": 3
    }
  }
}
```

**Calculation Logic:**
```javascript
function calculateMixMatch(bill, promotion) {
    const rules = promotion.rules;
    
    // 1. Get items from specified category
    const eligibleItems = bill.items.filter(item => 
        item.category_id === rules.mix_match.category_id
    );
    
    if (eligibleItems.length === 0) {
        return {
            status: 'skipped',
            reason: 'No items from eligible category',
            discount: 0
        };
    }
    
    // 2. Calculate total quantity
    const totalQty = eligibleItems.reduce((sum, item) => sum + item.quantity, 0);
    
    // 3. Check if minimum quantity met
    if (totalQty < rules.mix_match.required_quantity) {
        return {
            status: 'skipped',
            reason: `Need ${rules.mix_match.required_quantity} items, only have ${totalQty}`,
            discount: 0
        };
    }
    
    // 4. Calculate how many sets can be made
    const sets = Math.floor(totalQty / rules.mix_match.required_quantity);
    
    // 5. Calculate original price for sets
    let originalPrice = 0;
    let remainingQty = sets * rules.mix_match.required_quantity;
    
    for (const item of eligibleItems) {
        const qtyToCount = Math.min(item.quantity, remainingQty);
        originalPrice += item.price * qtyToCount;
        remainingQty -= qtyToCount;
        if (remainingQty === 0) break;
    }
    
    // 6. Calculate discount
    const specialTotal = sets * rules.mix_match.special_price;
    const discountAmount = originalPrice - specialTotal;
    
    return {
        status: 'applied',
        reason: `${sets} set(s) of ${rules.mix_match.required_quantity} items for Rp ${rules.mix_match.special_price} each`,
        discount: discountAmount,
        sets: sets,
        items_per_set: rules.mix_match.required_quantity,
        original: originalPrice,
        final: specialTotal
    };
}
```

**Example:**
```
Promo: Mix & Match - Any 3 Beverages for Rp 50,000

Bill Items (Beverages):
  - 2 × Coffee @ Rp 20,000 = Rp 40,000
  - 1 × Tea @ Rp 15,000 = Rp 15,000
  - 1 × Juice @ Rp 25,000 = Rp 25,000

Total: 4 items = 1 set of 3 items + 1 extra

Calculation:
  - Set 1: 3 items @ Rp 50,000
  - Original price (3 items): Rp 55,000
  - Discount: Rp 5,000
  - Extra item (1): Regular price Rp 25,000

Final:
  - 3 items (Mix & Match): Rp 50,000
  - 1 × Juice (regular): Rp 25,000
  - Total: Rp 75,000
```

---

### **12. UPSELL/ADD-ON**

**Input Data Structure:**
```json
{
  "promo_type": "upsell",
  "rules": {
    "upsell": {
      "required_product_id": "product-uuid-main-course",
      "required_min_qty": 1,
      "upsell_product_id": "product-uuid-side-dish",
      "special_price": 10000.0,
      "message": "Add side dish for only Rp 10,000!"
    }
  }
}
```

**Calculation Logic:**
```javascript
function calculateUpsell(bill, promotion) {
    const rules = promotion.rules;
    
    // 1. Check if required product is in bill
    const requiredItem = bill.items.find(item => 
        item.product_id === rules.upsell.required_product_id &&
        item.quantity >= rules.upsell.required_min_qty
    );
    
    if (!requiredItem) {
        return {
            status: 'skipped',
            reason: 'Required product not in cart',
            discount: 0,
            upsell_available: false
        };
    }
    
    // 2. Check if upsell product is already in bill
    const upsellItem = bill.items.find(item => 
        item.product_id === rules.upsell.upsell_product_id
    );
    
    if (!upsellItem) {
        // Offer upsell (not auto-applied, needs user action)
        return {
            status: 'available',
            reason: rules.upsell.message,
            discount: 0,
            upsell_available: true,
            upsell_offer: {
                product_id: rules.upsell.upsell_product_id,
                special_price: rules.upsell.special_price,
                message: rules.upsell.message
            }
        };
    }
    
    // 3. If upsell product is in bill, apply special price
    const upsellProduct = getProductById(rules.upsell.upsell_product_id);
    const originalPrice = upsellProduct.price * upsellItem.quantity;
    const specialTotal = rules.upsell.special_price * upsellItem.quantity;
    const discountAmount = originalPrice - specialTotal;
    
    return {
        status: 'applied',
        reason: `Special price for ${upsellProduct.name}: Rp ${rules.upsell.special_price}`,
        discount: discountAmount,
        upsell_applied: true,
        original_price: upsellProduct.price,
        special_price: rules.upsell.special_price,
        quantity: upsellItem.quantity,
        original: originalPrice,
        final: specialTotal
    };
}
```

**Example:**
```
Promo: Add Fries for only Rp 10,000 when you buy Burger

Scenario 1 - Offer Upsell:
Bill Items:
  - 1 × Burger @ Rp 35,000

Result:
  - Show message: "Add Fries for only Rp 10,000!"
  - Upsell available but not applied yet

Scenario 2 - Upsell Applied:
Bill Items:
  - 1 × Burger @ Rp 35,000
  - 1 × Fries @ Rp 15,000 (regular price)

Result:
  - Upsell promo applied
  - Fries discounted to Rp 10,000
  - Discount: Rp 5,000
  - Total: Rp 45,000 (instead of Rp 50,000)
```

---

## 🌐 Cross-Brand Promotions

Cross-brand promotions allow sophisticated marketing strategies across multiple brands within the same company. This section explains how to implement cross-brand logic at the POS/Edge level.

### **Cross-Brand Types**

| Type | Code | Description | POS Implementation |
|------|------|-------------|-------------------|
| Trigger-Benefit | `trigger_benefit` | Buy at Brand A → Get discount at Brand B | Track trigger, validate benefit |
| Multi-Brand Spend | `multi_brand_spend` | Spend at 2+ brands → Get reward | Accumulate across transactions |
| Cross-Brand Bundle | `cross_brand_bundle` | Bundle products from multiple brands | Validate items from different brands |
| Loyalty Accumulate | `loyalty_accumulate` | Accumulate points across brands | Sum points from all brands |
| Same Receipt | `same_receipt` | Multiple brands in one transaction | Check cart for multi-brand items |

---

### **1. TRIGGER-BENEFIT (Most Common)**

**Use Case:** "Buy Coffee at AVRIL, get 20% off at YO-KOPI"

**Data Structure:**
```json
{
  "promo_type": "percent_discount",
  "is_cross_brand": true,
  "cross_brand_type": "trigger_benefit",
  "rules": {
    "trigger": {
      "brand_ids": ["brand-uuid-avril"],
      "min_amount": 25000.0,
      "validity_days": 7
    },
    "benefit": {
      "brand_ids": ["brand-uuid-yokopi"],
      "discount_percent": 20.0,
      "max_discount": 50000.0
    }
  }
}
```

**Implementation Logic:**
```javascript
function evaluateTriggerBenefit(bill, promotion, customer) {
    const rules = promotion.rules;
    
    // STAGE 1: Check if this is trigger transaction
    if (rules.trigger.brand_ids.includes(bill.brand_id)) {
        // This is a trigger brand
        if (bill.subtotal >= rules.trigger.min_amount) {
            // Issue benefit voucher for customer
            const expiresAt = new Date();
            expiresAt.setDate(expiresAt.getDate() + rules.trigger.validity_days);
            
            return {
                status: 'trigger_activated',
                action: 'issue_voucher',
                voucher: {
                    promotion_id: promotion.id,
                    customer_id: customer.id,
                    benefit_brand_ids: rules.benefit.brand_ids,
                    discount_percent: rules.benefit.discount_percent,
                    max_discount: rules.benefit.max_discount,
                    expires_at: expiresAt.toISOString()
                }
            };
        }
    }
    
    // STAGE 2: Check if this is benefit transaction
    if (rules.benefit.brand_ids.includes(bill.brand_id)) {
        // Check if customer has active voucher
        const voucher = await checkCustomerVoucher(customer.id, promotion.id);
        
        if (voucher && !voucher.is_used && new Date(voucher.expires_at) > new Date()) {
            // Apply discount
            let discount = bill.subtotal * (rules.benefit.discount_percent / 100);
            if (rules.benefit.max_discount && discount > rules.benefit.max_discount) {
                discount = rules.benefit.max_discount;
            }
            
            // Mark voucher as used
            await markVoucherUsed(voucher.id, bill.id);
            
            return {
                status: 'applied',
                reason: `Cross-brand discount: ${rules.benefit.discount_percent}% from trigger at other brand`,
                discount: discount,
                voucher_id: voucher.id
            };
        } else {
            return {
                status: 'skipped',
                reason: 'No active cross-brand voucher found'
            };
        }
    }
    
    return {
        status: 'skipped',
        reason: 'Brand not eligible for this cross-brand promotion'
    };
}
```

**Edge Database: Store Vouchers Locally**
```sql
CREATE TABLE cross_brand_vouchers (
    id TEXT PRIMARY KEY,
    promotion_id TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    trigger_brand_id TEXT,
    trigger_transaction_id TEXT,
    trigger_amount DECIMAL(10,2),
    benefit_brand_ids TEXT, -- JSON array
    discount_percent DECIMAL(5,2),
    max_discount DECIMAL(10,2),
    issued_at TIMESTAMP,
    expires_at TIMESTAMP,
    is_used INTEGER DEFAULT 0,
    used_at TIMESTAMP,
    used_transaction_id TEXT
);
```

---

### **2. CROSS-BRAND BUNDLE (Same Receipt)**

**Use Case:** "Combo: Main Course from CHICKEN SUMO + Drink from AVRIL = Rp 150k"

**Data Structure:**
```json
{
  "promo_type": "combo",
  "is_cross_brand": true,
  "cross_brand_type": "cross_brand_bundle",
  "rules": {
    "bundle": {
      "items": [
        {
          "brand_id": "brand-uuid-chicken-sumo",
          "category_id": "category-uuid-main-course",
          "quantity": 1
        },
        {
          "brand_id": "brand-uuid-avril",
          "category_id": "category-uuid-beverages",
          "quantity": 1
        }
      ],
      "bundle_price": 150000.0
    }
  }
}
```

**Implementation Logic:**
```javascript
function evaluateCrossBrandBundle(bill, promotion) {
    const rules = promotion.rules;
    const bundleItems = rules.bundle.items;
    
    // 1. Group bill items by brand
    const itemsByBrand = {};
    for (const item of bill.items) {
        if (!itemsByBrand[item.brand_id]) {
            itemsByBrand[item.brand_id] = [];
        }
        itemsByBrand[item.brand_id].push(item);
    }
    
    // 2. Check if all bundle requirements are met
    let bundleComplete = true;
    let originalTotal = 0;
    const matchedItems = [];
    
    for (const bundleItem of bundleItems) {
        const brandItems = itemsByBrand[bundleItem.brand_id] || [];
        
        // Find item from this brand in specified category
        const matchingItem = brandItems.find(item => 
            item.category_id === bundleItem.category_id &&
            item.quantity >= bundleItem.quantity
        );
        
        if (!matchingItem) {
            bundleComplete = false;
            break;
        }
        
        matchedItems.push({
            item: matchingItem,
            required_qty: bundleItem.quantity
        });
        originalTotal += matchingItem.price * bundleItem.quantity;
    }
    
    // 3. Apply bundle if complete
    if (!bundleComplete) {
        return {
            status: 'skipped',
            reason: 'Cross-brand bundle incomplete - missing items from one or more brands'
        };
    }
    
    const discount = originalTotal - rules.bundle.bundle_price;
    
    if (discount <= 0) {
        return {
            status: 'skipped',
            reason: 'Bundle price higher than original price'
        };
    }
    
    return {
        status: 'applied',
        reason: `Cross-brand bundle: ${bundleItems.length} items from ${bundleItems.length} brands`,
        discount: discount,
        bundle_items: matchedItems,
        original: originalTotal,
        final: rules.bundle.bundle_price
    };
}
```

**Example:**
```
Promo: Cross-Brand Combo
  - 1 × Main Course (CHICKEN SUMO) @ Rp 100,000
  - 1 × Drink (AVRIL) @ Rp 50,000
  - Bundle Price: Rp 150,000

Cart:
  - 1 × Ayam Goreng (CHICKEN SUMO) @ Rp 100,000
  - 1 × Iced Latte (AVRIL) @ Rp 50,000

Original: Rp 150,000
Bundle: Rp 150,000
Discount: Rp 0 (already at bundle price)

BUT if original was higher:
Original: Rp 180,000
Bundle: Rp 150,000
Discount: Rp 30,000 ✓
```

---

### **3. SAME RECEIPT MULTI-BRAND DISCOUNT**

**Use Case:** "Buy from 2+ brands in one transaction, get 15% off"

**Data Structure:**
```json
{
  "promo_type": "percent_discount",
  "is_cross_brand": true,
  "cross_brand_type": "same_receipt",
  "rules": {
    "same_receipt": {
      "eligible_brand_ids": ["brand-uuid-avril", "brand-uuid-chicken-sumo", "brand-uuid-yokopi"],
      "min_brands_in_cart": 2,
      "min_purchase": 100000.0
    },
    "discount": {
      "type": "percent",
      "value": 15.0,
      "max_cap": 100000.0
    }
  }
}
```

**Implementation Logic:**
```javascript
function evaluateSameReceiptMultiBrand(bill, promotion) {
    const rules = promotion.rules;
    
    // 1. Count unique brands in cart
    const brandsInCart = new Set();
    let eligibleTotal = 0;
    
    for (const item of bill.items) {
        // Check if item's brand is eligible
        if (rules.same_receipt.eligible_brand_ids.includes(item.brand_id)) {
            brandsInCart.add(item.brand_id);
            eligibleTotal += item.price * item.quantity;
        }
    }
    
    // 2. Check if minimum brands requirement met
    if (brandsInCart.size < rules.same_receipt.min_brands_in_cart) {
        return {
            status: 'skipped',
            reason: `Need items from ${rules.same_receipt.min_brands_in_cart} brands, only have ${brandsInCart.size}`
        };
    }
    
    // 3. Check minimum purchase
    if (eligibleTotal < rules.same_receipt.min_purchase) {
        return {
            status: 'skipped',
            reason: `Minimum purchase Rp ${rules.same_receipt.min_purchase} not met`
        };
    }
    
    // 4. Calculate discount
    let discount = eligibleTotal * (rules.discount.value / 100);
    
    if (rules.discount.max_cap && discount > rules.discount.max_cap) {
        discount = rules.discount.max_cap;
    }
    
    return {
        status: 'applied',
        reason: `Multi-brand discount: ${rules.discount.value}% off for shopping at ${brandsInCart.size} brands`,
        discount: discount,
        brands_count: brandsInCart.size,
        brands_list: Array.from(brandsInCart),
        original: eligibleTotal,
        final: eligibleTotal - discount
    };
}
```

**Example:**
```
Promo: Shop 2+ Brands, Get 15% Off
  - Min brands: 2
  - Min purchase: Rp 100,000

Cart:
  - 2 × Coffee (AVRIL) @ Rp 20,000 = Rp 40,000
  - 1 × Chicken (CHICKEN SUMO) @ Rp 75,000 = Rp 75,000
  
Brands in cart: 2 (AVRIL, CHICKEN SUMO) ✓
Total: Rp 115,000 ✓

Discount: Rp 115,000 × 15% = Rp 17,250
Final: Rp 97,750
```

---

### **4. MULTI-BRAND SPEND ACCUMULATION**

**Use Case:** "Spend Rp 50k at 2 different brands within 30 days → Get Rp 50k voucher"

**Data Structure:**
```json
{
  "promo_type": "cashback",
  "is_cross_brand": true,
  "cross_brand_type": "multi_brand_spend",
  "rules": {
    "accumulation": {
      "eligible_brand_ids": ["brand-uuid-avril", "brand-uuid-chicken-sumo", "brand-uuid-yokopi"],
      "min_brands": 2,
      "min_amount_per_brand": 50000.0,
      "time_window_days": 30
    },
    "reward": {
      "type": "voucher",
      "value": 50000.0,
      "validity_days": 30
    }
  }
}
```

**Implementation Logic (HO/Backend):**
```javascript
// This type requires backend processing, not real-time at POS
// POS only records the transaction, backend processes the accumulation

function trackMultiBrandSpend(transaction, promotion) {
    // 1. Record transaction in accumulation tracker
    const record = {
        promotion_id: promotion.id,
        customer_id: transaction.customer_id,
        brand_id: transaction.brand_id,
        transaction_id: transaction.id,
        amount: transaction.subtotal,
        transaction_date: transaction.created_at
    };
    
    // 2. Save to backend database
    await saveMultiBrandRecord(record);
    
    // 3. Check if customer qualified (async job)
    // This runs as background job, not blocking POS
    queueJob('check_multi_brand_qualification', {
        customer_id: transaction.customer_id,
        promotion_id: promotion.id
    });
    
    return {
        status: 'tracked',
        message: 'Transaction recorded for multi-brand accumulation'
    };
}

// Background job (runs on HO server)
async function checkMultiBrandQualification(customerId, promotionId) {
    const promotion = await getPromotion(promotionId);
    const rules = promotion.rules;
    
    // Get customer transactions in time window
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - rules.accumulation.time_window_days);
    
    const transactions = await getCustomerTransactions(
        customerId, 
        rules.accumulation.eligible_brand_ids,
        cutoffDate
    );
    
    // Group by brand and sum amounts
    const spendByBrand = {};
    for (const tx of transactions) {
        if (!spendByBrand[tx.brand_id]) {
            spendByBrand[tx.brand_id] = 0;
        }
        spendByBrand[tx.brand_id] += tx.amount;
    }
    
    // Check qualification
    const qualifiedBrands = Object.entries(spendByBrand).filter(
        ([brandId, amount]) => amount >= rules.accumulation.min_amount_per_brand
    );
    
    if (qualifiedBrands.length >= rules.accumulation.min_brands) {
        // Customer qualified! Issue reward
        await issueRewardVoucher(customerId, promotion, rules.reward);
        
        // Notify customer
        await sendNotification(customerId, {
            title: 'Congratulations!',
            message: `You've earned a Rp ${rules.reward.value} voucher for shopping at ${qualifiedBrands.length} brands!`
        });
    }
}
```

**Note:** This promotion type is processed on the backend, not real-time at POS. The POS only needs to:
1. Track the transaction
2. Upload to HO when online
3. Sync vouchers back from HO

---

### **Cross-Brand Implementation Checklist**

#### **At POS/Edge:**
- ✅ Support `is_cross_brand` flag in promotion data
- ✅ Implement trigger-benefit voucher storage
- ✅ Validate cross-brand bundle items by brand_id
- ✅ Count unique brands in cart for same-receipt promos
- ✅ Track transactions for multi-brand accumulation
- ✅ Sync vouchers from HO

#### **At Head Office:**
- ✅ Compile cross-brand rules into JSON
- ✅ Process multi-brand accumulation (background jobs)
- ✅ Issue cross-brand vouchers
- ✅ Sync vouchers to POS
- ✅ Track cross-brand promotion performance

#### **Database Sync:**
- ✅ Download: Active cross-brand promotions
- ✅ Download: Customer cross-brand vouchers
- ✅ Upload: Transaction data for accumulation tracking
- ✅ Upload: Voucher usage data

---

## 📝 Code Examples

### **Complete Evaluation Engine (JavaScript/TypeScript)**

```javascript
class PromotionEngine {
    constructor(database) {
        this.db = database;
    }
    
    /**
     * Main evaluation function
     * @param {Object} bill - Bill draft
     * @param {Object} customer - Customer context
     * @param {Object} payment - Payment context (optional)
     * @returns {Object} Evaluation result
     */
    async evaluate(bill, customer, payment = null) {
        const startTime = Date.now();
        
        // Step 1: Load active promotions
        const promotions = await this.loadActivePromotions(bill.store_id);
        
        // Step 2: Pre-screening
        const eligible = this.preScreenPromotions(promotions, bill, customer);
        
        // Step 3: Detailed eligibility check
        const qualified = await this.checkEligibility(eligible, bill, customer);
        
        // Step 4: Conflict resolution
        const toApply = this.resolveConflicts(qualified);
        
        // Step 5: Calculate discounts
        const results = await this.calculateDiscounts(toApply, bill, customer, payment);
        
        // Step 6: Create logs
        await this.createLogs(bill.id, results);
        
        const executionTime = Date.now() - startTime;
        
        return {
            applied: results.applied,
            skipped: results.skipped,
            total_discount: results.total_discount,
            original_total: bill.total,
            final_total: bill.total - results.total_discount,
            execution_time_ms: executionTime,
            logs: results.logs
        };
    }
    
    /**
     * Load active promotions from database
     */
    async loadActivePromotions(storeId) {
        const today = new Date().toISOString().split('T')[0];
        const now = new Date();
        
        const query = \
            SELECT * FROM promotion_cache
            WHERE store_id = ?
              AND is_active = 1
              AND valid_from <= ?
              AND valid_until >= ?
            ORDER BY priority DESC, execution_priority ASC
        \;
        
        return await this.db.all(query, [storeId, today, today]);
    }
    
    /**
     * Fast pre-screening based on quick filters
     */
    preScreenPromotions(promotions, bill, customer) {
        const now = new Date();
        const dayOfWeek = now.getDay(); // 0=Sunday, 1=Monday, etc
        const currentTime = now.toTimeString().split(' ')[0]; // "HH:MM:SS"
        
        return promotions.filter(promo => {
            // Check day of week
            if (promo.valid_days) {
                const validDays = JSON.parse(promo.valid_days);
                if (!validDays.includes(dayOfWeek)) {
                    return false;
                }
            }
            
            // Check time range
            if (promo.valid_hours_start && promo.valid_hours_end) {
                if (currentTime < promo.valid_hours_start || currentTime > promo.valid_hours_end) {
                    return false;
                }
            }
            
            // Check member only
            if (promo.is_member_only && !customer.member_id) {
                return false;
            }
            
            // Check voucher requirement
            if (promo.require_voucher && !bill.voucher_code) {
                return false;
            }
            
            return true;
        });
    }
    
    /**
     * Detailed eligibility check with promotion rules
     */
    async checkEligibility(promotions, bill, customer) {
        const qualified = [];
        
        for (const promo of promotions) {
            const rules = JSON.parse(promo.promotion_data);
            const check = await this.checkPromotionRules(promo, rules, bill, customer);
            
            if (check.eligible) {
                qualified.push({
                    promotion: promo,
                    rules: rules,
                    check: check
                });
            }
        }
        
        return qualified;
    }
    
    /**
     * Check individual promotion rules
     */
    async checkPromotionRules(promo, rules, bill, customer) {
        const checks = {
            eligible: true,
            reasons: [],
            failed_conditions: []
        };
        
        // Check minimum purchase
        if (rules.requirements.min_purchase > 0) {
            if (bill.subtotal < rules.requirements.min_purchase) {
                checks.eligible = false;
                checks.reasons.push(\Minimum purchase Rp \ not met\);
                checks.failed_conditions.push('min_purchase');
            }
        }
        
        // Check minimum quantity
        if (rules.requirements.min_quantity > 0) {
            const totalQty = bill.items.reduce((sum, item) => sum + item.quantity, 0);
            if (totalQty < rules.requirements.min_quantity) {
                checks.eligible = false;
                checks.reasons.push(\Minimum \ items not met\);
                checks.failed_conditions.push('min_quantity');
            }
        }
        
        // Check product filters
        if (rules.filters.product_ids.length > 0) {
            const hasQualifyingProduct = bill.items.some(item =>
                rules.filters.product_ids.includes(item.product_id)
            );
            
            if (!hasQualifyingProduct) {
                checks.eligible = false;
                checks.reasons.push('No qualifying products in bill');
                checks.failed_conditions.push('product_filter');
            }
        }
        
        // Check category filters
        if (rules.filters.category_ids.length > 0) {
            const hasQualifyingCategory = bill.items.some(item =>
                rules.filters.category_ids.includes(item.category_id)
            );
            
            if (!hasQualifyingCategory) {
                checks.eligible = false;
                checks.reasons.push('No qualifying categories in bill');
                checks.failed_conditions.push('category_filter');
            }
        }
        
        // Check channel
        if (rules.eligibility.channels.length > 0) {
            if (!rules.eligibility.channels.includes(bill.channel)) {
                checks.eligible = false;
                checks.reasons.push(\Channel '\' not eligible\);
                checks.failed_conditions.push('channel');
            }
        }
        
        // Check member tier
        if (rules.eligibility.member_tiers.length > 0 && customer.member_id) {
            if (!rules.eligibility.member_tiers.includes(customer.member_tier)) {
                checks.eligible = false;
                checks.reasons.push(\Member tier '\' not eligible\);
                checks.failed_conditions.push('member_tier');
            }
        }
        
        return checks;
    }
    
    /**
     * Resolve conflicts and select best promotions
     */
    resolveConflicts(qualified) {
        // Group by execution stage
        const stages = {
            'item_level': [],
            'subtotal': [],
            'payment': [],
            'post_payment': []
        };
        
        for (const q of qualified) {
            const stage = q.promotion.execution_stage;
            stages[stage].push(q);
        }
        
        const selected = [];
        const appliedIds = new Set();
        
        // Process each stage
        for (const stage of ['item_level', 'subtotal', 'payment', 'post_payment']) {
            for (const q of stages[stage]) {
                const promo = q.promotion;
                
                // Check if conflicts with already applied
                const cannotCombine = JSON.parse(promo.cannot_combine_with || '[]');
                const hasConflict = cannotCombine.some(id => appliedIds.has(id));
                
                if (hasConflict) {
                    continue; // Skip conflicting promo
                }
                
                // Check if stackable
                if (!promo.is_stackable && appliedIds.size > 0 && stage === stages[stage][0].promotion.execution_stage) {
                    // If not stackable and already have promo in this stage, skip
                    if (selected.some(s => s.promotion.execution_stage === stage)) {
                        continue;
                    }
                }
                
                selected.push(q);
                appliedIds.add(promo.id);
            }
        }
        
        return selected;
    }
    
    /**
     * Calculate discounts for selected promotions
     */
    async calculateDiscounts(promotions, bill, customer, payment) {
        const applied = [];
        const skipped = [];
        let totalDiscount = 0;
        
        for (const q of promotions) {
            const promo = q.promotion;
            const rules = q.rules;
            
            let result;
            
            // Call type-specific calculator
            switch (promo.promo_type) {
                case 'percent_discount':
                    result = this.calculatePercentDiscount(bill, rules);
                    break;
                    
                case 'amount_discount':
                    result = this.calculateAmountDiscount(bill, rules);
                    break;
                    
                case 'buy_x_get_y':
                    result = this.calculateBOGO(bill, rules);
                    break;
                    
                case 'combo':
                    result = this.calculateCombo(bill, rules);
                    break;
                    
                case 'free_item':
                    result = this.calculateFreeItem(bill, rules);
                    break;
                    
                case 'happy_hour':
                    result = this.calculateHappyHour(bill, rules);
                    break;
                    
                case 'cashback':
                    if (payment) {
                        result = this.calculateCashback(bill, rules, payment.method);
                    } else {
                        result = { status: 'skipped', reason: 'Payment info not available', cashback: 0 };
                    }
                    break;
                    
                case 'payment_discount':
                    if (payment) {
                        result = this.calculatePaymentPromo(bill, rules, payment.method);
                    } else {
                        result = { status: 'skipped', reason: 'Payment info not available', discount: 0 };
                    }
                    break;
                    
                case 'package':
                    result = this.calculatePackage(bill, rules);
                    break;
                    
                case 'mix_match':
                    result = this.calculateMixMatch(bill, rules);
                    break;
                    
                case 'upsell':
                    result = this.calculateUpsell(bill, rules);
                    break;
                    
                case 'threshold_tier':
                    result = this.calculateTiered(bill, rules);
                    break;
                    
                default:
                    result = { status: 'failed', reason: `Unsupported promo type: ${promo.promo_type}`, discount: 0 };
            }
            
            if (result.status === 'applied') {
                applied.push({
                    promotion_id: promo.id,
                    promotion_code: promo.code,
                    promotion_name: promo.name,
                    discount: result.discount,
                    reason: result.reason,
                    details: result
                });
                totalDiscount += result.discount;
            } else {
                skipped.push({
                    promotion_id: promo.id,
                    promotion_code: promo.code,
                    promotion_name: promo.name,
                    status: result.status,
                    reason: result.reason
                });
            }
        }
        
        return {
            applied,
            skipped,
            total_discount: totalDiscount,
            logs: [...applied, ...skipped]
        };
    }
    
    /**
     * Create audit logs
     */
    async createLogs(billId, results) {
        const logs = [];
        
        for (const promo of results.applied) {
            logs.push({
                id: generateUUID(),
                bill_id: billId,
                promotion_id: promo.promotion_id,
                promotion_code: promo.promotion_code,
                status: 'applied',
                reason: promo.reason,
                original_amount: promo.details.original || 0,
                discount_amount: promo.discount,
                final_amount: promo.details.final || 0,
                validation_details: JSON.stringify(promo.details),
                evaluated_at: new Date().toISOString()
            });
        }
        
        for (const promo of results.skipped) {
            logs.push({
                id: generateUUID(),
                bill_id: billId,
                promotion_id: promo.promotion_id,
                promotion_code: promo.promotion_code,
                status: promo.status,
                reason: promo.reason,
                original_amount: 0,
                discount_amount: 0,
                final_amount: 0,
                validation_details: JSON.stringify({}),
                evaluated_at: new Date().toISOString()
            });
        }
        
        // Batch insert
        await this.db.insertBatch('promotion_log_local', logs);
        
        return logs;
    }
    
    // Type-specific calculators (implement based on examples above)
    calculatePercentDiscount(bill, rules) { /* See section 1 */ }
    calculateAmountDiscount(bill, rules) { /* See section 2 */ }
    calculateBOGO(bill, rules) { /* See section 3 */ }
    calculateCombo(bill, rules) { /* See section 8 */ }
    calculateFreeItem(bill, rules) { /* See section 9 */ }
    calculateHappyHour(bill, rules) { /* See section 6 */ }
    calculateCashback(bill, rules, paymentMethod) { /* See section 10 */ }
    calculatePaymentPromo(bill, rules, paymentMethod) { /* See section 7 */ }
    calculatePackage(bill, rules) { /* See section 4 */ }
    calculateMixMatch(bill, rules) { /* See section 11 */ }
    calculateUpsell(bill, rules) { /* See section 12 */ }
    calculateTiered(bill, rules) { /* See section 5 */ }
}

// Usage
const engine = new PromotionEngine(database);

const bill = {
    id: 'bill-uuid-123',
    store_id: 'store-uuid-abc',
    channel: 'dine_in',
    items: [
        { id: 'item-1', product_id: 'prod-1', category_id: 'cat-1', quantity: 2, price: 25000 },
        { id: 'item-2', product_id: 'prod-2', category_id: 'cat-2', quantity: 1, price: 30000 }
    ],
    subtotal: 80000,
    tax: 8000,
    service: 4000,
    total: 92000
};

const customer = {
    member_id: 'member-uuid-xyz',
    member_tier: 'gold',
    first_order: false
};

const payment = {
    method: 'gopay',
    amount: 92000
};

const result = await engine.evaluate(bill, customer, payment);

console.log(\Applied \ promotions\);
console.log(\Total Discount: Rp \\);
console.log(\Final Total: Rp \\);
console.log(\Execution Time: \ms\);
```

---

## ⚡ Performance Optimization

### **1. Database Indexing**

```sql
-- Critical indexes for fast queries
CREATE INDEX idx_promo_lookup ON promotion_cache(
    store_id, is_active, valid_from, valid_until
);

CREATE INDEX idx_promo_priority ON promotion_cache(
    priority DESC, execution_priority ASC
);

CREATE INDEX idx_promo_type_stage ON promotion_cache(
    promo_type, execution_stage
);

-- For voucher lookup
CREATE INDEX idx_voucher_lookup ON voucher_cache(
    code, status, expires_at
);
```

### **2. Caching Strategy**

```javascript
class PromotionCache {
    constructor() {
        this.cache = new Map();
        this.ttl = 300000; // 5 minutes
    }
    
    /**
     * Get promotions with in-memory cache
     */
    async getPromotions(storeId) {
        const cacheKey = \promos_\\;
        const cached = this.cache.get(cacheKey);
        
        if (cached && Date.now() - cached.timestamp < this.ttl) {
            return cached.data;
        }
        
        // Load from database
        const promotions = await this.loadFromDatabase(storeId);
        
        // Cache it
        this.cache.set(cacheKey, {
            data: promotions,
            timestamp: Date.now()
        });
        
        return promotions;
    }
    
    /**
     * Invalidate cache when sync happens
     */
    invalidate(storeId) {
        const cacheKey = \promos_\\;
        this.cache.delete(cacheKey);
    }
}
```

### **3. Query Optimization**

**❌ BAD (N+1 Query):**
```javascript
for (const promo of promotions) {
    const rules = await db.get('SELECT promotion_data FROM promotion_cache WHERE id = ?', promo.id);
    // Process rules...
}
```

**✅ GOOD (Batch Load):**
```javascript
// All data already in promotion_cache, no additional queries needed
const promotions = await db.all('SELECT * FROM promotion_cache WHERE ...');
for (const promo of promotions) {
    const rules = JSON.parse(promo.promotion_data); // Already loaded
    // Process rules...
}
```

### **4. Pre-computation**

**Store pre-computed values in promotion_data:**
```json
{
  \"rules\": {
    \"_precomputed\": {
      \"has_product_filter\": true,
      \"has_category_filter\": false,
      \"requires_member\": false,
      \"quick_check_flags\": 0b101010
    },
    \"discount\": { ... }
  }
}
```

**Fast eligibility check:**
```javascript
function quickCheck(promo, bill) {
    const precomputed = promo.rules._precomputed;
    
    // Bit flag checks (very fast)
    if (precomputed.quick_check_flags & FLAG_HAS_PRODUCT_FILTER) {
        // Do product filter check
    }
    
    if (precomputed.quick_check_flags & FLAG_REQUIRES_MEMBER) {
        if (!bill.customer.member_id) return false;
    }
    
    return true;
}
```

### **5. Execution Time Budget**

```javascript
class PromotionEngine {
    constructor(database, options = {}) {
        this.db = database;
        this.maxExecutionTime = options.maxExecutionTime || 100; // 100ms budget
        this.startTime = null;
    }
    
    async evaluate(bill, customer, payment) {
        this.startTime = Date.now();
        
        // Fast pre-screening with time check
        const eligible = [];
        for (const promo of promotions) {
            if (this.isTimeoutReached()) {
                console.warn('Promotion evaluation timeout, stopping early');
                break;
            }
            
            if (this.quickCheck(promo, bill)) {
                eligible.push(promo);
            }
        }
        
        // Continue with detailed evaluation...
    }
    
    isTimeoutReached() {
        return (Date.now() - this.startTime) > this.maxExecutionTime;
    }
}
```

---

## 🚨 Error Handling

### **1. Graceful Degradation**

```javascript
async function evaluatePromotions(bill, customer) {
    try {
        const engine = new PromotionEngine(db);
        return await engine.evaluate(bill, customer);
    } catch (error) {
        console.error('Promotion engine error:', error);
        
        // Log error but don't block checkout
        await logError({
            type: 'promotion_engine_error',
            bill_id: bill.id,
            error: error.message,
            stack: error.stack
        });
        
        // Return safe default (no promotions applied)
        return {
            applied: [],
            skipped: [],
            total_discount: 0,
            error: 'Promotion evaluation failed',
            can_proceed: true // Allow checkout without promotions
        };
    }
}
```

### **2. Validation Before Calculation**

```javascript
function validateBillDraft(bill) {
    const errors = [];
    
    if (!bill.id) errors.push('Bill ID required');
    if (!bill.store_id) errors.push('Store ID required');
    if (!Array.isArray(bill.items)) errors.push('Bill items must be array');
    if (bill.items.length === 0) errors.push('Bill has no items');
    if (typeof bill.subtotal !== 'number') errors.push('Invalid subtotal');
    if (bill.subtotal < 0) errors.push('Subtotal cannot be negative');
    
    if (errors.length > 0) {
        throw new ValidationError('Invalid bill draft', errors);
    }
}
```

### **3. Promotion Data Integrity**

```javascript
function validatePromotionData(promo) {
    try {
        const rules = JSON.parse(promo.promotion_data);
        
        // Validate structure
        if (!rules.discount) {
            throw new Error('Missing discount rules');
        }
        
        if (!rules.requirements) {
            throw new Error('Missing requirements');
        }
        
        return rules;
    } catch (error) {
        console.error(\Invalid promotion data for \:\, error);
        
        // Mark as failed
        return null;
    }
}
```

### **4. Conflict Detection**

```javascript
function detectCircularConflicts(promotions) {
    // Check for circular cannot_combine_with references
    const conflicts = new Map();
    
    for (const promo of promotions) {
        const cannotCombine = JSON.parse(promo.cannot_combine_with || '[]');
        conflicts.set(promo.id, cannotCombine);
    }
    
    // Detect cycles
    for (const [id, conflictIds] of conflicts.entries()) {
        for (const conflictId of conflictIds) {
            const reverseConflicts = conflicts.get(conflictId) || [];
            if (reverseConflicts.includes(id)) {
                console.warn(\Circular conflict detected: \ <-> \\);
            }
        }
    }
}
```

---

## 🧪 Testing Scenarios

### **Scenario 1: Simple Percent Discount**

```javascript
// Test: 10% discount, min purchase 50k, max cap 50k
const testBill = {
    id: 'test-1',
    store_id: 'store-1',
    items: [{ product_id: 'p1', price: 100000, quantity: 1 }],
    subtotal: 100000,
    total: 100000
};

const expected = {
    discount: 10000, // 10% of 100k
    final_total: 90000
};

// Test execution
const result = await engine.evaluate(testBill, {});
assert.equal(result.total_discount, expected.discount);
```

### **Scenario 2: BOGO with Partial Quantity**

```javascript
// Test: Buy 2 Get 1 Free
// Bill: 5 burgers
// Expected: 2 free burgers (floor(5/2) = 2)

const testBill = {
    id: 'test-2',
    items: [
        { product_id: 'burger', price: 25000, quantity: 5 }
    ],
    subtotal: 125000
};

const result = await engine.evaluate(testBill, {});

assert.equal(result.applied[0].details.free_items, 2);
assert.equal(result.total_discount, 50000); // 2 × 25k
```

### **Scenario 3: Tiered Promotion Edge Cases**

```javascript
// Test: Exactly at tier boundary
// Tier 1: 100k-199k → 10k off
// Tier 2: 200k-299k → 25k off

// Case A: Subtotal = 199,999 (Tier 1)
let result = await engine.evaluate({ subtotal: 199999 }, {});
assert.equal(result.total_discount, 10000);

// Case B: Subtotal = 200,000 (Tier 2)
result = await engine.evaluate({ subtotal: 200000 }, {});
assert.equal(result.total_discount, 25000);
```

### **Scenario 4: Stacking Rules**

```javascript
// Test: Two stackable promotions
// Promo A: 10% off (stackable)
// Promo B: Rp 5k off (stackable)

const testBill = { subtotal: 100000 };

const result = await engine.evaluate(testBill, {});

// Both should apply
assert.equal(result.applied.length, 2);
assert.equal(result.total_discount, 15000); // 10k + 5k
```

### **Scenario 5: Conflict Resolution**

```javascript
// Test: Cannot combine
// Promo A: 20% off (cannot combine with B)
// Promo B: Rp 25k off (cannot combine with A)
// Priority: A > B

const result = await engine.evaluate(testBill, {});

// Only Promo A should apply (higher priority)
assert.equal(result.applied.length, 1);
assert.equal(result.applied[0].promotion_code, 'PROMO_A');
assert.equal(result.skipped.length, 1);
assert.include(result.skipped[0].reason, 'conflict');
```

### **Scenario 6: Time-based Eligibility**

```javascript
// Test: Happy Hour 14:00-17:00
// Current time: 15:30 (eligible)

const mockNow = new Date('2026-01-26T15:30:00');
const result = await engine.evaluate(testBill, {}, null, mockNow);

assert.equal(result.applied.length, 1);
assert.include(result.applied[0].reason, 'Happy hour');

// Test: Current time: 18:00 (not eligible)
const mockNow2 = new Date('2026-01-26T18:00:00');
const result2 = await engine.evaluate(testBill, {}, null, mockNow2);

assert.equal(result2.applied.length, 0);
assert.include(result2.skipped[0].reason, 'only valid between');
```

### **Scenario 7: Package with Modifications**

```javascript
// Test: Package allows modification
// Package: Nasi + Choice of Ayam + Choice of Drink = 35k
// Customer picks: Ayam Goreng, Es Teh

const selectedItems = [
    { product_id: 'nasi', quantity: 1 },
    { product_id: 'ayam-goreng', category_id: 'ayam', quantity: 1 },
    { product_id: 'es-teh', category_id: 'drinks', quantity: 1 }
];

const result = await engine.calculatePackage(selectedItems, promotion);

assert.equal(result.status, 'applied');
assert.equal(result.final, 35000);
```

### **Scenario 8: Payment Method Promo**

```javascript
// Test: 5% off for GoPay, max 20k
// Bill: 500k
// Expected: 20k discount (capped)

const result = await engine.evaluate(
    { subtotal: 500000, total: 500000 },
    {},
    { method: 'gopay', amount: 500000 }
);

assert.equal(result.total_discount, 20000); // Capped at 20k
assert.equal(result.final_total, 480000);
```

---

## 📊 Performance Benchmarks

### **Target Performance**

| Metric | Target | Acceptable | Warning |
|--------|--------|------------|---------|
| Evaluation Time | < 50ms | < 100ms | > 100ms |
| Database Query | < 10ms | < 20ms | > 50ms |
| Memory Usage | < 50MB | < 100MB | > 200MB |
| Promotions per Bill | 20 | 50 | 100 |

### **Benchmark Test**

```javascript
async function benchmarkEngine() {
    const iterations = 1000;
    const times = [];
    
    for (let i = 0; i < iterations; i++) {
        const start = Date.now();
        await engine.evaluate(sampleBill, sampleCustomer);
        const duration = Date.now() - start;
        times.push(duration);
    }
    
    const avg = times.reduce((a, b) => a + b) / times.length;
    const max = Math.max(...times);
    const min = Math.min(...times);
    const p95 = times.sort((a, b) => a - b)[Math.floor(times.length * 0.95)];
    
    console.log(\Benchmark Results (\ iterations):\);
    console.log(\  Average: \ms\);
    console.log(\  Min: \ms\);
    console.log(\  Max: \ms\);
    console.log(\  P95: \ms\);
    
    if (p95 > 100) {
        console.warn('⚠️  P95 exceeds 100ms target!');
    } else {
        console.log('✅ Performance within target');
    }
}
```

---

## 🔄 Sync Back to HO

### **Usage Tracking Sync**

```javascript
async function syncUsageToHO() {
    // Get unsent logs
    const logs = await db.all(\
        SELECT * FROM promotion_log_local
        WHERE synced_to_ho = 0
        AND status = 'applied'
        LIMIT 100
    \);
    
    if (logs.length === 0) return;
    
    try {
        // Batch send to HO
        const response = await fetch('https://ho.example.com/api/promotions/usage/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': \Bearer \\
            },
            body: JSON.stringify({
                store_id: storeId,
                logs: logs.map(log => ({
                    promotion_id: log.promotion_id,
                    promotion_code: log.promotion_code,
                    bill_id: log.bill_id,
                    discount_amount: log.discount_amount,
                    evaluated_at: log.evaluated_at
                }))
            })
        });
        
        if (response.ok) {
            // Mark as synced
            const logIds = logs.map(l => l.id);
            await db.run(\
                UPDATE promotion_log_local
                SET synced_to_ho = 1
                WHERE id IN (\)\,
                logIds
            );
            
            console.log(\Synced \ promotion logs to HO\);
        }
    } catch (error) {
        console.error('Failed to sync logs to HO:', error);
        // Will retry next time
    }
}

// Run every 5 minutes
setInterval(syncUsageToHO, 5 * 60 * 1000);
```

---

## 📚 Summary & Best Practices

### **✅ DO:**
1. **Cache promotions** in memory for fast access
2. **Index database** properly for fast queries
3. **Validate inputs** before processing
4. **Log everything** for debugging and analytics
5. **Handle errors gracefully** - don't block checkout
6. **Set time budgets** for evaluation
7. **Batch sync** logs to HO
8. **Test edge cases** thoroughly

### **❌ DON'T:**
1. **Don't query database** inside loops (N+1)
2. **Don't trust JSON data** without validation
3. **Don't block UI** for promotion calculation
4. **Don't over-discount** - validate total
5. **Don't ignore conflicts** - resolve properly
6. **Don't skip logging** - explainability is critical
7. **Don't sync in real-time** - batch for efficiency

### **🎯 Key Metrics to Monitor:**
- Evaluation time (P50, P95, P99)
- Applied vs Skipped ratio
- Discount amount distribution
- Error rate
- Sync success rate
- Database query time

---

## 📞 Support & Troubleshooting

### **Common Issues:**

**Issue 1: Promotion not applying**
- Check: promotion_cache has latest version
- Check: valid_from, valid_until dates
- Check: valid_days includes today
- Check: min_purchase requirement
- Check: promotion_log_local for skip reason

**Issue 2: Wrong discount calculated**
- Check: promotion_data JSON is valid
- Check: max_cap logic applied
- Check: execution_stage order
- Check: conflict resolution logic

**Issue 3: Slow evaluation**
- Check: Number of active promotions
- Check: Database indexes
- Check: In-memory cache working
- Check: Complex product filters

---

**END OF DOCUMENTATION**

**Version:** 1.0  
**Last Updated:** 2026-01-26  
**Maintained By:** Development Team
