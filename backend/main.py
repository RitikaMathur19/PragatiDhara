"""
PragatiDhara Backend - Sustainable AI Route Optimization
Main FastAPI application with CPU-optimized, energy-efficient design
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

import psutil
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import get_settings
from app.core.energy_monitor import EnergyMonitor
from app.services.rl_agent import RLAgentService
from app.services.route_optimizer import RouteOptimizerService
from app.services.openai_service import SustainableOpenAIService

# Configure logging for sustainability tracking
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global services
energy_monitor = EnergyMonitor()
rl_service = None
route_service = None
openai_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan with energy monitoring and service initialization."""
    global rl_service, route_service
    
    # Startup
    logger.info("🌱 Starting PragatiDhara Sustainable Backend...")
    
    # Initialize energy monitoring
    energy_monitor.start_monitoring()
    
    # Initialize CPU-optimized services
    rl_service = RLAgentService()
    route_service = RouteOptimizerService()
    openai_service = SustainableOpenAIService()
    
    # Load models with CPU optimization
    await rl_service.initialize()
    await route_service.initialize()
    await openai_service.initialize()
    
    # Log startup metrics
    cpu_count = psutil.cpu_count()
    memory = psutil.virtual_memory()
    logger.info(f"🖥️  System: {cpu_count} CPU cores, {memory.total // (1024**3)}GB RAM")
    logger.info(f"⚡ Energy-efficient mode: CPU-only processing enabled")
    logger.info(f"🚀 Backend ready on sustainable infrastructure")
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down sustainable backend...")
    
    # Stop energy monitoring and log final metrics
    final_metrics = energy_monitor.stop_monitoring()
    logger.info(f"📊 Session Energy Metrics: {final_metrics}")
    
    # Cleanup services
    if rl_service:
        await rl_service.cleanup()
    if route_service:
        await route_service.cleanup()
    if openai_service:
        await openai_service.cleanup()
    
    logger.info("✅ Sustainable shutdown complete")


def create_app() -> FastAPI:
    """Create FastAPI application with sustainable configuration."""
    settings = get_settings()
    
    app = FastAPI(
        title="PragatiDhara Sustainable Backend",
        description="CPU-optimized AI route optimization with energy monitoring",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Add compression for sustainability (reduce bandwidth)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add energy monitoring middleware
    @app.middleware("http")
    async def energy_monitoring_middleware(request: Request, call_next):
        """Monitor energy consumption per request."""
        start_time = time.time()
        start_cpu = psutil.cpu_percent()
        
        response = await call_next(request)
        
        # Calculate request metrics
        duration = time.time() - start_time
        end_cpu = psutil.cpu_percent()
        cpu_usage = abs(end_cpu - start_cpu)
        
        # Log sustainable metrics
        if duration > 1.0:  # Log slow requests
            logger.warning(f"⚠️  Slow request: {request.url.path} took {duration:.2f}s")
        
        # Add sustainability headers
        response.headers["X-Processing-Time"] = str(round(duration * 1000, 2))
        response.headers["X-CPU-Usage"] = str(round(cpu_usage, 2))
        response.headers["X-Energy-Efficient"] = "true"
        
        return response
    
    # Include API routes
    app.include_router(router, prefix="/api/v1")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check() -> Dict[str, Any]:
        """Health check with sustainability metrics."""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "energy_efficient": True,
            "services": {
                "rl_agent": rl_service is not None and rl_service.is_ready(),
                "route_optimizer": route_service is not None and route_service.is_ready(),
            }
        }
    
    # Energy metrics endpoint
    @app.get("/metrics/energy")
    async def energy_metrics() -> Dict[str, Any]:
        """Get current energy and performance metrics."""
        return energy_monitor.get_current_metrics()
    
    return app


# Create the application instance
app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1,  # Single worker for energy efficiency
        access_log=True,
        log_level="info",
    )