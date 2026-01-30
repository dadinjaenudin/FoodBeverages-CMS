# 🚀 Complete Edge Server API Guide

**Dokumentasi lengkap semua API yang dibutuhkan Edge Server**

Dashboard: http://localhost:8002/promotions/compiler/

---

## 📋 Overview: 2 Set API untuk Edge Server

### 1. **Promotion Sync API** (`/api/v1/sync/`)
Specialized API untuk promotion dengan compilation engine

### 2. **Master Data REST API** (`/api/v1/`)
Standard REST API untuk semua master data (Company, Brand, Store, Products, Categories, dll)

---

## 🎯 Complete API List for Edge Server

| Category | Endpoint | Method | Purpose |
|----------|----------|--------|---------|
| **🔐 Authentication** |
| Token | `/api/token/` | POST | Get JWT token |
| Refresh | `/api/token/refresh/` | POST | Refresh token |
| **🏢 Core Master Data** |
| Companies | `/api/v1/core/companies/` | GET | List companies |
| Companies Sync | `/api/v1/core/companies/sync/` | GET | Sync companies |
| Brands | `/api/v1/core/brands/` | GET | List brands |
| Brands Sync | `/api/v1/core/brands/sync/` | GET | Sync brands |
| Stores | `/api/v1/core/stores/` | GET | List stores |
| Stores Sync | `/api/v1/core/stores/sync/` | GET | Sync stores |
| Users | `/api/v1/core/users/` | GET | List users |
| Users Sync | `/api/v1/core/users/sync/` | GET | Sync users |
| **🍔 Product Master Data** |
| Categories | `/api/v1/products/categories/` | GET | List categories |
| Categories Sync | `/api/v1/products/categories/sync/` | GET | Sync categories |
| Products | `/api/v1/products/products/` | GET | List products |
| Products Sync | `/api/v1/products/products/sync/` | GET | Sync products |
| Modifiers | `/api/v1/products/modifiers/` | GET | List modifiers |
| Modifiers Sync | `/api/v1/products/modifiers/sync/` | GET | Sync modifiers |
| Table Areas | `/api/v1/products/table-areas/` | GET | List table areas |
| Tables | `/api/v1/products/tables/` | GET | List tables |
| Kitchen Stations | `/api/v1/products/kitchen-stations/` | GET | List kitchen stations |
| **🎁 Promotions (Specialized)** |
| Version Check | `/api/v1/sync/version/` | GET | Check promotion version |
| Sync Promotions | `/api/v1/sync/promotions/` | GET | Download compiled promotions |
| Sync Categories | `/api/v1/sync/categories/` | GET | Download categories (alternative) |
| Sync Products | `/api/v1/sync/products/` | GET | Download products (alternative) |
| Upload Usage | `/api/v1/sync/usage/` | POST | Upload promotion usage |
| **👥 Members** |
| Members | `/api/v1/members/members/` | GET | List members |
| Members Sync | `/api/v1/members/members/sync/` | GET | Sync members |
| **📦 Inventory** |
| Inventory Items | `/api/v1/inventory/items/` | GET | List inventory |
| Recipes | `/api/v1/inventory/recipes/` | GET | List recipes |
| **📤 Transactions (Edge → HO)** |
| Push Bills | `/api/v1/transactions/bills/push/` | POST | Upload transactions |
| Push Cash Drop | `/api/v1/transactions/cash-drops/push/` | POST | Upload cash drops |
| Push Sessions | `/api/v1/transactions/sessions/push/` | POST | Upload sessions |

**Total: 30+ API endpoints available!**

---

## 🔑 Authentication (Step 1)

### Get JWT Token

```bash
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

**Use `access` token** for all subsequent requests:
```bash
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🏢 Core Master Data APIs

### 1. Companies

#### List All Companies
```bash
GET /api/v1/core/companies/
```

```bash
curl -X GET http://localhost:8002/api/v1/core/companies/ \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "code": "YGY",
      "name": "Yogya Group",
      "timezone": "Asia/Jakarta",
      "is_active": true,
      "point_expiry_months": 12,
      "points_per_currency": "1.00"
    }
  ]
}
```

#### Sync Companies (Incremental)
```bash
GET /api/v1/core/companies/sync/?last_sync=2026-01-27T00:00:00Z
```

---

### 2. Brands

#### List All Brands
```bash
GET /api/v1/core/brands/
```

```bash
curl -X GET http://localhost:8002/api/v1/core/brands/ \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "count": 2,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "company": "550e8400-e29b-41d4-a716-446655440000",
      "code": "YGY-001",
      "name": "Ayam Geprek Express",
      "tax_rate": "11.00",
      "service_charge": "5.00",
      "is_active": true
    }
  ]
}
```

#### Sync Specific Brand
```bash
GET /api/v1/core/brands/sync/?brand_id={uuid}&last_sync=2026-01-27T00:00:00Z
```

```bash
curl -X GET "http://localhost:8002/api/v1/core/brands/sync/?brand_id=$BRAND_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "count": 1,
  "last_sync": "2026-01-27T10:30:00.123456Z",
  "data": [...]
}
```

---

### 3. Stores

#### List All Stores
```bash
GET /api/v1/core/stores/
```

#### Sync Specific Store
```bash
GET /api/v1/core/stores/sync/?store_id={uuid}&last_sync=2026-01-27T00:00:00Z
```

```bash
curl -X GET "http://localhost:8002/api/v1/core/stores/sync/?store_id=$STORE_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "count": 1,
  "last_sync": "2026-01-27T10:30:00Z",
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "brand": "550e8400-e29b-41d4-a716-446655440001",
      "store_code": "YGY-001-BSD",
      "store_name": "Cabang BSD",
      "address": "Jl. BSD Raya...",
      "phone": "021-12345678",
      "timezone": "Asia/Jakarta",
      "is_active": true
    }
  ]
}
```

---

### 4. Users

#### List Users for Brand
```bash
GET /api/v1/core/users/?brand={brand_id}
```

#### Sync Users for Brand
```bash
GET /api/v1/core/users/sync/?brand_id={uuid}&last_sync=2026-01-27T00:00:00Z
```

```bash
curl -X GET "http://localhost:8002/api/v1/core/users/sync/?brand_id=$BRAND_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "count": 5,
  "last_sync": "2026-01-27T10:30:00Z",
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440010",
      "username": "cashier1",
      "role": "cashier",
      "role_scope": "store",
      "pin": "123456",
      "is_active": true
    }
  ]
}
```

---

## 🍔 Product Master Data APIs

### 5. Categories

#### List All Categories
```bash
GET /api/v1/products/categories/
```

```bash
curl -X GET http://localhost:8002/api/v1/products/categories/ \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440020",
      "company": "550e8400-e29b-41d4-a716-446655440000",
      "brand": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Main Course",
      "code": "MAIN",
      "parent": null,
      "display_order": 1,
      "is_active": true
    }
  ]
}
```

#### Sync Categories
```bash
GET /api/v1/products/categories/sync/?brand_id={uuid}&last_sync=2026-01-27T00:00:00Z
```

```bash
curl -X GET "http://localhost:8002/api/v1/products/categories/sync/?brand_id=$BRAND_ID" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 6. Products

#### List All Products
```bash
GET /api/v1/products/products/?brand={brand_id}
```

```bash
curl -X GET "http://localhost:8002/api/v1/products/products/?brand=$BRAND_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "count": 50,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440030",
      "company": "550e8400-e29b-41d4-a716-446655440000",
      "brand": "550e8400-e29b-41d4-a716-446655440001",
      "category": "550e8400-e29b-41d4-a716-446655440020",
      "name": "Nasi Goreng Special",
      "sku": "NGS-001",
      "price": "25000.00",
      "cost": "15000.00",
      "is_active": true,
      "has_modifiers": true,
      "image": "/media/products/ngs.jpg"
    }
  ]
}
```

#### Sync Products
```bash
GET /api/v1/products/products/sync/?brand_id={uuid}&store_id={uuid}&last_sync=2026-01-27T00:00:00Z
```

```bash
curl -X GET "http://localhost:8002/api/v1/products/products/sync/?brand_id=$BRAND_ID&store_id=$STORE_ID" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 7. Modifiers

#### List Modifiers
```bash
GET /api/v1/products/modifiers/?brand={brand_id}
```

#### Sync Modifiers
```bash
GET /api/v1/products/modifiers/sync/?brand_id={uuid}&last_sync=2026-01-27T00:00:00Z
```

---

### 8. Table Areas

```bash
GET /api/v1/products/table-areas/?brand={brand_id}
```

---

### 9. Kitchen Stations

```bash
GET /api/v1/products/kitchen-stations/?brand={brand_id}
```

---

## 🎁 Promotion APIs (Specialized)

### 10. Check Version (Always First!)

```bash
GET /api/v1/sync/version/?company_id={uuid}
```

```bash
curl -X GET "http://localhost:8002/api/v1/sync/version/?company_id=$COMPANY_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "version": 1738045842,
  "last_updated": "2026-01-27T09:10:42.123456Z",
  "force_update": false
}
```

---

### 11. Sync Promotions (Compiled JSON)

```bash
GET /api/v1/sync/promotions/?store_id={uuid}&company_id={uuid}&updated_since={iso_datetime}
```

```bash
curl -X GET "http://localhost:8002/api/v1/sync/promotions/?store_id=$STORE_ID&company_id=$COMPANY_ID" \
  -H "Authorization: Bearer $TOKEN" | jq
```

**Response:** Compiled promotion JSON ready for POS engine

---

### 12. Upload Promotion Usage

```bash
POST /api/v1/sync/usage/
```

```bash
curl -X POST http://localhost:8002/api/v1/sync/usage/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "usages": [
      {
        "promotion_id": "550e8400-e29b-41d4-a716-446655440000",
        "bill_id": "B20260127-001",
        "discount_amount": 15000.0,
        "used_at": "2026-01-27T10:30:00Z",
        "store_id": "'$STORE_ID'",
        "customer_id": null
      }
    ]
  }'
```

---

## 👥 Members API

### 13. Members

#### List Members
```bash
GET /api/v1/members/members/?brand={brand_id}
```

#### Sync Members
```bash
GET /api/v1/members/members/sync/?brand_id={uuid}&last_sync=2026-01-27T00:00:00Z
```

---

## 📤 Transaction Push APIs (Edge → HO)

### 14. Push Bills

```bash
POST /api/v1/transactions/bills/push/
```

```bash
curl -X POST http://localhost:8002/api/v1/transactions/bills/push/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bills": [
      {
        "bill_number": "B20260127-001",
        "store_id": "'$STORE_ID'",
        "total": 50000,
        "items": [...]
      }
    ]
  }'
```

---

## 🔄 Recommended Sync Flow for Edge Server

### Initial Sync (First Boot)

```
1. Get Token → POST /api/token/
2. Sync Company → GET /api/v1/core/companies/sync/
3. Sync Brand → GET /api/v1/core/brands/sync/?brand_id={id}
4. Sync Store → GET /api/v1/core/stores/sync/?store_id={id}
5. Sync Users → GET /api/v1/core/users/sync/?brand_id={id}
6. Sync Categories → GET /api/v1/products/categories/sync/?brand_id={id}
7. Sync Products → GET /api/v1/products/products/sync/?brand_id={id}&store_id={id}
8. Sync Modifiers → GET /api/v1/products/modifiers/sync/?brand_id={id}
9. Sync Table Areas → GET /api/v1/products/table-areas/?brand={id}
10. Sync Kitchen Stations → GET /api/v1/products/kitchen-stations/?brand={id}
11. Check Promotion Version → GET /api/v1/sync/version/?company_id={id}
12. Sync Promotions → GET /api/v1/sync/promotions/?store_id={id}&company_id={id}
13. Sync Members → GET /api/v1/members/members/sync/?brand_id={id}
```

### Periodic Sync (Every 6 Hours)

```
1. Check Promotion Version → GET /api/v1/sync/version/
2. IF version changed:
   - Incremental sync promotions with updated_since
3. Sync master data with last_sync parameter
   - Categories, Products, Modifiers, etc.
```

### Real-time Upload (Continuous)

```
1. Queue transactions locally
2. Every 5 minutes:
   - Upload bills → POST /api/v1/transactions/bills/push/
   - Upload promotion usage → POST /api/v1/sync/usage/
   - Upload cash drops, sessions, etc.
```

---

## 📊 API Comparison: `/api/v1/sync/` vs `/api/v1/`

| Feature | `/api/v1/sync/` | `/api/v1/` |
|---------|-------------|------------|
| **Purpose** | Promotion-specific | General master data |
| **Response Format** | Compiled JSON | Standard REST |
| **Filtering** | Sync strategy based | Query parameters |
| **Compilation** | Pre-compiled | Raw data |
| **Best For** | Promotions only | All other data |

**Recommendation:**
- Use `/api/v1/sync/promotions/` for promotions (compiled + optimized)
- Use `/api/v1/products/categories/` for categories (standard REST)
- Use `/api/v1/products/products/` for products (standard REST)

---

## 🧪 Complete Test Script

```bash
#!/bin/bash
# save as: test_all_edge_apis.sh

BASE_URL="http://localhost:8002"
TOKEN="your_jwt_token"
COMPANY_ID="your_company_id"
BRAND_ID="your_brand_id"
STORE_ID="your_store_id"

echo "🚀 Testing All Edge Server APIs"
echo "================================"

# 1. Core Master Data
echo "1. Testing Companies..."
curl -s "$BASE_URL/api/v1/core/companies/" -H "Authorization: Bearer $TOKEN" | jq '.count'

echo "2. Testing Brands..."
curl -s "$BASE_URL/api/v1/core/brands/" -H "Authorization: Bearer $TOKEN" | jq '.count'

echo "3. Testing Stores..."
curl -s "$BASE_URL/api/v1/core/stores/" -H "Authorization: Bearer $TOKEN" | jq '.count'

echo "4. Testing Users..."
curl -s "$BASE_URL/api/v1/core/users/" -H "Authorization: Bearer $TOKEN" | jq '.count'

# 2. Product Master Data
echo "5. Testing Categories..."
curl -s "$BASE_URL/api/v1/products/categories/" -H "Authorization: Bearer $TOKEN" | jq '.count'

echo "6. Testing Products..."
curl -s "$BASE_URL/api/v1/products/products/" -H "Authorization: Bearer $TOKEN" | jq '.count'

echo "7. Testing Modifiers..."
curl -s "$BASE_URL/api/v1/products/modifiers/" -H "Authorization: Bearer $TOKEN" | jq '.count'

# 3. Promotions
echo "8. Testing Promotion Version..."
curl -s "$BASE_URL/api/v1/sync/version/?company_id=$COMPANY_ID" -H "Authorization: Bearer $TOKEN" | jq '.version'

echo "9. Testing Promotion Sync..."
curl -s "$BASE_URL/api/v1/sync/promotions/?store_id=$STORE_ID&company_id=$COMPANY_ID" -H "Authorization: Bearer $TOKEN" | jq '.total'

echo ""
echo "✅ All tests complete!"
```

---

## 📚 Documentation Index

| Document | Purpose |
|----------|---------|
| **`COMPLETE_EDGE_SERVER_API_GUIDE.md`** (this file) | **Complete API reference** |
| `EDGE_SERVER_TESTING_SUMMARY.md` | Quick summary & checklist |
| `EDGE_SERVER_API_TESTING_GUIDE.md` | Detailed testing guide |
| `SYNC_API_DOCUMENTATION.md` | Promotion sync API details |
| `SYNC_API_POSTMAN_COLLECTION.json` | Postman collection |

---

## ✅ Quick Checklist

### Master Data APIs (READ)
- [ ] Companies - `/api/v1/core/companies/`
- [ ] Brands - `/api/v1/core/brands/`
- [ ] Stores - `/api/v1/core/stores/`
- [ ] Users - `/api/v1/core/users/`
- [ ] Categories - `/api/v1/products/categories/`
- [ ] Products - `/api/v1/products/products/`
- [ ] Modifiers - `/api/v1/products/modifiers/`
- [ ] Table Areas - `/api/v1/products/table-areas/`
- [ ] Kitchen Stations - `/api/v1/products/kitchen-stations/`
- [ ] Members - `/api/v1/members/members/`

### Promotion APIs (READ)
- [ ] Version Check - `/api/v1/sync/version/`
- [ ] Sync Promotions - `/api/v1/sync/promotions/`

### Transaction APIs (WRITE)
- [ ] Upload Promotion Usage - `/api/v1/sync/usage/`
- [ ] Push Bills - `/api/v1/transactions/bills/push/`
- [ ] Push Cash Drops - `/api/v1/transactions/cash-drops/push/`

---

**Dashboard:** http://localhost:8002/promotions/compiler/

**Total APIs Available:** 30+ endpoints

**Status:** ✅ Production Ready
