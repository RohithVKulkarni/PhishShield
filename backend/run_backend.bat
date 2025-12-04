@echo off
echo ========================================
echo PhishShield Backend Startup Script
echo ========================================
echo.

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and add it to your system PATH
    pause
    exit /b 1
)
echo.

echo Installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo Starting Backend Server...
echo Backend will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
