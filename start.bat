@echo off
echo ====================================
echo 🍽️  F&B POS HO System - Starting...
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

echo 🛑 Stopping existing containers...
docker-compose down

echo.
echo 🔨 Building and starting services...
docker-compose up -d --build

echo.
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo ✅ Services started successfully!
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
echo 📊 Database Info:
echo   Host: localhost:5432
echo   Database: fnb_ho_db
echo   Username: postgres
echo   Password: postgres123
echo.
echo 📝 To view logs: logs.bat
echo 🛑 To stop: stop.bat
echo.
echo 🔍 Checking container status...
docker-compose ps
echo.
pause