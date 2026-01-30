# 🍽️ F&B POS HO System (Head Office / Cloud)

**Multi-Tenant Cloud-Based Head Office System for F&B POS**

[![Django](https://img.shields.io/badge/Django-5.0.1-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14.0-blue.svg)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-red.svg)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

---

## 🚀 Quick Start with Docker

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### 1. Clone & Start
```bash
git clone <repository-url>
cd FoodBeverages-CMS

# Windows
start.bat

# Linux/macOS
chmod +x run-docker.sh
./run-docker.sh dev
```

### 2. Access Application
- **🌐 Main App**: http://localhost:8002
- **📚 API Docs (Swagger)**: http://localhost:8002/api/docs/
- **📖 API Docs (ReDoc)**: http://localhost:8002/api/redoc/
- **🔧 Admin Panel**: http://localhost:8002/admin/

### 3. Default Credentials
- **Username**: `admin`
- **Password**: `admin123`

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
│  │ REST API (JWT Auth) + Swagger Docs               │  │
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

### 5. **API Documentation** 📚
- **Swagger UI**: Interactive API documentation
- **ReDoc**: Beautiful API documentation
- **OpenAPI 3.0**: Standard API specification
- **JWT Authentication**: Secure API access
- **Comprehensive Examples**: Request/response samples

---

## 🛠️ Tech Stack

### **Backend**
- **Framework**: Django 5.0.1
- **API**: Django REST Framework 3.14+
- **Database**: PostgreSQL 16+ (production), SQLite (development)
- **Cache**: Redis (via django-redis)
- **Task Queue**: Celery + Redis (scheduled jobs)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **API Docs**: drf-spectacular (OpenAPI 3.0)

### **Frontend** ⭐
- **UI Framework**: HTMX 1.17+ (partial page updates)
- **JavaScript**: Alpine.js 3.x (reactive components)
- **CSS**: Tailwind CSS 3.x (utility-first)

### **DevOps**
- **Containerization**: Docker + Docker Compose
- **Web Server**: Gunicorn + Nginx (production)
- **Monitoring**: Flower (Celery monitoring)
- **Testing**: pytest + pytest-django

---

## 🐳 Docker Commands

### Basic Commands
```bash
# Start development environment
start.bat                    # Windows
./run-docker.sh dev         # Linux/macOS

# Stop all services
stop.bat                    # Windows
./run-docker.sh stop       # Linux/macOS

# View logs
logs.bat                    # Windows
./run-docker.sh logs       # Linux/macOS

# Run tests
test.bat                    # Windows
docker-compose exec web pytest

# Django shell
shell.bat                   # Windows
docker-compose exec web python manage.py shell
```

### Manual Docker Compose
```bash
# Build and start
docker-compose up -d --build

# Stop and remove
docker-compose down

# View logs
docker-compose logs -f

# Execute commands
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

---

## 📚 API Documentation

### Swagger UI
- **URL**: http://localhost:8002/api/docs/
- **Features**: Interactive testing, authentication, examples
- **Authentication**: JWT Bearer token

### ReDoc
- **URL**: http://localhost:8002/api/redoc/
- **Features**: Beautiful documentation, search, navigation

### OpenAPI Schema
- **URL**: http://localhost:8002/api/schema/
- **Format**: OpenAPI 3.0 JSON

### API Testing
See [API Test Examples](api_test_examples.md) for detailed examples.

---

## 🔐 Authentication

### JWT Token Flow
1. **Obtain Token**: `POST /api/token/`
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```

2. **Use Token**: Add to headers
   ```
   Authorization: Bearer <access_token>
   ```

3. **Refresh Token**: `POST /api/token/refresh/`
   ```json
   {
     "refresh": "<refresh_token>"
   }
   ```

---

## 🧪 Testing

### Run Tests
```bash
# Inside Docker
test.bat                    # Windows
docker-compose exec web pytest

# Local development
pytest -v --tb=short
pytest --cov=. --cov-report=html
```

### Test Structure
- **Unit Tests**: Model logic, business rules
- **Integration Tests**: API endpoints, workflows
- **End-to-End Tests**: Complete user journeys

---

## 📊 Monitoring

### Application Monitoring
- **Django Admin**: http://localhost:8002/admin/
- **API Health**: http://localhost:8002/api/health/
- **Database**: PostgreSQL on port 5432
- **Cache**: Redis on port 6379

### Celery Monitoring
- **Flower**: http://localhost:5555 (with monitoring profile)
- **Beat Schedule**: Automatic task scheduling
- **Worker Status**: Background task processing

---

## 🚀 Deployment

### Development
```bash
# Start development environment
start.bat
```

### Production
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# With monitoring
docker-compose --profile production --profile monitoring up -d
```

### Environment Variables
- **Development**: `.env.docker`
- **Production**: `.env.production`

---

## 📁 Project Structure

```
FoodBeverages-CMS/
├── 🐳 Docker Configuration
│   ├── docker-compose.yml          # Main compose file
│   ├── docker-compose.dev.yml      # Development
│   ├── docker-compose.prod.yml     # Production
│   ├── Dockerfile                  # Application image
│   ├── entrypoint.sh              # Container startup
│   └── requirements.txt           # Python dependencies
│
├── ⚙️ Configuration
│   ├── config/
│   │   ├── settings.py            # Django settings
│   │   ├── urls.py               # URL routing
│   │   ├── celery.py             # Celery config
│   │   └── tasks.py              # Scheduled tasks
│   └── .env.docker               # Environment variables
│
├── 🏢 Core Apps
│   ├── core/                     # Multi-tenant core
│   ├── products/                 # Product catalog
│   ├── members/                  # Loyalty program
│   ├── promotions/               # Promotion engine
│   ├── inventory/                # Inventory & recipes
│   ├── transactions/             # Transaction data
│   └── analytics/                # Reports & analytics
│
├── 🎨 Frontend
│   ├── templates/                # HTML templates
│   ├── static/                   # CSS, JS, images
│   └── media/                    # User uploads
│
├── 📚 Documentation
│   ├── README.md                 # This file
│   ├── DOCKER_SETUP.md          # Docker guide
│   ├── api_test_examples.md     # API examples
│   └── *.md                     # Other docs
│
└── 🧪 Testing
    ├── conftest.py              # Test configuration
    ├── pytest.ini              # Pytest settings
    └── */tests.py              # Test files
```

---

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Start development environment: `start.bat`
4. Make changes and test: `test.bat`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open Pull Request

### Code Standards
- **Python**: Black formatting, flake8 linting
- **Django**: Follow Django best practices
- **API**: RESTful design, proper HTTP status codes
- **Testing**: Write tests for new features
- **Documentation**: Update API docs and README

---

## 📞 Support

### Documentation
- **Docker Setup**: [DOCKER_SETUP.md](DOCKER_SETUP.md)
- **API Examples**: [api_test_examples.md](api_test_examples.md)
- **Testing Guide**: [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md)

### Troubleshooting
1. **Services not starting**: Check Docker Desktop is running
2. **Port conflicts**: Stop other services using ports 8002, 5432, 6379
3. **Database issues**: Run `docker-compose restart db`
4. **Permission issues**: Check file permissions and Docker settings

### Contact
- **Email**: dev@company.com
- **Documentation**: https://docs.yourdomain.com
- **Support**: https://support.yourdomain.com

---

## 📄 License

This project is proprietary software. All rights reserved.

---

**🍽️ F&B POS HO System - Powering Multi-Brand Restaurant Operations**