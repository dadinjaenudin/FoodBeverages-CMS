# 🐳 Docker Setup - F&B POS HO System

Panduan lengkap untuk menjalankan F&B POS HO System menggunakan Docker.

## 📋 Prerequisites

### 1. Install Docker Desktop
- **Windows**: Download dari [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
- **macOS**: Download dari [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
- **Linux**: Install Docker Engine dan Docker Compose

### 2. Verify Installation
```bash
docker --version
docker-compose --version
```

## 🚀 Quick Start

### Windows
```cmd
# Start development environment
run-docker.bat dev

# Stop services
run-docker.bat stop

# View logs
run-docker.bat logs
```

### Linux/macOS
```bash
# Make script executable
chmod +x run-docker.sh

# Start development environment
./run-docker.sh dev

# Stop services
./run-docker.sh stop

# View logs
./run-docker.sh logs
```

### Manual Docker Compose
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild images
docker-compose build --no-cache
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│              Docker Network             │
│  ┌──────────────────────────────────┐  │
│  │         fnb_ho_web               │  │
│  │    Django + DRF + Swagger        │  │
│  │         Port: 8002               │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │         fnb_ho_db                │  │
│  │      PostgreSQL 16               │  │
│  │         Port: 5432               │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │        fnb_ho_redis              │  │
│  │         Redis 7                  │  │
│  │         Port: 6379               │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │    fnb_ho_celery_worker          │  │
│  │      Background Tasks            │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │     fnb_ho_celery_beat           │  │
│  │      Scheduled Tasks             │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## 🌐 Services & Ports

| Service | Container Name | Port | Description |
|---------|----------------|------|-------------|
| Django Web | fnb_ho_web | 8002 | Main application |
| PostgreSQL | fnb_ho_db | 5432 | Database |
| Redis | fnb_ho_redis | 6379 | Cache & message broker |
| Celery Worker | fnb_ho_celery_worker | - | Background tasks |
| Celery Beat | fnb_ho_celery_beat | - | Scheduled tasks |

## 📚 API Documentation

Setelah aplikasi berjalan, akses dokumentasi API di:

- **Swagger UI**: http://localhost:8002/api/docs/
- **ReDoc**: http://localhost:8002/api/redoc/
- **OpenAPI Schema**: http://localhost:8002/api/schema/

## 🔐 Default Credentials

### Admin Panel
- **URL**: http://localhost:8002/admin/
- **Username**: `admin`
- **Password**: `admin123`

### Database
- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `fnb_ho_db`
- **Username**: `postgres`
- **Password**: `postgres123`

## 🛠️ Development Commands

### Django Management Commands
```bash
# Open Django shell
docker-compose exec web python manage.py shell

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Generate sample data
docker-compose exec web python manage.py generate_sample_data

# Collect static files
docker-compose exec web python manage.py collectstatic
```

### Database Commands
```bash
# Connect to PostgreSQL
docker-compose exec db psql -U postgres -d fnb_ho_db

# Backup database
docker-compose exec db pg_dump -U postgres fnb_ho_db > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres fnb_ho_db < backup.sql
```

### Redis Commands
```bash
# Connect to Redis CLI
docker-compose exec redis redis-cli

# Monitor Redis
docker-compose exec redis redis-cli monitor
```

## 📊 Monitoring

### Container Status
```bash
# Check running containers
docker-compose ps

# View container logs
docker-compose logs [service_name]

# Follow logs in real-time
docker-compose logs -f [service_name]
```

### Resource Usage
```bash
# View container resource usage
docker stats

# View disk usage
docker system df
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
netstat -tulpn | grep :8002

# Kill process using the port
sudo kill -9 $(lsof -t -i:8002)
```

#### 2. Database Connection Issues
```bash
# Check database container logs
docker-compose logs db

# Restart database container
docker-compose restart db
```

#### 3. Permission Issues (Linux/macOS)
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Make scripts executable
chmod +x run-docker.sh
```

#### 4. Build Issues
```bash
# Clean build (remove cache)
docker-compose build --no-cache

# Remove all containers and volumes
docker-compose down -v
docker system prune -a
```

### Reset Everything
```bash
# Stop and remove all containers, networks, volumes
docker-compose down -v

# Remove all images
docker rmi $(docker images -q)

# Clean system
docker system prune -a --volumes

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

## 🚀 Production Deployment

### Environment Variables
Copy `.env.docker` to `.env.production` and update:

```bash
# Production settings
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Secure database credentials
DB_PASSWORD=your_secure_password

# Email configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

### SSL/HTTPS Setup
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d
```

## 📝 Logs

### Log Locations
- **Django**: `logs/django.log`
- **Docker**: Use `docker-compose logs`

### Log Levels
- **Development**: DEBUG
- **Production**: INFO

## 🔄 Backup & Restore

### Database Backup
```bash
# Create backup
docker-compose exec db pg_dump -U postgres fnb_ho_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker-compose exec -T db psql -U postgres fnb_ho_db < backup_20240122_120000.sql
```

### Media Files Backup
```bash
# Backup media files
docker cp fnb_ho_web:/app/media ./media_backup

# Restore media files
docker cp ./media_backup fnb_ho_web:/app/media
```

## 📞 Support

Jika mengalami masalah:

1. Periksa logs: `docker-compose logs -f`
2. Restart services: `docker-compose restart`
3. Rebuild images: `docker-compose build --no-cache`
4. Reset everything: Follow "Reset Everything" section

## 📖 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)