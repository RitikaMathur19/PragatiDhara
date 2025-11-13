"""
FastAPI main application
Google Maps Routes API Backend
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import uuid
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from .config import get_settings, app_info
from .api.routes import router as routes_router
from .api.green_credits_routes import router as green_credits_router
from .services.google_maps import get_google_maps_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Google Maps Backend API")
    logger.info(f"🔧 Debug mode: {settings.debug_mode}")
    logger.info(f"🌍 API prefix: {settings.api_prefix}")
    logger.info(f"📍 Maps region: {settings.maps_region}")
    
    # Initialize services
    gmaps_service = get_google_maps_service()
    health_check = await gmaps_service.health_check()
    logger.info(f"📊 Google Maps service health: {health_check['status']}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Google Maps Backend API")


# Create FastAPI application
app = FastAPI(
    title=app_info.title,
    description=app_info.description,
    version=app_info.version,
    contact=app_info.contact,
    license_info=app_info.license_info,
    openapi_tags=app_info.tags_metadata,
    lifespan=lifespan,
    debug=settings.debug_mode
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

# Trusted Host Middleware (security)
if not settings.debug_mode:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
    )


# Request tracking middleware
@app.middleware("http")
async def request_tracking_middleware(request: Request, call_next):
    """Track requests for monitoring and rate limiting"""
    start_time = time.time()
    request_id = str(uuid.uuid4())[:8]
    
    # Add request ID to headers
    request.state.request_id = request_id
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = round((time.time() - start_time) * 1000, 2)
    
    # Add response headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log request
    logger.info(
        f"Request {request_id}: {request.method} {request.url.path} "
        f"- {response.status_code} - {process_time}ms"
    )
    
    return response


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "http_error",
                "message": exc.detail,
                "status_code": exc.status_code,
                "request_id": getattr(request.state, 'request_id', None),
                "timestamp": time.time()
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "internal_error",
                "message": "An internal server error occurred",
                "request_id": getattr(request.state, 'request_id', None),
                "timestamp": time.time()
            }
        }
    )


# Health check endpoints
@app.get("/health", tags=["health"])
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "google_maps_backend",
        "version": app_info.version,
        "timestamp": time.time()
    }


@app.get("/health/detailed", tags=["health"])
async def detailed_health_check():
    """Detailed health check with service status"""
    gmaps_service = get_google_maps_service()
    gmaps_health = await gmaps_service.health_check()
    
    return {
        "status": "healthy" if gmaps_health["status"] == "healthy" else "degraded",
        "service": "google_maps_backend",
        "version": app_info.version,
        "timestamp": time.time(),
        "services": {
            "google_maps": gmaps_health
        },
        "configuration": {
            "debug_mode": settings.debug_mode,
            "api_prefix": settings.api_prefix,
            "maps_region": settings.maps_region,
            "rate_limit_per_minute": settings.rate_limit_per_minute
        }
    }


@app.get("/", tags=["health"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Google Maps Routes API Backend",
        "version": app_info.version,
        "documentation": "/docs",
        "health_check": "/health",
        "api_prefix": settings.api_prefix,
        "timestamp": time.time()
    }


# API Routes
app.include_router(
    routes_router,
    prefix=settings.api_prefix,
    dependencies=[]
)

# Green Credits Routes
app.include_router(
    green_credits_router,
    prefix=settings.api_prefix,
    dependencies=[]
)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Additional startup operations"""
    logger.info("🔄 Running startup operations...")
    
    # Test Google Maps API connection
    try:
        gmaps_service = get_google_maps_service()
        health_result = await gmaps_service.health_check()
        if health_result["status"] == "healthy":
            logger.info("✅ Google Maps API connection verified")
        else:
            logger.warning("⚠️ Google Maps API connection issue detected")
    except Exception as e:
        logger.error(f"❌ Google Maps API connection failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting server on {settings.api_host}:{settings.api_port}")
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug_mode,
        access_log=settings.enable_access_logs,
        log_level=settings.log_level.lower()
    )