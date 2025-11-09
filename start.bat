@echo off
echo.
echo ========================================
echo   PragatiDhara - Sustainable AI App
echo ========================================
echo.
echo Starting both Backend and Frontend...
echo.

echo [1/2] Starting Python Backend...
cd /d "%~dp0backend"
start "PragatiDhara Backend" cmd /k "python simple_main.py"

echo [2/2] Starting Frontend Server...
cd /d "%~dp0frontend"
start "PragatiDhara Frontend" cmd /k "python -m http.server 3000"

echo.
echo ========================================
echo   Services Starting!
echo ========================================
echo.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:3000/index.html
echo API Docs: http://127.0.0.1:8000/docs
echo.
echo Press any key to open the application...
pause >nul

start http://localhost:3000/index.html

echo.
echo Both services are running!
echo Close the terminal windows to stop the servers.
echo.