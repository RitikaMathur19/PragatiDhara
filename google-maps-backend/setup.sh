#!/bin/bash

# Google Maps Backend Setup Script

echo "🚀 Setting up Google Maps Backend API..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo "📥 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create environment file
echo "⚙️ Setting up configuration..."
if [ ! -f ".env" ]; then
    cp config.template .env
    echo "✅ Created .env file from template"
    echo "📝 Please edit .env and add your Google Maps API key"
else
    echo "⚠️ .env file already exists"
fi

# Create logs directory
mkdir -p logs

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file and add your Google Maps API key"
echo "2. Get API key from: https://console.cloud.google.com/google/maps-apis"
echo "3. Enable required APIs:"
echo "   - Maps JavaScript API"
echo "   - Directions API"
echo "   - Distance Matrix API"
echo "   - Geocoding API"
echo "4. Run the server: uvicorn app.main:app --reload --host 0.0.0.0 --port 8001"
echo ""
echo "🔗 Useful commands:"
echo "  Start server: uvicorn app.main:app --reload --port 8001"
echo "  Run tests: pytest tests/ -v"
echo "  API docs: http://localhost:8001/docs"
echo "  Health check: http://localhost:8001/health"
echo ""