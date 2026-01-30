@echo off
REM ============================================================
REM Delete Promotions - Docker Version
REM ============================================================

echo.
echo ============================================================
echo  Delete Promotions Tool
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

REM Show menu
echo Select deletion option:
echo.
echo  1. Delete ALL promotions
echo  2. Delete sample promotions only
echo  3. Delete inactive promotions
echo  4. Delete expired promotions
echo  5. Delete by code (manual input)
echo  6. Delete by type (manual input)
echo  0. Cancel
echo.

set /p choice="Enter choice (0-6): "

if "%choice%"=="0" (
    echo Cancelled.
    pause
    exit /b 0
)

if "%choice%"=="1" (
    echo.
    echo [WARNING] This will delete ALL promotions!
    docker-compose exec web python manage.py delete_promotions --all
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Deleting sample promotions...
    docker-compose exec web python manage.py delete_promotions --samples --confirm
    goto end
)

if "%choice%"=="3" (
    echo.
    echo Deleting inactive promotions...
    docker-compose exec web python manage.py delete_promotions --inactive --confirm
    goto end
)

if "%choice%"=="4" (
    echo.
    echo Deleting expired promotions...
    docker-compose exec web python manage.py delete_promotions --expired --confirm
    goto end
)

if "%choice%"=="5" (
    echo.
    set /p code="Enter promotion code: "
    docker-compose exec web python manage.py delete_promotions --code %code%
    goto end
)

if "%choice%"=="6" (
    echo.
    echo Available types:
    echo   - percent_discount
    echo   - amount_discount
    echo   - happy_hour
    echo   - buy_x_get_y
    echo   - package
    echo   - threshold_tier
    echo.
    set /p type="Enter promotion type: "
    docker-compose exec web python manage.py delete_promotions --type %type%
    goto end
)

echo Invalid choice!

:end
echo.
pause
