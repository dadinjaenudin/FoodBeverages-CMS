# 🚀 Quick Start Guide - F&B HO Management System

## Prerequisites
- Docker & Docker Compose installed
- OR: Python 3.12+, PostgreSQL 15+, Redis 7+

---

## Option 1: Docker (Recommended) 🐳

### 1. Clone & Setup
```bash
git clone https://github.com/dadinjaenudin/FoodBeverages-CMS.git
cd FoodBeverages-CMS
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env if needed (default values work for Docker)
```

### 3. Start Services
```bash
# Start all services (web, db, redis, celery)
docker-compose up -d

# Check logs
docker-compose logs -f web
```

### 4. Run Migrations & Create Superuser
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Generate sample data (optional)
docker-compose exec web python manage.py generate_sample_data
```

### 5. Access the Application
- **HO Dashboard**: http://localhost:8000/
- **Django Admin**: http://localhost:8000/admin/
- **API Docs (Swagger)**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

### 6. Stop Services
```bash
docker-compose down

# Stop and remove volumes (reset database)
docker-compose down -v
```

---

## Option 2: Local Development 💻

### 1. Clone Repository
```bash
git clone https://github.com/dadinjaenudin/FoodBeverages-CMS.git
cd FoodBeverages-CMS
```

### 2. Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL Database
```bash
# Create database
createdb fnb_ho_db

# Or use SQLite for development (update .env)
```

### 5. Environment Configuration
```bash
cp .env.example .env
```

Edit `.env`:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# For SQLite (Development)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# For PostgreSQL (Production)
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=fnb_ho_db
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

### 6. Run Migrations
```bash
python manage.py migrate
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
```

### 8. Generate Sample Data (Optional)
```bash
python manage.py generate_sample_data
```

### 9. Run Development Server
```bash
python manage.py runserver
```

### 10. Run Celery (Optional - in separate terminals)
```bash
# Terminal 1: Celery Worker
celery -A config worker -l info

# Terminal 2: Celery Beat (scheduled tasks)
celery -A config beat -l info
```

### 11. Access the Application
- **HO Dashboard**: http://localhost:8000/
- **Django Admin**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/docs/

---

## 📝 Default Login Credentials

After running `generate_sample_data`:

### Admin User
- **Username**: `admin`
- **Password**: `admin123`

### Manager User
- **Username**: `manager`
- **Password**: `manager123`

### Cashier User
- **Username**: `cashier`
- **Password**: `cashier123`

---

## 🗂️ Project Structure

```
FoodBeverages-CMS/
├── config/              # Django settings & configuration
├── core/                # Multi-tenant core (Company, Brand, Store, User)
├── products/            # Product catalog
├── members/             # Member & loyalty
├── promotions/          # Promotion engine
├── inventory/           # Inventory & recipes
├── transactions/        # Transaction data (Edge → HO)
├── analytics/           # Reporting & analytics
├── dashboard/           # Dashboard UI
├── templates/           # HTML templates
│   ├── base.html
│   ├── auth/
│   ├── dashboard/
│   └── partials/
├── static/              # Static files (CSS, JS, images)
├── docker-compose.yml   # Docker orchestration
├── Dockerfile           # Docker image
├── requirements.txt     # Python dependencies
└── manage.py            # Django CLI
```

---

## 🎯 Key Features

### ✅ Implemented
1. **Multi-Tenant Architecture** (Company → Brand → Store)
2. **Product Catalog** (Categories, Products, Modifiers)
3. **Member & Loyalty Program** (Points, Tiers, Transactions)
4. **Promotion Engine** (12+ promotion types, stacking, explainability)
5. **Inventory & BOM** (Raw materials, recipes, movements)
6. **Transaction Management** (Bills, Payments, Refunds)
7. **REST API (HO ↔ Edge)** (40+ endpoints with JWT authentication)
8. **Reporting & Analytics** (7 report types)
9. **Celery Automation** (Point expiry, daily reports)
10. **API Documentation** (Swagger + ReDoc)
11. **Dashboard UI** (Django + HTMX + Alpine.js + Tailwind CSS)

---

## 📊 Dashboard Features

### Navigation (3-Level Menu)
- **Dashboard** - Key metrics and charts
- **Master Data**
  - Company Management
  - Brand & Store
  - Product Catalog
  - Members
  - Promotions
  - Inventory
- **Reports & Analytics**
  - Sales Report
  - Product Performance
  - Member Analytics
- **User Management**
- **Settings**

### UI Features
- ✅ Responsive design (mobile & desktop)
- ✅ Collapsible sidebar
- ✅ 3-level menu hierarchy
- ✅ Icon-based CRUD buttons
- ✅ Real-time dashboard metrics
- ✅ Charts (Chart.js)
- ✅ Pagination ready
- ✅ HTMX for smooth interactions
- ✅ Alpine.js for reactive components

---

## 🧪 Testing

### Run Tests
```bash
# All tests
python manage.py test

# Specific app
python manage.py test core
python manage.py test products

# With coverage
coverage run --source='.' manage.py test
coverage report
```

### Check Code Quality
```bash
python manage.py check
python manage.py check --deploy
```

---

## 📚 API Documentation

### Access API Docs
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Get JWT Token
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Use API with Token
```bash
curl -X GET http://localhost:8000/api/v1/core/companies/sync/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔧 Management Commands

### Expire Member Points
```bash
# Dry run (preview)
python manage.py expire_member_points --dry-run

# Execute
python manage.py expire_member_points
```

### Generate Sample Data
```bash
# Generate sample data
python manage.py generate_sample_data

# Clear and regenerate
python manage.py generate_sample_data --clear
```

---

## 🐛 Troubleshooting

### Docker Issues

**Problem**: Port already in use
```bash
# Check ports
docker-compose ps
lsof -i :8000

# Use different port
docker-compose down
# Edit docker-compose.yml ports: "8001:8000"
docker-compose up -d
```

**Problem**: Database connection refused
```bash
# Wait for DB to be ready
docker-compose logs db

# Restart services
docker-compose restart
```

### Local Development Issues

**Problem**: Module not found
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem**: Migration conflicts
```bash
# Reset migrations (development only)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
python manage.py makemigrations
python manage.py migrate
```

---

## 🚀 Next Steps

### Frontend Development
- [ ] Create CRUD pages for master data
- [ ] Implement HTMX partial views
- [ ] Add pagination components
- [ ] Create form modals
- [ ] Add search & filter

### Backend Enhancements
- [ ] Complete API endpoint testing
- [ ] Add rate limiting
- [ ] Implement caching (Redis)
- [ ] Add monitoring (Prometheus/Grafana)
- [ ] Performance optimization

### Production Deployment
- [ ] Setup production server
- [ ] Configure HTTPS/SSL
- [ ] Setup CI/CD pipeline
- [ ] Add backup automation
- [ ] Monitoring & logging

---

## 📞 Support

- **GitHub**: https://github.com/dadinjaenudin/FoodBeverages-CMS
- **Issues**: https://github.com/dadinjaenudin/FoodBeverages-CMS/issues
- **Documentation**: See README.md and TESTING_CHECKLIST.md

---

## 📄 License

Proprietary - All rights reserved

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-22
