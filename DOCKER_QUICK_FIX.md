# 🔧 Docker Quick Fix Guide

## Common Error: "exec /app/entrypoint.sh: no such file or directory"

### Problem
Container exits with code 255 and error message:
```
exec /app/entrypoint.sh: no such file or directory
```

### Root Causes
1. **Line ending issues** (Windows CRLF vs Unix LF)
2. **Docker build cache** (old layers cached)
3. **File permissions** (not executable)
4. **File not copied** (missing in Dockerfile)

---

## 🚀 Quick Fix (3 Methods)

### Method 1: Automated Script (RECOMMENDED)
```bash
# Run the rebuild script
./docker-rebuild.sh
```

This script will:
- ✅ Stop all containers
- ✅ Remove old images
- ✅ Fix line endings
- ✅ Rebuild with no cache
- ✅ Start services
- ✅ Test connectivity

---

### Method 2: Manual Fix
```bash
# Step 1: Stop containers
docker compose down

# Step 2: Fix line endings (choose one)
# Option A: If you have dos2unix
dos2unix entrypoint.sh

# Option B: Using sed (works on all Unix systems)
sed -i 's/\r$//' entrypoint.sh

# Step 3: Make executable
chmod +x entrypoint.sh

# Step 4: Rebuild without cache
docker compose build --no-cache

# Step 5: Start services
docker compose up -d

# Step 6: Check logs
docker compose logs -f
```

---

### Method 3: Clean Rebuild (Nuclear Option)
```bash
# Stop everything
docker compose down -v

# Remove ALL Docker resources (⚠️ deletes all containers, images, volumes)
docker system prune -a --volumes -f

# Rebuild
docker compose build --no-cache
docker compose up -d
```

---

## 🔍 Verification Steps

### 1. Check Container Status
```bash
docker compose ps
```

Expected output:
```
NAME                    STATUS
fnb_ho_web              Up 10 seconds
fnb_ho_db               Up 10 seconds (healthy)
fnb_ho_redis            Up 10 seconds (healthy)
fnb_ho_celery_worker    Up 10 seconds
fnb_ho_celery_beat      Up 10 seconds
```

### 2. Check Logs
```bash
# All services
docker compose logs

# Specific service
docker compose logs web

# Follow logs (real-time)
docker compose logs -f web
```

### 3. Test Web Service
```bash
# Check if web is responding
curl -I http://localhost:8000

# Should return:
# HTTP/1.1 302 Found (redirect to login)
# or
# HTTP/1.1 200 OK
```

### 4. Access Application
Open browser:
- http://localhost:8000
- Login: admin / admin123

---

## 🐛 Debugging Tips

### Check if entrypoint.sh exists in container
```bash
docker compose run --rm web ls -la /app/entrypoint.sh
```

Expected output:
```
-rwxr-xr-x 1 appuser appuser 1630 Jan 22 23:16 /app/entrypoint.sh
```

### Check line endings
```bash
file entrypoint.sh
```

Expected output:
```
entrypoint.sh: Bourne-Again shell script, ASCII text executable
```

If you see "CRLF":
```
entrypoint.sh: Bourne-Again shell script, ASCII text executable, with CRLF line terminators
```

Then fix it:
```bash
sed -i 's/\r$//' entrypoint.sh
```

### Inspect Docker image
```bash
# Build image
docker compose build web

# Inspect layers
docker history foodbeverages-cms_web:latest

# Run interactive shell
docker compose run --rm --entrypoint /bin/bash web
```

Inside container:
```bash
ls -la /app/entrypoint.sh
cat /app/entrypoint.sh
```

---

## 🔄 Alternative: Disable Entrypoint (Temporary)

If you need to start the container quickly without entrypoint:

### Edit docker-compose.yml
```yaml
services:
  web:
    # ... other config ...
    entrypoint: []  # Disable entrypoint
    command: |
      bash -c "
        python manage.py migrate &&
        python manage.py runserver 0.0.0.0:8000
      "
```

### Or use command line
```bash
docker compose run --rm --entrypoint "" web python manage.py migrate
docker compose run --rm --entrypoint "" web python manage.py runserver 0.0.0.0:8000
```

---

## 📋 Prevention Checklist

To avoid this issue in the future:

- [ ] Always use LF line endings (Unix format)
- [ ] Configure Git to handle line endings:
  ```bash
  git config --global core.autocrlf input  # On Linux/Mac
  git config --global core.autocrlf true   # On Windows
  ```
- [ ] Add `.gitattributes` file:
  ```
  * text=auto
  *.sh text eol=lf
  entrypoint.sh text eol=lf
  ```
- [ ] Use `sed -i 's/\r$//'` in Dockerfile
- [ ] Always rebuild with `--no-cache` after changes
- [ ] Check file permissions: `chmod +x entrypoint.sh`

---

## 🆘 Still Not Working?

### 1. Check Docker Version
```bash
docker --version
docker compose version
```

Minimum required:
- Docker: 20.10+
- Docker Compose: 2.0+

### 2. Check System Resources
```bash
docker system df
docker stats
```

Ensure you have:
- CPU: 2+ cores available
- RAM: 4+ GB available
- Disk: 10+ GB free

### 3. Check Logs in Detail
```bash
# Build logs
docker compose build --progress=plain

# Container logs with timestamps
docker compose logs --timestamps web

# Follow specific service
docker compose logs -f --tail=100 web
```

### 4. Test Individual Services
```bash
# Test database
docker compose up db
docker compose exec db pg_isready -U postgres

# Test Redis
docker compose up redis
docker compose exec redis redis-cli ping
```

---

## 📞 Get Help

If issue persists:

1. **Copy full error logs**:
   ```bash
   docker compose logs > docker-logs.txt
   ```

2. **Check Docker info**:
   ```bash
   docker info > docker-info.txt
   ```

3. **Share on GitHub Issues** with:
   - OS and version
   - Docker version
   - docker-compose.yml
   - Full error logs
   - Steps already tried

---

## ✅ Success Indicators

You'll know it's working when:

1. **Containers are running**:
   ```bash
   docker compose ps
   # All show "Up" status
   ```

2. **Logs show success**:
   ```bash
   docker compose logs web | grep "Initialization complete"
   ```

3. **Web is accessible**:
   ```bash
   curl http://localhost:8000
   # Returns HTML or redirects (302)
   ```

4. **Database migrations ran**:
   ```bash
   docker compose logs web | grep "Running migrations"
   ```

5. **Superuser created**:
   ```bash
   docker compose logs web | grep "Superuser"
   ```

---

**Last Updated**: 2026-01-22  
**For**: F&B POS HO System  
**Documentation**: See DOCKER_DEPLOYMENT.md for complete guide
