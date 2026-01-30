@echo off
REM F&B POS HO System - Docker Runner Script for Windows
REM Usage: run-docker.bat [dev|prod|stop|logs|shell|build]

setlocal enabledelayedexpansion

set COMPOSE_FILE=docker-compose.yml
set PROJECT_NAME=fnb-ho

REM Colors (limited in Windows CMD)
set GREEN=[92m
set RED=[91m
set YELLOW=[93m
set BLUE=[94m
set NC=[0m

if "%1"=="" (
    set COMMAND=dev
) else (
    set COMMAND=%1
)

echo.
echo %BLUE%======================================%NC%
echo %BLUE%🍽️  F&B POS HO System - Docker%NC%
echo %BLUE%======================================%NC%
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo %RED%✗ Docker is not installed. Please install Docker Desktop first.%NC%
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo %RED%✗ Docker Compose is not installed. Please install Docker Compose first.%NC%
    pause
    exit /b 1
)

echo %GREEN%✓ Docker and Docker Compose are available%NC%
echo.

if "%COMMAND%"=="dev" goto :start_dev
if "%COMMAND%"=="prod" goto :start_prod
if "%COMMAND%"=="stop" goto :stop_services
if "%COMMAND%"=="logs" goto :show_logs
if "%COMMAND%"=="shell" goto :open_shell
if "%COMMAND%"=="build" goto :build_services
if "%COMMAND%"=="help" goto :show_help
if "%COMMAND%"=="-h" goto :show_help
if "%COMMAND%"=="--help" goto :show_help

echo %RED%✗ Unknown command: %COMMAND%%NC%
goto :show_help

:start_dev
echo %BLUE%ℹ Starting F&B POS HO System in DEVELOPMENT mode...%NC%
echo.

REM Build and start services
echo Building Docker images...
docker-compose -f %COMPOSE_FILE% -p %PROJECT_NAME% build

echo Starting services...
docker-compose -f %COMPOSE_FILE% -p %PROJECT_NAME% up -d

echo.
echo %GREEN%✓ Development environment started!%NC%
echo.
echo %BLUE%ℹ Services:%NC%
echo   🌐 Django App: http://localhost:8002
echo   📚 API Docs (Swagger): http://localhost:8002/api/docs/
echo   📖 API Docs (ReDoc): http://localhost:8002/api/redoc/
echo   🔧 Admin Panel: http://localhost:8002/admin/
echo   🗄️  PostgreSQL: localhost:5432
echo   🔴 Redis: localhost:6379
echo.
echo %BLUE%ℹ Default Admin Credentials:%NC%
echo   Username: admin
echo   Password: admin123
echo.
echo %BLUE%ℹ Use 'run-docker.bat logs' to view logs%NC%
echo %BLUE%ℹ Use 'run-docker.bat stop' to stop services%NC%
echo.
pause
goto :eof

:start_prod
echo %BLUE%ℹ Starting F&B POS HO System in PRODUCTION mode...%NC%
echo.

REM Build and start all services
echo Building Docker images...
docker-compose -f %COMPOSE_FILE% -p %PROJECT_NAME% build

echo Starting services...
docker-compose -f %COMPOSE_FILE% -p %PROJECT_NAME% up -d

echo.
echo %GREEN%✓ Production environment started!%NC%
echo.
echo %BLUE%ℹ Services:%NC%
echo   🌐 Django App: http://localhost:8002
echo   📚 API Docs (Swagger): http://localhost:8002/api/docs/
echo   📖 API Docs (ReDoc): http://localhost:8002/api/redoc/
echo   🔧 Admin Panel: http://localhost:8002/admin/
echo   🗄️  PostgreSQL: localhost:5432
echo   🔴 Redis: localhost:6379
echo.
echo %BLUE%ℹ Use 'run-docker.bat logs' to view logs%NC%
echo %BLUE%ℹ Use 'run-docker.bat stop' to stop services%NC%
echo.
pause
goto :eof

:stop_services
echo %BLUE%ℹ Stopping F&B POS HO System...%NC%
echo.

docker-compose -f %COMPOSE_FILE% -p %PROJECT_NAME% down

echo.
echo %GREEN%✓ All services stopped!%NC%
echo.
pause
goto :eof

:show_logs
echo %BLUE%ℹ Showing logs for F&B POS HO System...%NC%
echo.

docker-compose -f %COMPOSE_FILE% -p %PROJECT_NAME% logs -f
goto :eof

:open_shell
echo %BLUE%ℹ Opening Django shell...%NC%
echo.

docker-compose -f %COMPOSE_FILE% -p %PROJECT_NAME% exec web python manage.py shell
goto :eof

:build_services
echo %BLUE%ℹ Building Docker images...%NC%
echo.

docker-compose -f %COMPOSE_FILE% -p %PROJECT_NAME% build --no-cache

echo.
echo %GREEN%✓ Docker images built successfully!%NC%
echo.
pause
goto :eof

:show_help
echo Usage: %0 [COMMAND]
echo.
echo Commands:
echo   dev      Start development environment (default)
echo   prod     Start production environment
echo   stop     Stop all services
echo   logs     Show and follow logs
echo   shell    Open Django shell
echo   build    Build Docker images
echo   help     Show this help message
echo.
echo Examples:
echo   %0 dev     # Start development environment
echo   %0 prod    # Start production environment
echo   %0 logs    # View logs
echo   %0 stop    # Stop all services
echo.
pause
goto :eof