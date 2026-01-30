@echo off
echo ====================================
echo 🔄 F&B POS HO System - Clean Rebuild
echo ====================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo ✅ Docker is running
echo.

echo 🛑 Stopping and removing all containers...
docker-compose down -v

echo.
echo 🧹 Cleaning up Docker images...
docker-compose build --no-cache

echo.
echo 🔨 Starting services...
docker-compose up -d

echo.
echo ⏳ Waiting for services to be ready...
timeout /t 15 /nobreak >nul

echo.
echo ✅ Clean rebuild completed!
echo.
echo 🌐 Application URLs:
echo   - Main App: http://localhost:8002
echo   - API Docs (Swagger): http://localhost:8002/api/docs/
echo   - API Docs (ReDoc): http://localhost:8002/api/redoc/
echo   - Admin Panel: http://localhost:8002/admin/
echo.
echo 🔐 Default Admin Credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo 🔍 Checking container status...
docker-compose ps
echo.
pause