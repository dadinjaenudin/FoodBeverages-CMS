@echo off
echo ====================================
echo 🍽️  F&B POS HO System - Stopping...
echo ====================================
echo.

echo 🛑 Stopping all services...
docker-compose down

echo.
echo ✅ All services stopped successfully!
echo.
pause