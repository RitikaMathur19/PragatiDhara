# Google Maps Backend Setup and Launch Script for PowerShell
# This script sets up the environment and starts the server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Google Maps Backend Setup & Launch" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "app\")) {
    Write-Host "❌ Please run this script from the google-maps-backend directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Correct directory detected" -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
    
    if (Test-Path "config.template") {
        Write-Host "Creating .env file from template..." -ForegroundColor Cyan
        Copy-Item "config.template" ".env"
        
        Write-Host
        Write-Host "⚠️  Please edit .env file and add your Google Maps API key" -ForegroundColor Yellow
        Write-Host "Opening .env file for editing..." -ForegroundColor Cyan
        Start-Process notepad ".env"
        
        Write-Host
        Read-Host "Press Enter after you've configured your API key"
    } else {
        Write-Host "❌ config.template not found. Please create .env file manually" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "✅ Configuration file found" -ForegroundColor Green

# Install dependencies
Write-Host
Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
$installResult = pip install -r requirements.txt 

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green

# Check if API key is configured
$envContent = Get-Content ".env" -Raw
if ($envContent -match "your-api-key-here") {
    Write-Host
    Write-Host "⚠️  WARNING: Google Maps API key appears to be default placeholder" -ForegroundColor Yellow
    Write-Host "Please update your .env file with a valid API key" -ForegroundColor Yellow
    Write-Host
    
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -notmatch "^[Yy]") {
        exit 1
    }
}

# Start the server
Write-Host
Write-Host "🚀 Starting Google Maps Backend Server..." -ForegroundColor Green
Write-Host "Server will be available at: http://localhost:8001" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host

try {
    uvicorn app.main:app --reload --port 8001 --host 0.0.0.0
} catch {
    Write-Host
    Write-Host "❌ Failed to start server: $_" -ForegroundColor Red
} finally {
    Write-Host
    Write-Host "Server stopped." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}