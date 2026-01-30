@echo off
REM ============================================================
REM Create Promotion Sample Data - Docker Version
REM ============================================================

echo.
echo ============================================================
echo  Creating Promotion Sample Data
echo ============================================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Check if containers are running
docker-compose ps | findstr "web" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker containers are not running!
    echo Starting containers...
    docker-compose up -d
    echo Waiting for containers to start...
    timeout /t 10 /nobreak >nul
)

echo [INFO] Running create_promotion_samples command...
echo.

REM Run the Django management command inside the container
docker-compose exec web python manage.py create_promotion_samples

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo  SUCCESS! Promotion samples created.
    echo ============================================================
    echo.
    echo  Access promotions at: http://localhost:8002/promotions/
    echo.
) else (
    echo.
    echo ============================================================
    echo  ERROR! Failed to create promotion samples.
    echo ============================================================
    echo.
    echo  Please check:
    echo  - Docker containers are running
    echo  - Database is accessible
    echo  - Company, Brand, and Stores exist
    echo.
)

pause
