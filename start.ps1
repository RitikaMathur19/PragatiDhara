# PragatiDhara Startup Script
# Sustainable AI Route Optimization Application

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   PragatiDhara - Sustainable AI App" -ForegroundColor Green  
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $Port)
        $listener.Start()
        $listener.Stop()
        return $false
    } catch {
        return $true
    }
}

Write-Host "[1/2] Starting Python Backend..." -ForegroundColor Yellow

# Check if backend port is available
if (Test-Port 8000) {
    Write-Host "⚠️  Port 8000 is already in use. Backend might already be running." -ForegroundColor Orange
} else {
    $backendPath = Join-Path $rootDir "backend"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; python simple_main.py" -WindowStyle Normal
    Write-Host "✅ Backend started on http://127.0.0.1:8000" -ForegroundColor Green
}

Write-Host "[2/2] Starting Frontend Server..." -ForegroundColor Yellow

# Check if frontend port is available  
if (Test-Port 3000) {
    Write-Host "⚠️  Port 3000 is already in use. Frontend might already be running." -ForegroundColor Orange
} else {
    $frontendPath = Join-Path $rootDir "frontend" 
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; python -m http.server 3000" -WindowStyle Normal
    Write-Host "✅ Frontend started on http://localhost:3000" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Services Status" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Frontend:  http://localhost:3000/index.html" -ForegroundColor Cyan
Write-Host "🚀 Backend:   http://127.0.0.1:8000" -ForegroundColor Cyan  
Write-Host "📚 API Docs:  http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host ""

# Wait a moment for services to start
Write-Host "Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "🎉 Opening application in browser..." -ForegroundColor Green
Start-Process "http://localhost:3000/index.html"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ PragatiDhara is now running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "   - Close the terminal windows to stop the servers" -ForegroundColor Gray
Write-Host "   - Check the connection indicator in the app" -ForegroundColor Gray
Write-Host "   - Visit /docs for API documentation" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit this script (services will keep running)..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")