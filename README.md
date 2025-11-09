# PragatiDhara - Sustainable Route Optimization

🌱 **AI-Powered Route Optimization with Sustainability Focus**

PragatiDhara is a full-stack application that combines React frontend with Python FastAPI backend to provide intelligent, sustainable route optimization using reinforcement learning and energy-efficient computing.

## 🏗️ Architecture Overview

- **Frontend**: React 18 with custom hooks for backend integration
- **Backend**: FastAPI with sustainable AI services (RL Agent, Route Optimizer, OpenAI integration)
- **AI Services**: CPU-optimized reinforcement learning, A* pathfinding, quantized models
- **Energy Monitoring**: Real-time CPU/memory tracking with sustainability scoring

---

## 🚀 Quick Start Guide

### Prerequisites

Ensure you have the following installed:
- **Python 3.8+** (for backend)
- **Node.js 16+** and **npm** (for frontend React development)
- **Git** (for version control)

### 📁 Project Structure

```
PragatiDhara/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # Full backend with all services
│   ├── simple_main.py      # Simplified backend for testing
│   ├── requirements.txt    # Python dependencies
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── services/      # AI and optimization services
│   │   ├── models/        # Data models
│   │   └── core/          # Configuration and utilities
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API integration layer
│   │   └── components/    # React components
│   ├── index.html         # Standalone HTML version
│   └── package.json       # Node dependencies
└── README.md              # This file
```

---

## 🔧 Backend Setup & Launch

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run Backend Server

Choose one of these options:

#### Option A: Full Backend (Recommended)
```bash
python main.py
```

#### Option B: Simplified Backend (For testing)
```bash
python simple_main.py
```

### ✅ Backend Verification

Once started, you should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Test the backend:**
- Health Check: http://127.0.0.1:8000/health
- API Documentation: http://127.0.0.1:8000/docs
- Interactive API: http://127.0.0.1:8000/redoc

---

## 🎨 Frontend Setup & Launch

### Option 1: React Development Server (Requires Node.js)

#### Step 1: Navigate to Frontend Directory
```bash
cd frontend
```

#### Step 2: Install Dependencies
```bash
npm install
```

#### Step 3: Start Development Server
```bash
npm start
```

The React app will open at: **http://localhost:3000**

### Option 2: Standalone HTML Version (No Node.js required)

#### Step 1: Navigate to Frontend Directory
```bash
cd frontend
```

#### Step 2: Start Simple HTTP Server
```bash
# Using Python (if installed)
python -m http.server 3000

# Or using Node.js (if installed)
npx serve -p 3000
```

#### Step 3: Open in Browser
Navigate to: **http://localhost:3000/index.html**

---

## 🔗 Full Stack Integration

### 🚀 Easy Start (Recommended)

Use the provided startup scripts to launch both services automatically:

#### Windows (PowerShell - Recommended)
```powershell
.\start.ps1
```

#### Windows (Batch file)
```cmd
start.bat
```

#### macOS/Linux
```bash
chmod +x start.sh
./start.sh
```

These scripts will:
- Start both backend and frontend servers
- Check for port conflicts
- Open the application in your browser
- Provide helpful status information

### Manual Setup

If you prefer to start services manually:

1. **Start Backend** (Terminal 1):
   ```bash
   cd backend
   python main.py
   # Backend runs on http://127.0.0.1:8000
   ```

2. **Start Frontend** (Terminal 2):
   ```bash
   cd frontend
   python -m http.server 3000
   # Frontend runs on http://localhost:3000
   ```

3. **Open Application**: 
   - Navigate to **http://localhost:3000/index.html**
   - The frontend will automatically connect to the backend

### 🌐 Connection Status

The application includes real-time connection monitoring:
- **🌿 AI Backend Connected**: Backend is running and responsive
- **⚡ Offline Mode**: Using client-side processing as fallback
- **🔄 Connecting**: Establishing backend connection

---

## 🎯 Features & Usage

### Core Features

1. **Sustainable Route Optimization**
   - Real-time traffic analysis
   - AI-powered route recommendations
   - Energy-efficient processing

2. **Live Monitoring**
   - Backend health status
   - CPU and memory usage
   - Energy efficiency scoring
   - Sustainability grades

3. **Intelligent AI Services**
   - Reinforcement Learning agent
   - A* pathfinding algorithm
   - OpenAI integration for enhanced recommendations

### Using the Application

1. **Configure Route Points**: Select start and destination locations
2. **Adjust Parameters**: Use the Alpha slider to balance speed vs. eco-friendliness
3. **Plan Route**: Click "Plan RL-Optimized Route" to get AI recommendations
4. **Monitor Performance**: View real-time energy metrics and sustainability scores

---

## 🛠️ API Endpoints

### Backend API Routes

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/health` | GET | Backend health check |
| `/traffic` | GET | Current traffic data |
| `/optimize` | POST | Route optimization |
| `/metrics` | GET | Energy and performance metrics |

### Example API Usage

```bash
# Health check
curl http://127.0.0.1:8000/health

# Get traffic data
curl http://127.0.0.1:8000/traffic

# Route optimization
curl -X POST http://127.0.0.1:8000/optimize \
  -H "Content-Type: application/json" \
  -d '{"start_node": "A", "end_node": "J", "alpha": 0.7}'
```

---

## 🔍 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check Python version
python --version

# Install dependencies
pip install -r requirements.txt

# Try simplified backend
python simple_main.py
```

#### Frontend Connection Issues
- Ensure backend is running on http://127.0.0.1:8000
- Check browser console for error messages
- Try the standalone HTML version

#### Port Conflicts
- Backend: Change port in `main.py` or `simple_main.py`
- Frontend: Use different port with `python -m http.server 3001`

#### Permission Issues (Windows)
```bash
# Run as administrator or use different ports
python -m http.server 8080
```

### Performance Optimization

1. **Backend**: The application uses CPU-only processing for sustainability
2. **Caching**: Routes are cached to improve response times
3. **Quantization**: AI models use INT8 quantization for efficiency

---

## 🌱 Sustainability Features

### Energy Efficiency
- **CPU Optimization**: All AI processing optimized for CPU-only execution
- **Intelligent Caching**: Reduces redundant computations
- **Quantized Models**: Lower memory footprint and faster inference
- **Real-time Monitoring**: Track energy consumption and efficiency

### Green Computing Practices
- Minimal resource usage
- Efficient algorithms (A* pathfinding)
- Sustainable software architecture
- Energy-aware processing

---

## 📦 Dependencies

### Backend (Python)
```
fastapi>=0.104.1
uvicorn>=0.24.0
pydantic>=2.5.0
numpy>=1.24.3
scikit-learn>=1.3.0
psutil>=5.9.0
openai>=1.3.0
diskcache>=5.6.3
```

### Frontend (React)
```
react@18.2.0
react-dom@18.2.0
react-scripts@5.0.1
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both backend and frontend
5. Submit a pull request

---

## 📄 License

This project is part of the GreenMind Hackathon initiative for sustainable technology solutions.

---

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API documentation at http://127.0.0.1:8000/docs
3. Check browser console for frontend errors
4. Ensure both servers are running properly

**Happy Sustainable Computing! 🌱🚀**

---

## Vision & Mission

**Vision**: To make Indian cities cleaner, smarter, and more sustainable by transforming how citizens contribute to traffic management through AI-powered route optimization.

**Mission**: To create an intelligent mobility ecosystem where every commuter action contributes to reduced congestion, lower emissions, and collective sustainability goals through advanced reinforcement learning and energy-efficient computing.
