#!/bin/bash

# PragatiDhara Startup Script
# Sustainable AI Route Optimization Application

echo ""
echo "========================================"
echo "   PragatiDhara - Sustainable AI App"
echo "========================================"
echo ""

# Get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

echo "[1/2] Starting Python Backend..."

# Check if backend port is available
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use. Backend might already be running."
else
    cd "$DIR/backend"
    # Start backend in background
    if command -v python3 &> /dev/null; then
        python3 simple_main.py &
    else
        python simple_main.py &
    fi
    BACKEND_PID=$!
    echo "✅ Backend started on http://127.0.0.1:8000 (PID: $BACKEND_PID)"
fi

echo "[2/2] Starting Frontend Server..."

# Check if frontend port is available
if check_port 3000; then
    echo "⚠️  Port 3000 is already in use. Frontend might already be running."
else
    cd "$DIR/frontend"
    # Start frontend server in background
    if command -v python3 &> /dev/null; then
        python3 -m http.server 3000 &
    else
        python -m http.server 3000 &
    fi
    FRONTEND_PID=$!
    echo "✅ Frontend started on http://localhost:3000 (PID: $FRONTEND_PID)"
fi

echo ""
echo "========================================"
echo "   Services Status"
echo "========================================"
echo ""
echo "🌐 Frontend:  http://localhost:3000/index.html"
echo "🚀 Backend:   http://127.0.0.1:8000"
echo "📚 API Docs:  http://127.0.0.1:8000/docs"
echo ""

# Wait a moment for services to start
echo "Waiting for services to initialize..."
sleep 3

echo ""
echo "🎉 Opening application in browser..."

# Try to open browser (different commands for different systems)
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000/index.html
elif command -v open &> /dev/null; then
    open http://localhost:3000/index.html  
elif command -v start &> /dev/null; then
    start http://localhost:3000/index.html
else
    echo "Please open http://localhost:3000/index.html in your browser"
fi

echo ""
echo "========================================"
echo "✅ PragatiDhara is now running!"
echo "========================================"
echo ""
echo "💡 Tips:"
echo "   - Use Ctrl+C to stop this script and kill services"
echo "   - Check the connection indicator in the app"
echo "   - Visit /docs for API documentation"
echo ""

# Keep script running and handle Ctrl+C
trap 'echo ""; echo "Stopping services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo "✅ Services stopped. Goodbye!"; exit' INT

echo "Press Ctrl+C to stop all services and exit..."
wait