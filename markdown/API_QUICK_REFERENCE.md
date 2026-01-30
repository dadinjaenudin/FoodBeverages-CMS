# 🚀 Edge Server API - Quick Reference Card

**Dokumentasi lengkap semua API untuk Edge Server**

---

## 🔑 Authentication (STEP 1)

```bash
# Get JWT Token
curl -X POST http://localhost:8002/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Response: {"access": "YOUR_TOKEN", "refresh": "..."}
# Use: -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📋 Master Data APIs - `/api/v1/`

### Core Data (Company/Brand/Store/Users)

| API | Endpoint | Example |
|-----|----------|---------|
| **Companies** | `GET /api/v1/core/companies/` | List all |
| **Companies Sync** | `GET /api/v1/core/companies/sync/?last_sync={iso}` | Incremental |
| **Brands** | `GET /api/v1/core/brands/` | List all |
| **Brands Sync** | `GET /api/v1/core/brands/sync/?brand_id={uuid}&last_sync={iso}` | Specific brand |
| **Stores** | `GET /api/v1/core/stores/` | List all |
| **Stores Sync** | `GET /api/v1/core/stores/sync/?store_id={uuid}&last_sync={iso}` | Specific store |
| **Users** | `GET /api/v1/core/users/` | List all |
| **Users Sync** | `GET /api/v1/core/users/sync/?brand_id={uuid}&last_sync={iso}` | For brand |

### Product Data (Categories/Products/Modifiers)

| API | Endpoint | Example |
|-----|----------|---------|
| **Categories** | `GET /api/v1/products/categories/` | List all |
| **Categories Sync** | `GET /api/v1/products/categories/sync/?brand_id={uuid}&last_sync={iso}` | Incremental |
| **Products** | `GET /api/v1/products/products/?brand={uuid}` | For brand |
| **Products Sync** | `GET /api/v1/products/products/sync/?brand_id={uuid}&store_id={uuid}&last_sync={iso}` | Incremental |
| **Modifiers** | `GET /api/v1/products/modifiers/?brand={uuid}` | For brand |
| **Modifiers Sync** | `GET /api/v1/products/modifiers/sync/?brand_id={uuid}&last_sync={iso}` | Incremental |
| **Table Areas** | `GET /api/v1/products/table-areas/?brand={uuid}` | For brand |
| **Kitchen Stations** | `GET /api/v1/products/kitchen-stations/?brand={uuid}` | For brand |

### Members Data

| API | Endpoint | Example |
|-----|----------|---------|
| **Members** | `GET /api/v1/members/members/?brand={uuid}` | For brand |
| **Members Sync** | `GET /api/v1/members/members/sync/?brand_id={uuid}&last_sync={iso}` | Incremental |

---

## 🎁 Promotion APIs - `/api/v1/sync/`

| API | Endpoint | Example |
|-----|----------|---------|
| **Version Check** | `GET /api/v1/sync/version/?company_id={uuid}` | Check if sync needed |
| **Sync Promotions** | `GET /api/v1/sync/promotions/?store_id={uuid}&company_id={uuid}` | Full sync |
| **Incremental Sync** | `GET /api/v1/sync/promotions/?store_id={uuid}&company_id={uuid}&updated_since={iso}` | Only updates |
| **Upload Usage** | `POST /api/v1/sync/usage/` | Upload promotion usage |

---

## 📤 Transaction Push APIs (Edge → HO)

| API | Endpoint | Purpose |
|-----|----------|---------|
| **Push Bills** | `POST /api/v1/transactions/bills/push/` | Upload transactions |
| **Push Cash Drops** | `POST /api/v1/transactions/cash-drops/push/` | Upload cash drops |
| **Push Sessions** | `POST /api/v1/transactions/sessions/push/` | Upload store sessions |

---

## 🔄 Sync Strategy

### Initial Sync (First Boot)

```
1. GET /api/token/ → Get token
2. GET /api/v1/core/companies/sync/
3. GET /api/v1/core/brands/sync/?brand_id={id}
4. GET /api/v1/core/stores/sync/?store_id={id}
5. GET /api/v1/core/users/sync/?brand_id={id}
6. GET /api/v1/products/categories/sync/?brand_id={id}
7. GET /api/v1/products/products/sync/?brand_id={id}&store_id={id}
8. GET /api/v1/products/modifiers/sync/?brand_id={id}
9. GET /api/v1/sync/version/?company_id={id}
10. GET /api/v1/sync/promotions/?store_id={id}&company_id={id}
11. GET /api/v1/members/members/sync/?brand_id={id}
```

### Periodic Sync (Every 6 Hours)

```
1. GET /api/v1/sync/version/ → Check if changed
2. If changed:
   GET /api/v1/sync/promotions/?...&updated_since={last_sync}
3. Sync master data with last_sync parameter
```

### Real-time Upload (Every 5 Minutes)

```
1. POST /api/v1/sync/usage/ → Promotion usage
2. POST /api/v1/transactions/bills/push/ → Transactions
```

---

## 🧪 Quick Test Commands

```bash
# Setup
export TOKEN="your_jwt_token"
export COMPANY_ID="your_company_id"
export BRAND_ID="your_brand_id"
export STORE_ID="your_store_id"

# Test 1: Get Companies
curl -X GET http://localhost:8002/api/v1/core/companies/ \
  -H "Authorization: Bearer $TOKEN" | jq

# Test 2: Get Products
curl -X GET "http://localhost:8002/api/v1/products/products/?brand=$BRAND_ID" \
  -H "Authorization: Bearer $TOKEN" | jq

# Test 3: Check Promotion Version
curl -X GET "http://localhost:8002/api/v1/sync/version/?company_id=$COMPANY_ID" \
  -H "Authorization: Bearer $TOKEN" | jq

# Test 4: Sync Promotions
curl -X GET "http://localhost:8002/api/v1/sync/promotions/?store_id=$STORE_ID&company_id=$COMPANY_ID" \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## 📊 API Comparison

| Feature | `/api/v1/sync/` | `/api/v1/` |
|---------|-------------|------------|
| **Purpose** | Promotions only | All master data |
| **Format** | Compiled JSON | Standard REST |
| **Use For** | Promotions | Categories, Products, Users, etc |

**Best Practice:**
- Use `/api/v1/sync/promotions/` for promotions (optimized)
- Use `/api/v1/products/categories/` for categories
- Use `/api/v1/products/products/` for products

---

## ⏱️ Expected Response Times

| Endpoint | Expected | Max |
|----------|----------|-----|
| `/api/v1/sync/version/` | < 50ms | 200ms |
| `/api/v1/core/companies/` | < 100ms | 500ms |
| `/api/v1/products/categories/` | < 200ms | 1s |
| `/api/v1/products/products/` | < 500ms | 2s |
| `/api/v1/sync/promotions/` | < 1s | 5s |

---

## 🐛 Common Errors

### ❌ 401 Unauthorized
**Fix:** Get fresh token from `/api/token/`

### ❌ 400 Bad Request - "brand_id parameter required"
**Fix:** Add `?brand_id={uuid}` to URL

### ❌ Empty results
**Fix:** Check brand_id, store_id, filters

---

## 📚 Full Documentation

- **`COMPLETE_EDGE_SERVER_API_GUIDE.md`** - Complete API reference (this is the main one!)
- **`EDGE_SERVER_TESTING_SUMMARY.md`** - Testing summary
- **`SYNC_API_DOCUMENTATION.md`** - Promotion API details
- **`SYNC_API_POSTMAN_COLLECTION.json`** - Postman collection

---

## 🎯 Total APIs Available

✅ **Authentication:** 2 endpoints
✅ **Core Master Data:** 8 endpoints (Companies, Brands, Stores, Users)
✅ **Product Master Data:** 14 endpoints (Categories, Products, Modifiers, Tables, Stations)
✅ **Promotions:** 5 endpoints (Version, Sync, Upload)
✅ **Members:** 2 endpoints
✅ **Transactions:** 3+ endpoints (Bills, Cash Drops, Sessions)

**Total: 30+ API endpoints!**

**Dashboard:** http://localhost:8002/promotions/compiler/

---

**Print this as your reference card! 🚀**

