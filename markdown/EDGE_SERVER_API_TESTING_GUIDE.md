# 🚀 Edge Server API Testing Guide

Panduan lengkap untuk testing semua API yang akan di-hit dari Edge Server.

Berdasarkan dashboard di: **http://localhost:8002/promotions/compiler/**

---

## 📋 Daftar Lengkap API untuk Edge Server

### **Base URL:** `http://localhost:8002/api/v1/sync/`

| # | Endpoint | Method | Purpose | Frequency |
|---|----------|--------|---------|-----------|
| 1 | `/api/v1/sync/promotions/` | GET | Download promotion rules | Every 6 hours |
| 2 | `/api/v1/sync/categories/` | GET | Download product categories | Daily |
| 3 | `/api/v1/sync/products/` | GET | Download product catalog | Daily |
| 4 | `/api/v1/sync/version/` | GET | Check if sync needed | Every sync |
| 5 | `/api/v1/sync/usage/` | POST | Upload promotion usage | Every 5 mins |

---

## 🔑 Authentication Setup

### Step 1: Get Your API Token

```bash
# Method 1: JWT Token (Recommended for Edge Server)
curl -X POST http://localhost:8002/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin"
  }'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Save the `access` token** - gunakan untuk semua request!

### Step 2: Get Your Store/Company IDs

Buka browser ke: http://localhost:8002/promotions/compiler/

Di bagian **"Edge Server Sync"** akan terlihat:
- Company ID
- Store ID
- Brand ID

Atau via Django shell:
```bash
python manage.py shell
```

```python
from core.models import Company, Brand, Store

# Get IDs
company = Company.objects.first()
print(f"Company ID: {company.id}")

brand = Brand.objects.first()
print(f"Brand ID: {brand.id}")

store = Store.objects.first()
print(f"Store ID: {store.id}")
```

---

## 🧪 Testing Setiap Endpoint

### 1️⃣ Check Version (Lightest - Always First!)

**Purpose:** Cek apakah ada perubahan data sebelum full sync.

```bash
curl -X GET "http://localhost:8002/api/v1/sync/version/?company_id=YOUR_COMPANY_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "version": 1738045842,
  "last_updated": "2026-01-27T09:10:42.123456Z",
  "force_update": false
}
```

**Testing Checklist:**
- ✅ Returns version number
- ✅ Returns last_updated timestamp
- ✅ Status code 200

**Edge Server Logic:**
```python
# Store last known version
if new_version > stored_version:
    # Trigger full sync
    sync_all_data()
else:
    # Skip sync - no changes
    pass
```

---

### 2️⃣ Sync Promotions (Most Important!)

**Purpose:** Download compiled promotion rules untuk POS engine.

#### Test A: Full Sync (First Time)

```bash
curl -X GET "http://localhost:8002/api/v1/sync/promotions/?store_id=YOUR_STORE_ID&company_id=YOUR_COMPANY_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq
```

**Expected Response:**
```json
{
  "promotions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "code": "WEEKEND20",
      "name": "Weekend Special 20% Off",
      "discount_type": "percent",
      "discount_value": 20.0,
      "start_date": "2026-01-20",
      "end_date": "2026-02-05",
      "execution_priority": 10,
      "scope": {
        "apply_to": "all_products",
        "stores": ["all"],
        "categories": [],
        "products": []
      },
      "time_rules": {
        "days_of_week": [1, 2, 3, 4, 5, 6, 7],
        "time_start": null,
        "time_end": null
      },
      "rules": {
        "min_quantity": 1,
        "min_amount": null,
        "max_discount": null
      },
      "limits": {
        "usage_limit_per_transaction": null,
        "usage_limit_per_customer": null,
        "total_usage_limit": 1000
      }
    }
  ],
  "deleted_ids": [],
  "sync_timestamp": "2026-01-27T09:10:42.123456Z",
  "total": 15,
  "total_available": 20,
  "settings": {
    "strategy": "include_future",
    "future_days": 7,
    "past_days": 1,
    "max_promotions": 100
  },
  "store": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "code": "YGY-001-BSD",
    "name": "Cabang BSD"
  }
}
```

#### Test B: Incremental Sync (Updates Only)

```bash
# Save timestamp from previous sync
LAST_SYNC="2026-01-27T09:10:42Z"

curl -X GET "http://localhost:8002/api/v1/sync/promotions/?store_id=YOUR_STORE_ID&company_id=YOUR_COMPANY_ID&updated_since=$LAST_SYNC" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq
```

**Expected:** Only promotions updated after `updated_since` timestamp.

#### Test C: Filter by Brand

```bash
curl -X GET "http://localhost:8002/api/v1/sync/promotions/?store_id=YOUR_STORE_ID&company_id=YOUR_COMPANY_ID&brand_id=YOUR_BRAND_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq
```

**Testing Checklist:**
- ✅ Returns compiled JSON (ready for POS engine)
- ✅ Includes all relevant promotions
- ✅ Respects sync strategy settings
- ✅ Status code 200
- ✅ Response time < 2 seconds

---

### 3️⃣ Sync Categories

**Purpose:** Download product categories untuk menampilkan menu.

```bash
curl -X GET "http://localhost:8002/api/v1/sync/categories/?company_id=YOUR_COMPANY_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq
```

**With Brand Filter:**
```bash
curl -X GET "http://localhost:8002/api/v1/sync/categories/?company_id=YOUR_COMPANY_ID&brand_id=YOUR_BRAND_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq
```

**Expected Response:**
```json
{
  "categories": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440010",
      "company_id": "550e8400-e29b-41d4-a716-446655440000",
      "brand_id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Main Course",
      "code": "MAIN",
      "parent_id": null,
      "is_active": true,
      "display_order": 1,
      "image_url": "https://example.com/categories/main.jpg",
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-27T09:00:00Z"
    }
  ],
  "deleted_ids": [],
  "sync_timestamp": "2026-01-27T09:10:42.123456Z",
  "total": 10
}
```

**Testing Checklist:**
- ✅ Returns all active categories
- ✅ Includes parent-child relationships
- ✅ Response time < 500ms

---

### 4️⃣ Sync Products

**Purpose:** Download product catalog dengan harga.

```bash
curl -X GET "http://localhost:8002/api/v1/sync/products/?company_id=YOUR_COMPANY_ID&brand_id=YOUR_BRAND_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq
```

**With Store Filter:**
```bash
curl -X GET "http://localhost:8002/api/v1/sync/products/?company_id=YOUR_COMPANY_ID&brand_id=YOUR_BRAND_ID&store_id=YOUR_STORE_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq
```

**Expected Response:**
```json
{
  "products": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440020",
      "company_id": "550e8400-e29b-41d4-a716-446655440000",
      "brand_id": "550e8400-e29b-41d4-a716-446655440001",
      "store_id": null,
      "category_id": "550e8400-e29b-41d4-a716-446655440010",
      "name": "Nasi Goreng Special",
      "sku": "NGS-001",
      "price": "25000.00",
      "cost": "15000.00",
      "is_active": true,
      "has_modifiers": true,
      "image_url": "https://example.com/products/ngs.jpg",
      "description": "Nasi goreng dengan telur dan ayam",
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-27T09:00:00Z"
    }
  ],
  "deleted_ids": [],
  "sync_timestamp": "2026-01-27T09:10:42.123456Z",
  "total": 50
}
```

**Testing Checklist:**
- ✅ Returns all active products
- ✅ Includes pricing information
- ✅ Includes category relationships
- ✅ Response time < 1 second

---

### 5️⃣ Upload Usage (POS → HO)

**Purpose:** Upload promotion usage logs dari POS ke HO.

```bash
curl -X POST http://localhost:8002/api/v1/sync/usage/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "usages": [
      {
        "promotion_id": "550e8400-e29b-41d4-a716-446655440000",
        "bill_id": "B20260127-001",
        "discount_amount": 15000.0,
        "used_at": "2026-01-27T10:30:00Z",
        "store_id": "YOUR_STORE_ID",
        "customer_id": null
      },
      {
        "promotion_id": "550e8400-e29b-41d4-a716-446655440000",
        "bill_id": "B20260127-002",
        "discount_amount": 20000.0,
        "used_at": "2026-01-27T10:35:00Z",
        "store_id": "YOUR_STORE_ID",
        "customer_id": "550e8400-e29b-41d4-a716-446655440010"
      }
    ]
  }'
```

**Expected Response:**
```json
{
  "created": 2,
  "errors": [],
  "total": 2
}
```

**Testing Checklist:**
- ✅ Accepts batch upload
- ✅ Returns success count
- ✅ Returns errors for invalid data
- ✅ Response time < 500ms

---

## 🔄 Complete Sync Flow (Edge Server Simulation)

### Initial Sync (First Time POS Starts)

```bash
#!/bin/bash
# save as: edge_server_initial_sync.sh

BASE_URL="http://localhost:8002"
TOKEN="YOUR_JWT_TOKEN"
COMPANY_ID="YOUR_COMPANY_ID"
BRAND_ID="YOUR_BRAND_ID"
STORE_ID="YOUR_STORE_ID"

echo "🚀 Edge Server Initial Sync"
echo "=========================="

# 1. Check version
echo "1. Checking version..."
VERSION=$(curl -s -X GET "$BASE_URL/api/v1/sync/version/?company_id=$COMPANY_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.version')
echo "   Version: $VERSION"

# 2. Sync categories
echo "2. Syncing categories..."
CATEGORIES=$(curl -s -X GET "$BASE_URL/api/v1/sync/categories/?company_id=$COMPANY_ID&brand_id=$BRAND_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.total')
echo "   Downloaded: $CATEGORIES categories"

# 3. Sync products
echo "3. Syncing products..."
PRODUCTS=$(curl -s -X GET "$BASE_URL/api/v1/sync/products/?company_id=$COMPANY_ID&brand_id=$BRAND_ID&store_id=$STORE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.total')
echo "   Downloaded: $PRODUCTS products"

# 4. Sync promotions
echo "4. Syncing promotions..."
PROMOTIONS=$(curl -s -X GET "$BASE_URL/api/v1/sync/promotions/?store_id=$STORE_ID&company_id=$COMPANY_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.total')
echo "   Downloaded: $PROMOTIONS promotions"

echo ""
echo "✅ Initial sync complete!"
echo "   Categories: $CATEGORIES"
echo "   Products: $PRODUCTS"
echo "   Promotions: $PROMOTIONS"
echo "   Version: $VERSION"
```

### Periodic Sync (Every 6 Hours)

```bash
#!/bin/bash
# save as: edge_server_periodic_sync.sh

BASE_URL="http://localhost:8002"
TOKEN="YOUR_JWT_TOKEN"
COMPANY_ID="YOUR_COMPANY_ID"
STORE_ID="YOUR_STORE_ID"
STORED_VERSION="1738045842"  # From previous sync

echo "🔄 Edge Server Periodic Sync"
echo "============================"

# 1. Check version
echo "1. Checking for updates..."
RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/sync/version/?company_id=$COMPANY_ID" \
  -H "Authorization: Bearer $TOKEN")

NEW_VERSION=$(echo $RESPONSE | jq -r '.version')
echo "   Stored version: $STORED_VERSION"
echo "   New version: $NEW_VERSION"

# 2. Compare versions
if [ "$NEW_VERSION" -gt "$STORED_VERSION" ]; then
    echo "   ⚡ Updates available! Syncing..."
    
    # Get last sync timestamp
    LAST_SYNC=$(date -u -d "6 hours ago" +"%Y-%m-%dT%H:%M:%SZ")
    
    # Incremental sync
    PROMOTIONS=$(curl -s -X GET "$BASE_URL/api/v1/sync/promotions/?store_id=$STORE_ID&company_id=$COMPANY_ID&updated_since=$LAST_SYNC" \
      -H "Authorization: Bearer $TOKEN" | jq -r '.total')
    
    echo "   Updated promotions: $PROMOTIONS"
    echo "   ✅ Sync complete!"
else
    echo "   ✅ No updates needed. Skipping sync."
fi
```

### Usage Upload (Every 5 Minutes)

```bash
#!/bin/bash
# save as: edge_server_upload_usage.sh

BASE_URL="http://localhost:8002"
TOKEN="YOUR_JWT_TOKEN"
STORE_ID="YOUR_STORE_ID"

echo "📤 Uploading promotion usage logs"
echo "================================="

# Read from local queue (example)
USAGE_DATA=$(cat <<EOF
{
  "usages": [
    {
      "promotion_id": "550e8400-e29b-41d4-a716-446655440000",
      "bill_id": "B20260127-001",
      "discount_amount": 15000.0,
      "used_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
      "store_id": "$STORE_ID",
      "customer_id": null
    }
  ]
}
EOF
)

# Upload
RESULT=$(curl -s -X POST "$BASE_URL/api/v1/sync/usage/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$USAGE_DATA")

CREATED=$(echo $RESULT | jq -r '.created')
ERRORS=$(echo $RESULT | jq -r '.errors | length')

echo "✅ Upload complete!"
echo "   Created: $CREATED"
echo "   Errors: $ERRORS"
```

---

## 🧪 Postman Collection

### Import ke Postman

1. Import file: `SYNC_API_POSTMAN_COLLECTION.json`
2. Setup Environment:
   - `base_url` = `http://localhost:8002`
   - `token` = (get from `/api/token/`)
   - `company_id` = (your company UUID)
   - `brand_id` = (your brand UUID)
   - `store_id` = (your store UUID)

### Test Runner

1. Klik "Run Collection"
2. Select all requests
3. Klik "Run"
4. Review results

---

## 🐛 Troubleshooting

### Error: "Authentication credentials were not provided"

**Problem:** Token tidak valid atau tidak di-include.

**Solution:**
```bash
# Get fresh token
curl -X POST http://localhost:8002/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Use Bearer (not Token) for JWT
-H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Error: "Store not found"

**Problem:** Store ID atau Company ID salah.

**Solution:**
```bash
# Get correct IDs
python manage.py shell
>>> from core.models import Store
>>> store = Store.objects.first()
>>> print(f"Store ID: {store.id}")
>>> print(f"Company ID: {store.brand.company.id}")
```

### Error: Empty promotions array

**Problem:** Tidak ada promosi yang match dengan filter.

**Solution:**
```bash
# Check sync settings
python manage.py shell
>>> from promotions.models_settings import PromotionSyncSettings
>>> settings = PromotionSyncSettings.objects.first()
>>> print(f"Strategy: {settings.sync_strategy}")
>>> print(f"Future days: {settings.future_days}")

# Create test promotions
python create_promotion_samples.py
```

### Slow Response (> 5 seconds)

**Possible Causes:**
- Too many promotions (check `max_promotions_per_sync`)
- Database not indexed
- Network latency

**Solution:**
```bash
# Adjust sync settings
python manage.py shell
>>> from promotions.models_settings import PromotionSyncSettings
>>> settings = PromotionSyncSettings.objects.first()
>>> settings.max_promotions_per_sync = 50  # Reduce limit
>>> settings.save()
```

---

## 📊 Performance Benchmarks

| Endpoint | Expected Time | Acceptable Time | Max Time |
|----------|--------------|----------------|----------|
| `/version/` | < 50ms | < 100ms | 200ms |
| `/categories/` | < 200ms | < 500ms | 1s |
| `/products/` | < 500ms | < 1s | 2s |
| `/promotions/` | < 1s | < 2s | 5s |
| `/usage/` (POST) | < 300ms | < 500ms | 1s |

---

## ✅ Testing Checklist

### Before Production

- [ ] All 5 endpoints tested successfully
- [ ] Authentication working
- [ ] Incremental sync working
- [ ] Batch upload working
- [ ] Error handling verified
- [ ] Response times acceptable
- [ ] Network retry logic implemented
- [ ] Local storage/queue implemented

### Edge Server Requirements

- [ ] Store promotions in local SQLite
- [ ] Cache categories and products
- [ ] Queue usage logs for batch upload
- [ ] Implement retry with exponential backoff
- [ ] Handle network failures gracefully
- [ ] Log all sync operations

---

## 📞 Quick Reference

**Base URL:** `http://localhost:8002/api/v1/sync/`

**Get Token:**
```bash
curl -X POST http://localhost:8002/api/token/ -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}'
```

**Headers untuk semua request:**
```
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json  (for POST)
```

**Dashboard:** http://localhost:8002/promotions/compiler/

**Full Docs:** `SYNC_API_DOCUMENTATION.md`

---

**Happy Testing! 🚀**
