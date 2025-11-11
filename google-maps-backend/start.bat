@echo off
REM Google Maps Backend Setup and Launch Script for Windows
REM This script sets up the environment and starts the server

echo ========================================
echo Google Maps Backend Setup ^& Launch
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

echo ✅ Python detected
python --version

REM Check if we're in the right directory
if not exist "app\" (
    echo ❌ Please run this script from the google-maps-backend directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo ✅ Correct directory detected

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo ⚠️  .env file not found
    if exist "config.template" (
        echo Creating .env file from template...
        copy config.template .env
        echo.
        echo ⚠️  Please edit .env file and add your Google Maps API key
        echo Opening .env file for editing...
        start notepad .env
        echo.
        echo Press any key after you've configured your API key...
        pause >nul
    ) else (
        echo ❌ config.template not found. Please create .env file manually
        pause
        exit /b 1
    )
)

echo ✅ Configuration file found

REM Install dependencies
echo.
echo 📦 Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

REM Check if API key is configured
findstr /C:"your-api-key-here" .env >nul
if not errorlevel 1 (
    echo.
    echo ⚠️  WARNING: Google Maps API key appears to be default placeholder
    echo Please update your .env file with a valid API key
    echo.
    choice /C YN /M "Continue anyway (Y/N)"
    if errorlevel 2 exit /b 1
)

REM Start the server
echo.
echo 🚀 Starting Google Maps Backend Server...
echo Server will be available at: http://localhost:8001
echo API Documentation: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --reload --port 8001 --host 0.0.0.0

echo.
echo Server stopped.
pause