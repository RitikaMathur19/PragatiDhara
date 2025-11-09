"""
Simplified API Routes for initial testing
"""

import time
import logging
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Simple request/response models
class RouteRequest(BaseModel):
    start_node: str
    end_node: str
    alpha: float = 1.0

class RouteResponse(BaseModel):
    path: List[str]
    total_time: float
    total_emissions: float
    green_points_score: int
    route_type: str

class TrafficResponse(BaseModel):
    traffic_factor: float
    incident_factor: float
    timestamp: float

# Simple endpoints for testing
@router.get("/health")
async def health_check():
    """Simple health check."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "message": "PragatiDhara Backend is running sustainably!"
    }

@router.get("/traffic/current")
async def get_traffic_data() -> TrafficResponse:
    """Get simulated traffic data."""
    import random
    return TrafficResponse(
        traffic_factor=round(random.uniform(0.2, 0.8), 3),
        incident_factor=round(random.uniform(0.0, 0.3), 3),
        timestamp=time.time()
    )

@router.post("/routes/optimize")
async def optimize_routes(request: RouteRequest) -> Dict[str, Any]:
    """Simple route optimization."""
    
    # Validate nodes
    valid_nodes = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'}
    if request.start_node not in valid_nodes or request.end_node not in valid_nodes:
        raise HTTPException(status_code=400, detail="Invalid node specified")
    
    if request.start_node == request.end_node:
        raise HTTPException(status_code=400, detail="Start and end must be different")
    
    # Simple mock routes
    routes = [
        RouteResponse(
            path=[request.start_node, 'D', request.end_node],
            total_time=15.0,
            total_emissions=800,
            green_points_score=85,
            route_type="fast"
        ),
        RouteResponse(
            path=[request.start_node, 'F', 'H', request.end_node],
            total_time=18.0,
            total_emissions=400,
            green_points_score=95,
            route_type="eco"
        ),
        RouteResponse(
            path=[request.start_node, 'E', request.end_node],
            total_time=16.5,
            total_emissions=600,
            green_points_score=90,
            route_type="rl-optimized"
        )
    ]
    
    return {
        "routes": [route.dict() for route in routes],
        "recommendation": "eco",
        "processing_time_ms": 25.0,
        "sustainability_score": 90
    }

@router.get("/metrics/energy")
async def get_energy_metrics():
    """Get energy metrics."""
    import psutil
    
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    
    return {
        "timestamp": time.time(),
        "cpu_usage_percent": cpu_usage,
        "memory_usage_percent": memory.percent,
        "energy_efficiency_score": max(0, 100 - cpu_usage),
        "sustainability_grade": "A" if cpu_usage < 50 else "B",
        "system_info": {
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(memory.total / (1024**3), 2)
        }
    }