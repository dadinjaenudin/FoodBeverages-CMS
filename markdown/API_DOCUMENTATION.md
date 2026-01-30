# 🔌 F&B POS HO System - REST API Documentation

**Version**: 1.0  
**Base URL**: `http://localhost:8000/api/v1/`  
**Authentication**: JWT (JSON Web Token)

---

## 📑 Table of Contents

1. [Authentication](#authentication)
2. [API Architecture](#api-architecture)
3. [Core Master Data APIs](#core-master-data-apis)
4. [Product Management APIs](#product-management-apis)
5. [Member & Loyalty APIs](#member--loyalty-apis)
6. [Promotion APIs](#promotion-apis)
7. [Inventory APIs](#inventory-apis)
8. [Transaction APIs](#transaction-apis)
9. [Error Handling](#error-handling)
10. [Testing with Swagger](#testing-with-swagger)
11. [Code Examples](#code-examples)

---

## 🔐 Authentication

### JWT Token Authentication

All API endpoints require JWT authentication except for token obtain endpoints.

### 1. Obtain Token

**Endpoint**: `POST /api/token/`

**Request**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Token Expiry**:
- **Access Token**: 60 minutes
- **Refresh Token**: 24 hours

### 2. Refresh Token

**Endpoint**: `POST /api/token/refresh/`

**Request**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 3. Using Token

Include the access token in the `Authorization` header:

```bash
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## 🏗️ API Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                    HO (Cloud - Django)                  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ REST API Endpoints                               │  │
│  │                                                  │  │
│  │ 1. Master Data Pull (HO → Edge)                 │  │
│  │    - Companies, Brands, Stores                  │  │
│  │    - Products, Categories, Modifiers            │  │
│  │    - Members, Promotions, Inventory             │  │
│  │    - Users & Permissions                        │  │
│  │                                                  │  │
│  │ 2. Transaction Push (Edge → HO)                 │  │
│  │    - Bills, Payments, Refunds                   │  │
│  │    - Kitchen Orders, Stock Movements            │  │
│  │    - Cash Drops, EOD Sessions                   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         ↕ HTTPS + JWT
┌─────────────────────────────────────────────────────────┐
│               Edge Server (Per Store)                   │
│  - Pull master data from HO (periodic)                  │
│  - Push transactions to HO (async queue)                │
│  - Offline-first operation                              │
└─────────────────────────────────────────────────────────┘
```

### Sync Strategy

#### **Incremental Sync**
All master data endpoints support incremental sync using `last_sync` parameter:

```bash
GET /api/v1/core/companies/sync/?last_sync=2026-01-22T10:30:00Z
```

- **First Sync**: Omit `last_sync` parameter (pulls all data)
- **Subsequent Syncs**: Include `last_sync` with ISO datetime (pulls only changes)

#### **Response Format**
```json
{
  "count": 5,
  "last_sync": "2026-01-22T12:00:00Z",
  "data": [...]
}
```

---

## 🏢 Core Master Data APIs

### 1. Companies API

#### **List Companies**
```
GET /api/v1/core/companies/
```

**Response**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "company_code": "YGY",
    "company_name": "Yogya Group",
    "is_active": true,
    "created_at": "2026-01-22T10:00:00Z",
    "updated_at": "2026-01-22T10:00:00Z"
  }
]
```

#### **Sync Companies** (Incremental)
```
GET /api/v1/core/companies/sync/
GET /api/v1/core/companies/sync/?last_sync=2026-01-22T10:30:00Z
```

**Response**:
```json
{
  "count": 1,
  "last_sync": "2026-01-22T12:00:00Z",
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "company_code": "YGY",
      "company_name": "Yogya Group",
      "is_active": true
    }
  ]
}
```

---

### 2. Brands API

#### **List Brands**
```
GET /api/v1/core/brands/
```

**Response**:
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "company": "550e8400-e29b-41d4-a716-446655440000",
    "brand_code": "YGY-001",
    "brand_name": "Ayam Geprek Express",
    "is_active": true,
    "created_at": "2026-01-22T10:00:00Z",
    "updated_at": "2026-01-22T10:00:00Z"
  }
]
```

#### **Sync Brands** (Incremental, Filtered)
```
GET /api/v1/core/brands/sync/?brand_id=660e8400-e29b-41d4-a716-446655440000
GET /api/v1/core/brands/sync/?brand_id=660e8400-e29b-41d4-a716-446655440000&last_sync=2026-01-22T10:30:00Z
```

**Query Parameters**:
- `brand_id` (required): UUID of the brand
- `last_sync` (optional): ISO datetime for incremental sync

**Response**:
```json
{
  "count": 1,
  "last_sync": "2026-01-22T12:00:00Z",
  "data": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440000",
      "company": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "company_name": "Yogya Group"
      },
      "brand_code": "YGY-001",
      "brand_name": "Ayam Geprek Express",
      "is_active": true
    }
  ]
}
```

---

### 3. Stores API

#### **List Stores**
```
GET /api/v1/core/stores/
```

#### **Sync Stores** (Incremental, Filtered)
```
GET /api/v1/core/stores/sync/?store_id=770e8400-e29b-41d4-a716-446655440000
GET /api/v1/core/stores/sync/?store_id=770e8400-e29b-41d4-a716-446655440000&last_sync=2026-01-22T10:30:00Z
```

**Query Parameters**:
- `store_id` (required): UUID of the store
- `last_sync` (optional): ISO datetime for incremental sync

**Response**:
```json
{
  "count": 1,
  "last_sync": "2026-01-22T12:00:00Z",
  "data": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440000",
      "brand": {
        "id": "660e8400-e29b-41d4-a716-446655440000",
        "brand_name": "Ayam Geprek Express"
      },
      "store_code": "BSD-001",
      "store_name": "BSD City",
      "address": "Jl. BSD Raya",
      "phone": "021-12345678",
      "is_active": true
    }
  ]
}
```

---

### 4. Users API

#### **List Users**
```
GET /api/v1/core/users/
```

#### **Sync Users** (Incremental, Filtered by Brand)
```
GET /api/v1/core/users/sync/?brand_id=660e8400-e29b-41d4-a716-446655440000
GET /api/v1/core/users/sync/?brand_id=660e8400-e29b-41d4-a716-446655440000&last_sync=2026-01-22T10:30:00Z
```

**Query Parameters**:
- `brand_id` (required): UUID of the brand
- `last_sync` (optional): ISO datetime for incremental sync

**Response**:
```json
{
  "count": 3,
  "last_sync": "2026-01-22T12:00:00Z",
  "data": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440000",
      "username": "admin",
      "email": "admin@yogyagroup.com",
      "full_name": "System Administrator",
      "role": "ADMIN",
      "role_scope": "company",
      "is_active": true
    }
  ]
}
```

---

## 📦 Product Management APIs

### 1. Categories API

#### **List Categories**
```
GET /api/v1/products/categories/
```

#### **Sync Categories** (Incremental, Filtered by Brand)
```
GET /api/v1/products/categories/sync/?brand_id=660e8400-e29b-41d4-a716-446655440000
GET /api/v1/products/categories/sync/?brand_id=660e8400-e29b-41d4-a716-446655440000&last_sync=2026-01-22T10:30:00Z
```

**Response**:
```json
{
  "count": 11,
  "last_sync": "2026-01-22T12:00:00Z",
  "data": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440000",
      "category_code": "FOOD",
      "category_name": "Food",
      "parent_category": null,
      "is_active": true,
      "sort_order": 1
    }
  ]
}
```

---

### 2. Products API

#### **List Products**
```
GET /api/v1/products/products/
```

#### **Sync Products** (Incremental, Filtered by Brand)
```
GET /api/v1/products/products/sync/?brand_id=660e8400-e29b-41d4-a716-446655440000
GET /api/v1/products/products/sync/?brand_id=660e8400-e29b-41d4-a716-446655440000&last_sync=2026-01-22T10:30:00Z
```

**Response**:
```json
{
  "count": 17,
  "last_sync": "2026-01-22T12:00:00Z",
  "data": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440000",
      "product_code": "PROD-001",
      "product_name": "Ayam Bakar",
      "category": "990e8400-e29b-41d4-a716-446655440000",
      "description": "Grilled chicken with special sauce",
      "base_price": 25000.00,
      "is_available": true,
      "is_active": true
    }
  ]
}
```

---

### 3. Modifiers API

#### **List Modifiers**
```
GET /api/v1/products/modifiers/
```

#### **Sync Modifiers** (Incremental, Filtered by Brand)
```
GET /api/v1/products/modifiers/sync/?brand_id=660e8400-e29b-41d4-a716-446655440000
```

**Response**:
```json
{
  "count": 5,
  "last_sync": "2026-01-22T12:00:00Z",
  "data": [
    {
      "id": "bb0e8400-e29b-41d4-a716-446655440000",
      "modifier_name": "Spice Level",
      "modifier_type": "SINGLE",
      "is_required": true,
      "options": [
        {
          "id": "cc0e8400-e29b-41d4-a716-446655440000",
          "option_name": "Mild",
          "additional_price": 0.00
        }
      ]
    }
  ]
}
```

---

### 4. Table Areas & Tables API

#### **Sync Table Areas**
```
GET /api/v1/products/tableareas/sync/?brand_id=660e8400-e29b-41d4-a716-446655440000
```

#### **Sync Tables**
```
GET /api/v1/products/tables/sync/?store_id=770e8400-e29b-41d4-a716-446655440000
```

---

### 5. Kitchen Stations API

#### **Sync Kitchen Stations**
```
GET /api/v1/products/kitchenstations/sync/?brand_id=660e8400-e29b-41d4-a716-446655440000
```

---

## 👥 Member & Loyalty APIs

### 1. Members API

#### **List Members**
```
GET /api/v1/members/members/
```

#### **Sync Members** (Bidirectional)
```
GET /api/v1/members/members/sync/?brand_id=660e8400-e29b-41d4-a716-446655440000
POST /api/v1/members/members/  # Create from Edge
PUT /api/v1/members/members/{id}/  # Update from Edge
```

**Response** (GET):
```json
{
  "count": 5,
  "last_sync": "2026-01-22T12:00:00Z",
  "data": [
    {
      "id": "dd0e8400-e29b-41d4-a716-446655440000",
      "member_number": "MBR-0001",
      "full_name": "John Doe",
      "phone_number": "08123456789",
      "email": "john@example.com",
      "current_points": 1500,
      "tier": "silver",
      "is_active": true
    }
  ]
}
```

**Create Member** (POST):
```json
{
  "member_number": "MBR-0002",
  "full_name": "Jane Smith",
  "phone_number": "08987654321",
  "email": "jane@example.com",
  "brand_id": "660e8400-e29b-41d4-a716-446655440000"
}
```

---

### 2. Member Transactions API

#### **Get Member Transactions**
```
GET /api/v1/members/members/{id}/transactions/
```

---

## 🎁 Promotion APIs

### 1. Promotions API

#### **List Promotions**
```
GET /api/v1/promotions/promotions/
```

#### **Sync Promotions** (Incremental)
```
GET /api/v1/promotions/promotions/sync/?brand_id=660e8400-e29b-41d4-a716-446655440000
GET /api/v1/promotions/promotions/sync/?brand_id=660e8400-e29b-41d4-a716-446655440000&last_sync=2026-01-22T10:30:00Z
```

**Response**:
```json
{
  "count": 5,
  "last_sync": "2026-01-22T12:00:00Z",
  "data": [
    {
      "id": "ee0e8400-e29b-41d4-a716-446655440000",
      "code": "NEWYEAR2026",
      "name": "New Year Mega Sale",
      "promo_type": "percent_discount",
      "discount_percent": 30.00,
      "max_discount_amount": 50000.00,
      "start_date": "2026-01-01",
      "end_date": "2026-01-07",
      "is_active": true
    }
  ]
}
```

---

### 2. Vouchers API

#### **Validate Voucher**
```
POST /api/v1/promotions/vouchers/validate/
```

**Request**:
```json
{
  "voucher_code": "WELCOME2026",
  "member_id": "dd0e8400-e29b-41d4-a716-446655440000",
  "bill_amount": 100000.00
}
```

**Response**:
```json
{
  "valid": true,
  "voucher": {
    "id": "ff0e8400-e29b-41d4-a716-446655440000",
    "code": "WELCOME2026",
    "discount_amount": 20000.00
  }
}
```

---

## 📦 Inventory APIs

### 1. Inventory Items API

#### **Sync Inventory Items**
```
GET /api/v1/inventory/items/sync/?brand_id=660e8400-e29b-41d4-a716-446655440000
```

**Response**:
```json
{
  "count": 6,
  "last_sync": "2026-01-22T12:00:00Z",
  "data": [
    {
      "id": "gg0e8400-e29b-41d4-a716-446655440000",
      "item_code": "RM-CHICKEN-001",
      "name": "Chicken Breast",
      "item_type": "raw_material",
      "base_unit": "kg",
      "cost_per_unit": 45000.00,
      "min_stock": 10.00,
      "max_stock": 50.00
    }
  ]
}
```

---

### 2. Recipes (BOM) API

#### **Sync Recipes**
```
GET /api/v1/inventory/recipes/sync/?brand_id=660e8400-e29b-41d4-a716-446655440000
```

**Response**:
```json
{
  "count": 1,
  "last_sync": "2026-01-22T12:00:00Z",
  "data": [
    {
      "id": "hh0e8400-e29b-41d4-a716-446655440000",
      "recipe_code": "RCP-001",
      "recipe_name": "Recipe for Ayam Bakar",
      "product": "aa0e8400-e29b-41d4-a716-446655440000",
      "version": 1,
      "yield_quantity": 1.00,
      "yield_unit": "portion",
      "ingredients": [
        {
          "inventory_item": "gg0e8400-e29b-41d4-a716-446655440000",
          "quantity": 0.25,
          "unit": "kg",
          "yield_factor": 0.90
        }
      ]
    }
  ]
}
```

---

## 💰 Transaction APIs (Edge → HO)

### 1. Bills API

#### **Push Bill** (Create from Edge)
```
POST /api/v1/transactions/bills/
```

**Request**:
```json
{
  "store": "770e8400-e29b-41d4-a716-446655440000",
  "bill_number": "BILL-2026-001",
  "bill_date": "2026-01-22T12:00:00Z",
  "table_number": "A1",
  "customer_count": 2,
  "subtotal": 100000.00,
  "tax_amount": 10000.00,
  "service_charge": 5000.00,
  "discount_amount": 10000.00,
  "total_amount": 105000.00,
  "payment_status": "PAID",
  "items": [
    {
      "product": "aa0e8400-e29b-41d4-a716-446655440000",
      "quantity": 2,
      "unit_price": 25000.00,
      "subtotal": 50000.00
    }
  ]
}
```

**Response** (201 Created):
```json
{
  "id": "ii0e8400-e29b-41d4-a716-446655440000",
  "bill_number": "BILL-2026-001",
  "total_amount": 105000.00,
  "status": "received"
}
```

---

### 2. Payments API

#### **Push Payment**
```
POST /api/v1/transactions/payments/
```

**Request**:
```json
{
  "bill": "ii0e8400-e29b-41d4-a716-446655440000",
  "payment_method": "CASH",
  "amount": 105000.00,
  "payment_date": "2026-01-22T12:05:00Z"
}
```

---

### 3. Stock Movements API

#### **Push Stock Movement**
```
POST /api/v1/transactions/stock-movements/
```

**Request**:
```json
{
  "store": "770e8400-e29b-41d4-a716-446655440000",
  "inventory_item": "gg0e8400-e29b-41d4-a716-446655440000",
  "movement_type": "out",
  "quantity": 0.25,
  "unit": "kg",
  "reference_no": "BILL-2026-001",
  "notes": "Used for production",
  "movement_date": "2026-01-22T12:00:00Z"
}
```

---

### 4. Cash Drops API

#### **Push Cash Drop**
```
POST /api/v1/transactions/cash-drops/
```

---

### 5. Store Sessions (EOD) API

#### **Push Store Session**
```
POST /api/v1/transactions/sessions/
```

---

## ⚠️ Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "error": "Error message",
  "detail": "Detailed error description",
  "code": "ERROR_CODE"
}
```

### HTTP Status Codes

| Status Code | Meaning | Usage |
|-------------|---------|-------|
| 200 | OK | Successful GET request |
| 201 | Created | Successful POST (resource created) |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |

### Common Errors

#### 1. Authentication Error
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Solution**: Include `Authorization: Bearer {token}` header

#### 2. Invalid Token
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid"
}
```

**Solution**: Refresh or obtain a new token

#### 3. Missing Required Parameter
```json
{
  "error": "brand_id parameter required"
}
```

**Solution**: Include the required query parameter

#### 4. Validation Error
```json
{
  "field_name": [
    "This field is required."
  ]
}
```

**Solution**: Fix the validation error in the request data

---

## 🧪 Testing with Swagger

### Access Swagger UI

**URL**: `http://localhost:8000/api/docs/`

### Using Swagger UI

#### **Step 1: Obtain Token**
1. Go to `/api/docs/`
2. Find **"POST /api/token/"** endpoint
3. Click **"Try it out"**
4. Enter credentials:
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
5. Click **"Execute"**
6. Copy the `access` token from response

#### **Step 2: Authorize**
1. Click **"Authorize"** button (top right)
2. Enter: `Bearer {your_access_token}`
3. Click **"Authorize"**
4. Click **"Close"**

#### **Step 3: Test Endpoints**
1. Choose any endpoint (e.g., **"GET /api/v1/core/companies/sync/"**)
2. Click **"Try it out"**
3. Fill in parameters (if required)
4. Click **"Execute"**
5. View response

### Alternative: ReDoc Documentation

**URL**: `http://localhost:8000/api/redoc/`

ReDoc provides a cleaner, read-only documentation interface.

---

## 💻 Code Examples

### Python (requests)

#### **Obtain Token**
```python
import requests

url = "http://localhost:8000/api/token/"
data = {
    "username": "admin",
    "password": "admin123"
}

response = requests.post(url, json=data)
token = response.json()["access"]
print(f"Token: {token}")
```

#### **Sync Companies**
```python
import requests

url = "http://localhost:8000/api/v1/core/companies/sync/"
headers = {
    "Authorization": f"Bearer {token}"
}

response = requests.get(url, headers=headers)
companies = response.json()
print(f"Companies: {companies}")
```

#### **Create Bill**
```python
import requests

url = "http://localhost:8000/api/v1/transactions/bills/"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
data = {
    "store": "770e8400-e29b-41d4-a716-446655440000",
    "bill_number": "BILL-2026-001",
    "bill_date": "2026-01-22T12:00:00Z",
    "subtotal": 100000.00,
    "total_amount": 105000.00,
    "payment_status": "PAID"
}

response = requests.post(url, headers=headers, json=data)
bill = response.json()
print(f"Bill created: {bill}")
```

---

### JavaScript (fetch)

#### **Obtain Token**
```javascript
const url = "http://localhost:8000/api/token/";
const data = {
  username: "admin",
  password: "admin123"
};

fetch(url, {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(data)
})
  .then(response => response.json())
  .then(data => {
    const token = data.access;
    console.log("Token:", token);
  });
```

#### **Sync Products**
```javascript
const url = "http://localhost:8000/api/v1/products/products/sync/?brand_id=660e8400-e29b-41d4-a716-446655440000";
const token = "your_access_token_here";

fetch(url, {
  method: "GET",
  headers: {
    "Authorization": `Bearer ${token}`
  }
})
  .then(response => response.json())
  .then(data => {
    console.log("Products:", data);
  });
```

---

### cURL

#### **Obtain Token**
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

#### **Sync Companies**
```bash
curl -X GET http://localhost:8000/api/v1/core/companies/sync/ \
  -H "Authorization: Bearer {your_token}"
```

#### **Sync Products with Last Sync**
```bash
curl -X GET "http://localhost:8000/api/v1/products/products/sync/?brand_id=660e8400-e29b-41d4-a716-446655440000&last_sync=2026-01-22T10:30:00Z" \
  -H "Authorization: Bearer {your_token}"
```

---

## 📊 API Endpoint Summary

### Master Data Pull (HO → Edge) - Read-Only

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/core/companies/sync/` | GET | Sync companies |
| `/api/v1/core/brands/sync/` | GET | Sync brands |
| `/api/v1/core/stores/sync/` | GET | Sync stores |
| `/api/v1/core/users/sync/` | GET | Sync users |
| `/api/v1/products/categories/sync/` | GET | Sync categories |
| `/api/v1/products/products/sync/` | GET | Sync products |
| `/api/v1/products/modifiers/sync/` | GET | Sync modifiers |
| `/api/v1/products/tableareas/sync/` | GET | Sync table areas |
| `/api/v1/products/kitchenstations/sync/` | GET | Sync kitchen stations |
| `/api/v1/members/members/sync/` | GET | Sync members |
| `/api/v1/promotions/promotions/sync/` | GET | Sync promotions |
| `/api/v1/inventory/items/sync/` | GET | Sync inventory items |
| `/api/v1/inventory/recipes/sync/` | GET | Sync recipes |

### Transaction Push (Edge → HO) - Write

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/transactions/bills/` | POST | Push bills |
| `/api/v1/transactions/payments/` | POST | Push payments |
| `/api/v1/transactions/stock-movements/` | POST | Push stock movements |
| `/api/v1/transactions/cash-drops/` | POST | Push cash drops |
| `/api/v1/transactions/sessions/` | POST | Push EOD sessions |
| `/api/v1/transactions/kitchen-orders/` | POST | Push kitchen orders |
| `/api/v1/transactions/refunds/` | POST | Push refunds |

### Bidirectional Sync

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/api/v1/members/members/` | GET, POST, PUT | Member CRUD |
| `/api/v1/members/members/{id}/transactions/` | GET, POST | Member transactions |

---

## 🔗 Quick Links

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/
- **Admin Panel**: http://localhost:8000/admin/
- **Main README**: [README.md](README.md)

---

## 📞 Support

For API questions or issues:
- **Email**: api-support@yogyagroup.com
- **Slack**: #api-development
- **Documentation**: This file

---

**Version**: 1.0  
**Last Updated**: 2026-01-22  
**Status**: Production Ready ✅
