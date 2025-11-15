@echo off
echo Installing required Python packages for Redis services...
echo.

pip install fastapi uvicorn redis aioredis python-multipart

echo.
echo ✅ Installation complete!
echo.
echo You can now run START_ALL_SERVICES.bat
pause
