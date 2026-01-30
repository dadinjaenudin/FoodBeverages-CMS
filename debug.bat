@echo off
echo ====================================
echo 🔍 F&B POS HO System - Debug Info
echo ====================================
echo.

echo 📊 Docker System Info:
docker --version
docker-compose --version
echo.

echo 🔍 Container Status:
docker-compose ps
echo.

echo 📝 Recent Logs (Web Service):
echo ====================================
docker-compose logs --tail=50 web
echo.

echo 📝 Recent Logs (Database):
echo ====================================
docker-compose logs --tail=20 db
echo.

echo 📝 Recent Logs (Redis):
echo ====================================
docker-compose logs --tail=20 redis
echo.

echo 🔍 Network Info:
docker network ls | findstr fnb
echo.

echo 💾 Volume Info:
docker volume ls | findstr fnb
echo.

echo 🖥️ System Resources:
docker system df
echo.

pause