@echo off
echo ====================================
echo 🐍 F&B POS HO System - Django Shell
echo ====================================
echo.

REM Check if services are running
docker-compose ps | findstr "fnb_ho_web" >nul
if errorlevel 1 (
    echo ❌ Services are not running. Please start them first with start.bat
    pause
    exit /b 1
)

echo ✅ Services are running
echo.

echo 🐍 Opening Django shell...
echo.

REM Open Django shell inside the web container
docker-compose exec web python manage.py shell