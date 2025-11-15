@echo off
setlocal EnableDelayedExpansion
color 0B
title M3U Matrix - Redis Installation for Windows

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║          M3U MATRIX - Redis Installation (Windows)              ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

echo Redis will be installed using Python's redis-server package.
echo This provides a Windows-compatible Redis server.
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed!
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    INSTALLING REDIS DEPENDENCIES
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

echo Installing redis-py (Python Redis client)...
pip install redis
echo.

echo Installing redis-server for Windows...
pip install redis-server
echo.

echo ✅ Redis packages installed!
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    CREATING REDIS CONFIGURATION
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Create redis config directory
if not exist "config" mkdir config

REM Create redis.conf
(
echo # M3U Matrix Redis Configuration
echo.
echo bind 127.0.0.1
echo protected-mode yes
echo port 6379
echo.
echo # Persistence
echo save 900 1
echo save 300 10
echo save 60 10000
echo.
echo # Memory
echo maxmemory 512mb
echo maxmemory-policy allkeys-lru
echo.
echo # Logging
echo loglevel notice
echo logfile "redis.log"
echo.
echo # Database
echo databases 16
) > config\redis.conf

echo ✅ Created: config\redis.conf
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    CREATING STARTUP SCRIPTS
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Create Redis startup script
(
echo @echo off
echo title M3U Matrix - Redis Server
echo echo Starting Redis Server...
echo echo.
echo redis-server config\redis.conf
echo pause
) > start_redis.bat

echo ✅ Created: start_redis.bat
echo.

REM Create Redis CLI script
(
echo @echo off
echo title M3U Matrix - Redis CLI
echo redis-cli
) > redis_cli.bat

echo ✅ Created: redis_cli.bat
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo    INSTALLATION COMPLETE!
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ✅ Redis is installed and configured!
echo.
echo To start Redis:
echo    └─ Double-click: start_redis.bat
echo.
echo To access Redis CLI:
echo    └─ Double-click: redis_cli.bat
echo.
echo Configuration file:
echo    └─ config\redis.conf
echo.
echo Redis will run on: localhost:6379
echo.
pause
endlocal
