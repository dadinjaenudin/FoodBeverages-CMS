# 🍽️ F&B POS HO System (Head Office / Cloud)

**Multi-Tenant Cloud-Based Head Office System for F&B POS**

---

## 📖 Overview

Head Office (HO) system untuk mengelola **master data**, menerima **data transaksional** dari Edge Server, dan menyediakan **reporting & analytics** untuk jaringan restoran multi-brand.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    HO (Cloud - Django)                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Master Data Management                           │  │
│  │ - Company / Brand / Store                        │  │
│  │ - Products / Categories / Modifiers              │  │
│  │ - Members / Loyalty                              │  │
│  │ - Promotions (12+ types)                         │  │
│  │ - Inventory / Recipes (BOM)                      │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │ REST API (JWT Auth)                              │  │
│  │ - HO → Edge: Master data pull (incremental)     │  │
│  │ - Edge → HO: Transaction data push (async)      │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Transaction Reception (Read-Only)                │  │
│  │ - Bills / Payments / Refunds                     │  │
│  │ - Kitchen Orders                                 │  │
│  │ - Cash Drops / EOD Sessions                      │  │
│  │ - Inventory Movements                            │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Reporting & Analytics                            │  │
│  │ - Multi-store sales reports                      │  │
│  │ - Promotion performance                          │  │
│  │ - Inventory COGS & margin                        │  │
│  │ - Member loyalty analytics                       │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         ↕ REST API (HTTPS)
┌─────────────────────────────────────────────────────────┐
│               Edge Server (Per Store - Django)          │
│  - POS UI (HTMX)                                        │
│  - Offline-first (LAN only)                             │
│  - Single source of truth per store                     │
│  - Pull master data from HO (periodic)                  │
│  - Push transactions to HO (async queue)                │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Features

### 1. **Multi-Tenant Hierarchy**
- **Company** → **Brand** → **Store** → **Terminal**
- Company: Yogya Group (YGY)
- Brand: Ayam Geprek Express (YGY-001), Bakso Boedjangan (YGY-002), etc.
- Store: BSD, Senayan, Gading, etc.
- Role-based access control: `company` > `brand` > `store`

### 2. **Master Data Management**
- **Products**: Categories, Products, Modifiers, Photos
- **Tables**: Areas, Tables, Table Groups (dine-in)
- **Members**: Loyalty program with points & tiers
- **Promotions**: 12+ types (BOGO, Happy Hour, Member Tier, Package, etc.)
- **Inventory**: Items, Recipes (BOM), Yield factors
- **Users**: Multi-scope authorization (Admin, Manager, Cashier)

### 3. **Promotion Engine** ⭐
**12+ Promotion Types**:
- Percent/Amount Discount
- BOGO (Buy X Get Y)
- Package/Set Menu
- Combo/Bundle
- Mix & Match
- Threshold/Tiered Discount
- Happy Hour (Time-based)
- Payment Method Discount
- Member Tier Discount
- Upsell/Add-on
- Voucher-based
- Manual Discount (with approval)

**Features**:
- Multi-brand scope
- Stacking rules & conflict resolution
- Execution priority
- Usage limits (per customer)
- Manager approval workflow
- Explainability logs (applied/skipped with reasons)

### 4. **Inventory & Recipe Management** ⭐
- **Inventory Items**: Raw Material, Semi-Finished, Finished Goods, Packaging
- **Recipes (BOM)**: Multi-versioned, with ingredients
- **Yield Factor**: Handle cooking loss & waste
- **COGS Calculation**: Recipe cost → Product margin
- **Stock Deduction**: POS sale → Recipe explosion → Inventory movement

### 5. **Transaction Data Reception**
HO receives transaction data from Edge Servers (read-only):
- **Bills**: Complete transaction records
- **BillItems**: Line items with modifiers
- **Payments**: Multi-payment support (CASH, CARD, QRIS, EWALLET, etc.)
- **BillPromotions**: Applied promotions tracking
- **CashDrops**: Cash management
- **StoreSession**: EOD sessions with variance
- **KitchenOrders**: Kitchen operations tracking
- **BillRefunds**: Refund workflow (with approval)
- **InventoryMovements**: Stock movements from POS

### 6. **Sync API (HO ↔ Edge)**
**HO → Edge (Master Data Pull)**:
- `/api/v1/core/companies/sync/`
- `/api/v1/core/brands/sync/`
- `/api/v1/core/stores/sync/`
- `/api/v1/core/users/sync/`
- TODO: Products, Members, Promotions, Inventory

**Edge → HO (Transaction Push)**: TODO

**Features**:
- Incremental sync with `last_sync` parameter
- JWT authentication
- Brand/Store filtering for Edge
- Read-only ViewSets

### 7. **Management Commands**
- `python manage.py expire_member_points` - Expire member points (daily)
- `python manage.py generate_sample_data` - Generate test data

---

## 🛠️ Tech Stack

### **Backend**
- **Framework**: Django 5.0.1
- **API**: Django REST Framework 3.14+
- **Database**: PostgreSQL 15+ (production), SQLite (development)
- **Cache**: Redis (via django-redis)
- **Task Queue**: Celery + Redis (scheduled jobs)
- **Authentication**: JWT (djangorestframework-simplejwt)

### **Frontend** ⭐ **NEW!**
- **UI Framework**: HTMX 1.9+ (partial page updates)
- **JavaScript**: Alpine.js 3.x (reactive components)
- **CSS**: Tailwind CSS 3.x (utility-first styling)
- **Icons**: Font Awesome 6.x
- **Template Engine**: Django Templates (Jinja2-compatible)

### **Deployment**
- **Containerization**: Docker + Docker Compose
- **Web Server**: Gunicorn (production), Django DevServer (development)
- **Reverse Proxy**: Nginx (production)
- **Static Files**: WhiteNoise (development), S3/CDN (production)

### **Development Tools**
- **Code Quality**: Black (formatter), Flake8 (linter)
- **Version Control**: Git + GitHub
- **API Docs**: drf-spectacular (OpenAPI/Swagger) - planned
- **Testing**: Django TestCase + pytest - planned

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.12+
- PostgreSQL 15+ (production) or SQLite (dev)
- Redis (for caching & Celery)

### 1. Clone & Setup Virtual Environment

```bash
git clone <repository-url>
cd webapp
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 4. Database Setup

**Development (SQLite)**:
```bash
python manage.py migrate
python manage.py createsuperuser
```

**Production (PostgreSQL via Docker)**:
```bash
docker-compose up -d db redis
python manage.py migrate
python manage.py createsuperuser
```

### 5. Generate Sample Data (Optional)

```bash
python manage.py generate_sample_data

# Login credentials:
# - Admin: admin / admin123
# - Manager: manager_bsd / manager123
# - Cashier: cashier1 / cashier123 (PIN: 1234)
```

### 6. Run Development Server

```bash
python manage.py runserver
```

**Access Points**:
- **Admin Panel**: http://localhost:8000/admin/
- **Dashboard**: http://localhost:8000/dashboard/
- **Login Page**: http://localhost:8000/auth/login/

**Default Credentials** (from sample data):
- **Admin**: `admin` / `admin123`
- **Manager**: `manager_bsd` / `manager123`
- **Cashier**: `cashier1` / `cashier123` (PIN: 1234)

### 7. Explore the UI ⭐ **NEW!**

After logging in, you can access:

**Master Data Management**:
- Companies: http://localhost:8000/company/
- Brands: http://localhost:8000/brand/
- Stores: http://localhost:8000/store/
- Categories: http://localhost:8000/products/categories/
- Products: http://localhost:8000/products/
- Modifiers: http://localhost:8000/products/modifiers/
- Table Areas: http://localhost:8000/products/tableareas/
- Kitchen Stations: http://localhost:8000/products/kitchenstations/

**Customer & Marketing**:
- Members: http://localhost:8000/members/
- Promotions: http://localhost:8000/promotions/

**Inventory Management**:
- Inventory Items: http://localhost:8000/inventory/items/
- Recipes (BOM): http://localhost:8000/inventory/recipes/
- Stock Movements: http://localhost:8000/inventory/movements/

**Features to Try**:
- ✅ Search products by name or code
- ✅ Filter by category, brand, or status
- ✅ Create new products via modal form
- ✅ Edit products with real-time validation
- ✅ Delete with confirmation dialog
- ✅ Pagination through large lists
- ✅ HTMX partial updates (no page reload)

---

## 📁 Project Structure

```
webapp/
├── config/                 # Django project settings
│   ├── settings.py        # Production-ready settings
│   ├── urls.py            # Main URL config (includes API)
│   ├── celery.py          # Celery configuration
│   └── wsgi.py
├── core/                   # Multi-tenant core models
│   ├── models.py          # Company, Brand, Store, User
│   ├── admin.py           # Admin with multi-tenant filtering
│   ├── views/             # Auth views (login/logout)
│   ├── api/               # REST API endpoints
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── management/commands/
│       └── generate_sample_data.py
├── dashboard/              # Dashboard module ⭐ NEW!
│   ├── views.py           # Dashboard overview
│   └── urls.py
├── products/               # Product catalog
│   ├── models.py          # Category, Product, Modifier, Table, etc.
│   ├── admin.py
│   ├── views/             # CRUD views for all product modules ⭐
│   │   ├── product_views.py
│   │   ├── category_views.py
│   │   ├── modifier_views.py
│   │   ├── tablearea_views.py
│   │   └── kitchenstation_views.py
│   ├── urls_product.py    # Product URLs
│   ├── urls_category.py   # Category URLs
│   ├── urls_modifier.py   # Modifier URLs
│   ├── urls_tablearea.py  # Table Area URLs
│   └── urls_kitchenstation.py  # Kitchen Station URLs
├── members/                # Loyalty program
│   ├── models.py          # Member, MemberTransaction
│   ├── admin.py
│   ├── views/             # Member CRUD views ⭐
│   │   └── member_views.py
│   ├── urls.py
│   └── management/commands/
│       └── expire_member_points.py
├── promotions/             # Promotion engine (12+ types)
│   ├── models.py          # Promotion, PackagePromotion, Voucher, etc.
│   ├── admin.py
│   ├── views/             # Promotion CRUD views ⭐
│   │   └── promotion_views.py
│   └── urls.py
├── inventory/              # Inventory & Recipe (BOM)
│   ├── models.py          # InventoryItem, Recipe, RecipeIngredient, StockMovement
│   ├── admin.py
│   ├── views/             # Inventory CRUD views ⭐
│   │   ├── inventoryitem_views.py
│   │   ├── recipe_views.py
│   │   └── stockmovement_views.py
│   ├── urls_inventoryitem.py
│   ├── urls_recipe.py
│   └── urls_stockmovement.py
├── transactions/           # Transaction data from Edge (read-only)
│   ├── models.py          # Bill, BillItem, Payment, etc.
│   └── admin.py
├── templates/              # Django templates ⭐ NEW!
│   ├── base.html          # Base template with sidebar/navbar
│   ├── partials/          # Reusable components
│   │   ├── sidebar_menu.html
│   │   ├── navbar.html
│   │   └── pagination.html
│   ├── dashboard/         # Dashboard templates
│   │   └── index.html
│   ├── auth/              # Authentication templates
│   │   ├── login.html
│   │   └── logout.html
│   ├── products/          # Product module templates
│   │   ├── product/       # Product CRUD
│   │   │   ├── list.html
│   │   │   ├── _table.html
│   │   │   └── _form.html
│   │   ├── category/      # Category CRUD
│   │   ├── modifier/      # Modifier CRUD
│   │   ├── tablearea/     # Table Area CRUD
│   │   └── kitchenstation/  # Kitchen Station CRUD
│   ├── members/           # Member module templates
│   │   └── member/
│   │       ├── list.html
│   │       ├── _table.html
│   │       └── _form.html
│   ├── promotions/        # Promotion module templates
│   │   └── promotion/
│   │       ├── list.html
│   │       ├── _table.html
│   │       └── _form.html
│   └── inventory/         # Inventory module templates
│       ├── inventoryitem/
│       │   ├── list.html
│       │   ├── _table.html
│       │   └── _form.html
│       ├── recipe/
│       │   ├── list.html
│       │   ├── _table.html
│       │   └── _form.html
│       └── stockmovement/
│           ├── list.html
│           └── _table.html
├── static/                 # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── docker-compose.yml      # PostgreSQL + Redis
├── requirements.txt
├── .env.example
├── README.md              # This file
└── TESTING_CHECKLIST.md   # Comprehensive testing guide (350+ tests)
```

---

## 📊 Database Schema

**Total Tables**: 50+ (including Django system tables)

**Core Models** (4):
- Company, Brand, Store, User

**Product Models** (12):
- Category, Product, ProductPhoto, Modifier, ModifierOption, ProductModifier
- TableArea, Table, TableGroup, TableGroupMember
- KitchenStation, PrinterConfig

**Member Models** (2):
- Member, MemberTransaction

**Promotion Models** (8):
- Promotion, PackagePromotion, PackageItem, PromotionTier
- Voucher, PromotionUsage, PromotionLog, PromotionApproval
- CustomerPromotionHistory

**Inventory Models** (4):
- InventoryItem, Recipe, RecipeIngredient, StockMovement

**Transaction Models** (10):
- Bill, BillItem, Payment, BillPromotion
- CashDrop, StoreSession, CashierShift
- KitchenOrder, BillRefund, InventoryMovement

**Total Application Models**: 40+

### 📈 **Sample Data Statistics**
- **64 sample records** across 14 modules
- Proper foreign key relationships
- Multi-tenant data isolation (Company → Brand → Store)
- UUID primary keys for distributed systems
- Indexed fields for search/filter performance

See `TESTING_CHECKLIST.md` for detailed field descriptions and `DATABASE_ERD.md` for entity relationships.

---

## 🔐 Authentication & Permissions

### JWT Authentication

**Obtain Token**:
```bash
POST /api/token/
{
  "username": "admin",
  "password": "admin123"
}

# Response:
{
  "access": "eyJ0eXAiOiJKV1Q...",
  "refresh": "eyJ0eXAiOiJKV1Q..."
}
```

**Use Token**:
```bash
GET /api/v1/core/companies/sync/
Authorization: Bearer eyJ0eXAiOiJKV1Q...
```

**Refresh Token**:
```bash
POST /api/token/refresh/
{
  "refresh": "eyJ0eXAiOiJKV1Q..."
}
```

### Role-Based Access Control

| Role         | Scope    | Permissions                                      |
|--------------|----------|--------------------------------------------------|
| ADMIN        | Company  | Full access to all brands & stores              |
| MANAGER      | Brand    | Manage brand settings, users, products          |
| SUPERVISOR   | Store    | Store operations, shift management              |
| CASHIER      | Store    | POS operations only (Edge)                      |
| KITCHEN_STAFF| Store    | Kitchen display & order management (Edge)       |
| WAITER       | Store    | Table service, orders (Edge)                    |

---

## 🧪 Testing

See **`TESTING_CHECKLIST.md`** for comprehensive testing guide.

**350+ Test Cases** covering:
- Unit tests (models, business logic)
- Integration tests (API, multi-model operations)
- Admin tests (Django admin functionality)
- Command tests (management commands)
- End-to-end tests (complete workflows)
- Performance tests (query benchmarks)
- Security tests (authentication, authorization, input validation)

**Run Tests** (when implemented):
```bash
python manage.py test
```

---

## 📝 API Documentation

**Base URL**: `http://localhost:8000/api/v1/`

### Core Endpoints

| Endpoint                         | Method | Description                     | Auth Required |
|----------------------------------|--------|---------------------------------|---------------|
| `/api/token/`                    | POST   | Obtain JWT token                | No            |
| `/api/token/refresh/`            | POST   | Refresh JWT token               | No            |
| `/api/v1/core/companies/sync/`   | GET    | Sync companies (incremental)    | Yes           |
| `/api/v1/core/brands/sync/`      | GET    | Sync brands (by brand_id)       | Yes           |
| `/api/v1/core/stores/sync/`      | GET    | Sync stores (by store_id)       | Yes           |
| `/api/v1/core/users/sync/`       | GET    | Sync users (by brand_id)        | Yes           |

**Query Parameters**:
- `last_sync`: ISO datetime (e.g., `2024-01-22T10:30:00Z`) for incremental sync
- `brand_id`: UUID (filter by brand)
- `store_id`: UUID (filter by store)

**Response Format**:
```json
{
  "count": 5,
  "last_sync": "2024-01-22T12:00:00Z",
  "data": [...]
}
```

**TODO**: Add OpenAPI schema with drf-spectacular

---

## 🚀 Deployment

### Development

```bash
python manage.py runserver
```

### Production (Docker Compose)

```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --noinput
```

### Environment Variables

See `.env.example` for required variables:
- `SECRET_KEY`: Django secret key
- `DEBUG`: True/False
- `DB_ENGINE`: postgresql / sqlite3
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `REDIS_URL`: redis://localhost:6379/0

---

## 🎊 **COMPLETE UI MANAGEMENT SYSTEM**

### ✅ **14 CRUD Modules - 100% COMPLETE!**

All master data management modules have been fully implemented with complete UI/UX:

#### **Core Master Data (4 Modules)**
- [x] **Dashboard** - System overview and quick stats
- [x] **Company Management** - Multi-tenant company setup (1 sample)
- [x] **Brand Management** - Brand configuration per company (1 sample)
- [x] **Store Management** - Store/outlet management (1 sample)

#### **Product Management (5 Modules)**
- [x] **Product Categories** - Hierarchical category tree (11 samples)
- [x] **Products** - Complete product catalog with pricing (17 samples)
- [x] **Modifiers** - Product customization options (5 samples)
- [x] **Table Areas** - Dining area management (7 samples)
- [x] **Kitchen Stations** - Kitchen workflow routing (4 samples)

#### **Customer & Marketing (2 Modules)**
- [x] **Members** - Loyalty program with points & tiers (5 samples)
- [x] **Promotions** - 12+ promotion types (5 samples)

#### **Inventory Management (3 Modules)**
- [x] **Inventory Items** - Raw materials & packaging (6 samples)
- [x] **Recipes (BOM)** - Bill of materials with yield factors (1 sample)
- [x] **Stock Movements** - Inventory tracking (read-only, 6 samples)

### 📊 **Sample Data Summary**
**Total Records**: **64** across 14 modules
- Company: 1 (Test Company)
- Brand: 1 (Test Brand)
- Store: 1 (Headquarters)
- Categories: 11 (Food, Beverage, Main Course, etc.)
- Products: 17 (Ayam Bakar, Nasi Goreng, Cappuccino, etc.)
- Modifiers: 5 (Spice Level, Add-ons, Size, etc.)
- Table Areas: 7 (Indoor, Outdoor, VIP, etc.)
- Kitchen Stations: 4 (Grill, Wok, Beverage, Dessert)
- Members: 5 (John Doe, Jane Smith, Ahmad Hidayat, etc.)
- Promotions: 5 (NEWYEAR2026, BOGO-COFFEE, CASHBACK10, etc.)
- Inventory Items: 6 (Chicken, Rice, Oil, Coffee, Milk, Cups)
- Recipes: 1 (Ayam Bakar Recipe)
- Stock Movements: 6 (IN, OUT, ADJUSTMENT, PRODUCTION)

### 🎨 **UI/UX Features**
- **HTMX Integration** - Partial page updates without full reload
- **Alpine.js Modals** - Smooth modal forms for create/edit
- **Real-time Search** - Instant search with debounce (500ms)
- **Advanced Filters** - Filter by company, brand, type, status
- **Pagination** - 10-20 items per page with page navigation
- **Color-Coded Badges** - Status indicators and type badges
- **Responsive Layout** - Mobile-friendly Tailwind CSS design
- **Toast Notifications** - Success/error messages
- **Form Validation** - Real-time client-side validation
- **Loading Spinners** - Better UX during async operations
- **Confirmation Dialogs** - Delete confirmations
- **Sidebar Navigation** - Collapsible menu with icons

### 🔗 **URL Structure**
All modules follow RESTful URL patterns:

```
/dashboard/                    # Dashboard overview
/company/                      # Company management
/brand/                        # Brand management
/store/                        # Store management
/products/                     # Product list
/products/create/              # Create product
/products/<uuid>/edit/         # Edit product
/products/<uuid>/delete/       # Delete product
/products/categories/          # Category management
/products/modifiers/           # Modifier management
/products/tableareas/          # Table area management
/products/kitchenstations/     # Kitchen station management
/members/                      # Member management
/promotions/                   # Promotion management
/inventory/items/              # Inventory item management
/inventory/recipes/            # Recipe/BOM management
/inventory/movements/          # Stock movement reports
```

### 🎯 **Technical Implementation**

#### **Backend (Django)**
- **Views**: Class-based and function-based views with `@login_required`
- **Forms**: Django ModelForms with validation
- **QuerySets**: Optimized with `select_related()` and `prefetch_related()`
- **Pagination**: Django Paginator with 10-20 items per page
- **Search**: Q objects for multi-field text search
- **Filters**: GET parameters for dynamic filtering
- **JSON Responses**: HTMX-compatible partial rendering

#### **Frontend (HTMX + Alpine.js + Tailwind)**
- **HTMX Attributes**: `hx-get`, `hx-post`, `hx-target`, `hx-swap`, `hx-trigger`
- **Alpine.js State**: Modal management, form handling, confirmations
- **Tailwind CSS**: Utility-first styling with responsive design
- **Font Awesome Icons**: Icon library for UI elements
- **Template Structure**: Base template with partials (_table.html, _form.html, list.html)

#### **Database Relationships**
- **Multi-Tenant**: Company → Brand → Store hierarchy
- **Foreign Keys**: Proper CASCADE/PROTECT constraints
- **Many-to-Many**: Products ↔ Categories, Products ↔ Modifiers
- **UUID Primary Keys**: Distributed system compatibility
- **Indexes**: Optimized for search and filter queries

### 🧪 **Testing Status**
- ✅ All CRUD operations tested via browser
- ✅ Search functionality verified
- ✅ Filter combinations validated
- ✅ Pagination tested with sample data
- ✅ Modal forms tested (create/edit/delete)
- ✅ HTMX partial updates confirmed
- ✅ Form validation tested (required fields, unique constraints)
- ✅ Multi-tenant data isolation verified

---

## 📈 Roadmap

### ✅ Completed (Phase 1-9) ✨ **NEW!**
- [x] Phase 1: Foundation & Multi-Tenant Core
- [x] Phase 2: Product Catalog & Tables
- [x] Phase 3: Member & Loyalty Program
- [x] Phase 4: Promotion Engine (12+ types)
- [x] Phase 5: Inventory & Recipe Management
- [x] Phase 6: Transaction Data Reception
- [x] Phase 7: Sync API (Core endpoints)
- [x] Phase 8: Management Commands
- [x] **Phase 9: Complete UI Implementation (14 CRUD Modules)** ⭐

### 🔄 In Progress
- [ ] Phase 10: Remaining API endpoints
  - [ ] Products API
  - [ ] Members API (bidirectional sync)
  - [ ] Promotions API
  - [ ] Inventory API
  - [ ] Transactions push API (Edge → HO)

### 📅 Upcoming
- [ ] Phase 11: Reporting & Analytics UI
- [ ] Phase 12: API Documentation (drf-spectacular/Swagger)
- [ ] Phase 13: Celery Beat (scheduled tasks)
- [ ] Phase 14: Performance Optimization
- [ ] Phase 15: Security Audit & Testing
- [ ] Phase 16: Load Testing & Production Deployment

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'feat: Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

**Commit Message Convention**:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Tests
- `chore:` Maintenance

---

## 📄 License

Proprietary - Yogya Group © 2026

---

## 📞 Support

For questions or issues, contact:
- **Email**: info@yogyagroup.com
- **Slack**: #pos-development

---

## 🙏 Acknowledgments

- Django Framework
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- All open-source contributors

---

## 🎯 **Business Value & Benefits**

### **For Developers**
- ✅ **Modern Tech Stack**: Django 5.0.1 + HTMX + Alpine.js + Tailwind CSS
- ✅ **Clean Architecture**: Separation of concerns, reusable components
- ✅ **RESTful APIs**: JWT authentication, incremental sync
- ✅ **Comprehensive Models**: 40+ models with proper relationships
- ✅ **Code Quality**: Consistent naming, docstrings, type hints
- ✅ **Development Speed**: CRUD scaffolding, template inheritance
- ✅ **Testing Ready**: Sample data, test scenarios prepared

### **For Business Users**
- ✅ **Complete Master Data Management**: All restaurant data in one place
- ✅ **Multi-Brand Support**: Manage multiple restaurant brands
- ✅ **Inventory Control**: Track ingredients, recipes, and costs
- ✅ **Member Loyalty**: Points, tiers, and customer retention
- ✅ **Flexible Promotions**: 12+ promotion types for marketing
- ✅ **Real-Time Reporting**: Transaction data from all stores (planned)
- ✅ **Cost Efficiency**: Centralized system, reduced IT overhead
- ✅ **Scalability**: Cloud-based, handles growth easily

### **For Operations**
- ✅ **User-Friendly UI**: Intuitive interface, minimal training
- ✅ **Fast Performance**: HTMX partial updates, optimized queries
- ✅ **Mobile Responsive**: Works on tablets and smartphones
- ✅ **Search & Filter**: Find data quickly
- ✅ **Audit Trail**: Track who changed what and when
- ✅ **Multi-Tenant**: Data isolation between companies
- ✅ **Offline Capable**: Edge servers work without internet (planned)

---

**Version**: 2.0 ⭐ **UI COMPLETE!**  
**Last Updated**: 2026-01-22  
**Status**: Development - **Phase 9 Complete (14 CRUD Modules with UI)** ✅  
**Next Phase**: API Completion & Reporting UI
