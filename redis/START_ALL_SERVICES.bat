@echo off
setlocal EnableDelayedExpansion
color 0B
title M3U Matrix - Start All Services

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║          M3U MATRIX - Starting All Redis Services               ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo Starting services in sequence...
echo.

REM Check if Redis is already running
tasklist /FI "IMAGENAME eq redis-server.exe" 2>NUL | find /I /N "redis-server.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ Redis server is already running
) else (
    echo [1/3] Starting Redis Server...
    start "M3U Matrix - Redis Server" /MIN cmd /c "redis-server config\redis.conf"
    timeout /t 2 >nul
    echo ✅ Redis Server started
)

echo.
echo [2/3] Starting API Server...
start "M3U Matrix - API Server" cmd /c "python api_server.py"
timeout /t 2 >nul
echo ✅ API Server starting on port 3000

echo.
echo [3/3] Starting Web Dashboard...
start "M3U Matrix - Dashboard" cmd /c "python dashboard.py"
timeout /t 2 >nul
echo ✅ Dashboard starting on port 8080

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    ALL SERVICES STARTED!
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 🎯 Services running:
echo.
echo    📦 Redis Server     : localhost:6379
echo    🚀 API Server       : http://localhost:3000
echo    🌐 Web Dashboard    : http://localhost:8080
echo.
echo Opening dashboard in browser...
timeout /t 3 >nul
start http://localhost:8080
echo.
echo Press any key to stop all services...
pause >nul

REM Stop all services
echo.
echo Stopping services...
taskkill /FI "WINDOWTITLE eq M3U Matrix - API Server" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq M3U Matrix - Dashboard" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq M3U Matrix - Redis Server" /F >nul 2>&1
echo ✅ All services stopped

endlocal
