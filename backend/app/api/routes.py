"""
API Routes for PragatiDhara Sustainable Backend
"""

import time
import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from app.models.api_models import (
    TrafficStateRequest, RouteOptimizationRequest, ModelUpdateRequest,
    OpenAIRequest, RLPredictionResponse, RouteOptimizationResponse,
    TrafficDataResponse, OpenAIResponse, ServiceMetricsResponse,
    EnergyMetricsResponse, HealthCheckResponse, ErrorResponse
)
from app.services.rl_agent import RLAgentService, TrafficState
from app.services.route_optimizer import RouteOptimizerService
from app.services.openai_service import SustainableOpenAIService
from app.core.energy_monitor import EnergyMonitor

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Global service instances (will be injected from main app)
from app import main

def get_services():
    """Get service instances from main app."""
    return main.rl_service, main.route_service, main.openai_service, main.energy_monitor


# Dependency injection helpers
def get_rl_service() -> RLAgentService:
    """Get RL service instance."""
    if not rl_service or not rl_service.is_ready():
        raise HTTPException(status_code=503, detail="RL Agent service not ready")
    return rl_service


def get_route_service() -> RouteOptimizerService:
    """Get route optimization service instance."""
    if not route_service or not route_service.is_ready():
        raise HTTPException(status_code=503, detail="Route Optimizer service not ready")
    return route_service


def get_openai_service() -> SustainableOpenAIService:
    """Get OpenAI service instance."""
    if not openai_service or not openai_service.is_ready():
        raise HTTPException(status_code=503, detail="OpenAI service not ready")
    return openai_service


# Route Optimization Endpoints
@router.post("/routes/optimize", response_model=RouteOptimizationResponse)
async def optimize_routes(
    request: RouteOptimizationRequest,
    route_svc: RouteOptimizerService = Depends(get_route_service)
) -> RouteOptimizationResponse:
    """
    Optimize routes with multiple algorithms and sustainability focus.
    
    Returns the top 3 route options ranked by green points score.
    """
    try:
        start_time = time.time()
        
        # Get optimized routes
        routes = await route_svc.optimize_routes(
            start_node=request.start_node,
            end_node=request.end_node,
            alpha=request.alpha
        )
        
        # Convert to response format
        route_responses = []
        for route in routes:
            route_responses.append({
                "path": route.path,
                "total_time": route.total_time,
                "total_distance": route.total_distance,
                "total_emissions": route.total_emissions,
                "green_points_score": route.green_points_score,
                "route_type": route.route_type,
                "processing_time_ms": route.processing_time_ms,
                "cache_hit": route.cache_hit
            })
        
        # Determine recommendation
        best_route = routes[0] if routes else None
        recommendation = best_route.route_type if best_route else "no-route-found"
        
        # Calculate sustainability score
        sustainability_score = (
            sum(r.green_points_score for r in routes) // len(routes) if routes else 0
        )
        
        total_processing_time = (time.time() - start_time) * 1000
        
        return RouteOptimizationResponse(
            routes=route_responses,
            recommendation=recommendation,
            total_processing_time_ms=total_processing_time,
            sustainability_score=min(100, sustainability_score)
        )
        
    except Exception as e:
        logger.error(f"Route optimization error: {e}")
        raise HTTPException(status_code=500, detail=f"Route optimization failed: {str(e)}")


@router.get("/traffic/current", response_model=TrafficDataResponse)
async def get_current_traffic(
    route_svc: RouteOptimizerService = Depends(get_route_service)
) -> TrafficDataResponse:
    """Get current real-time traffic data and recommendations."""
    try:
        traffic_data = await route_svc.get_traffic_data()
        
        # Generate recommendations based on traffic conditions
        recommendations = []
        if traffic_data["traffic_factor"] > 0.7:
            recommendations.append("🚦 High traffic detected - consider eco routes")
        if traffic_data["incident_factor"] > 0.5:
            recommendations.append("⚠️ Traffic incidents reported - allow extra time")
        if traffic_data["is_peak_hour"]:
            recommendations.append("🕐 Peak hour - eco routes may save time and emissions")
        if not recommendations:
            recommendations.append("✅ Good traffic conditions - all route types available")
        
        return TrafficDataResponse(
            timestamp=traffic_data["timestamp"],
            traffic_factor=traffic_data["traffic_factor"],
            incident_factor=traffic_data["incident_factor"],
            hour_of_day=traffic_data["hour_of_day"],
            is_peak_hour=traffic_data["is_peak_hour"],
            weather_factor=traffic_data["weather_factor"],
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Traffic data error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get traffic data: {str(e)}")


# RL Agent Endpoints
@router.post("/rl/predict", response_model=RLPredictionResponse)
async def predict_optimal_alpha(
    request: TrafficStateRequest,
    rl_svc: RLAgentService = Depends(get_rl_service)
) -> RLPredictionResponse:
    """Predict optimal emissions weighting factor using RL agent."""
    try:
        # Convert request to traffic state
        traffic_state = TrafficState(
            traffic_factor=request.traffic_factor,
            incident_factor=request.incident_factor,
            time_of_day=request.time_of_day,
            day_of_week=request.day_of_week,
            weather_factor=request.weather_factor,
            road_capacity=request.road_capacity
        )
        
        # Get RL prediction
        prediction = await rl_svc.predict_alpha(traffic_state)
        
        return RLPredictionResponse(
            alpha=prediction.alpha,
            confidence=prediction.confidence,
            processing_time_ms=prediction.processing_time_ms,
            energy_cost=prediction.energy_cost,
            cache_hit=prediction.cache_hit,
            model_version="cpu-optimized-v1"
        )
        
    except Exception as e:
        logger.error(f"RL prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"RL prediction failed: {str(e)}")


@router.post("/rl/update")
async def update_rl_model(
    request: ModelUpdateRequest,
    background_tasks: BackgroundTasks,
    rl_svc: RLAgentService = Depends(get_rl_service)
) -> Dict[str, Any]:
    """Update RL model with new experience data."""
    try:
        # Convert request to traffic state
        traffic_state = TrafficState(
            traffic_factor=request.traffic_state.traffic_factor,
            incident_factor=request.traffic_state.incident_factor,
            time_of_day=request.traffic_state.time_of_day,
            day_of_week=request.traffic_state.day_of_week,
            weather_factor=request.traffic_state.weather_factor,
            road_capacity=request.traffic_state.road_capacity
        )
        
        # Schedule model update in background for performance
        background_tasks.add_task(
            rl_svc.update_model,
            traffic_state,
            request.alpha_used,
            request.actual_performance
        )
        
        return {
            "status": "update_scheduled",
            "message": "Model update scheduled for background processing",
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"RL model update error: {e}")
        raise HTTPException(status_code=500, detail=f"Model update failed: {str(e)}")


# OpenAI Integration Endpoints
@router.post("/ai/insights", response_model=OpenAIResponse)
async def get_route_insights(
    request: OpenAIRequest,
    openai_svc: SustainableOpenAIService = Depends(get_openai_service)
) -> OpenAIResponse:
    """Get AI-powered route insights and recommendations."""
    try:
        # Generate insights based on context
        context = request.context
        
        if "route_data" in context:
            response = await openai_svc.generate_route_insights(context["route_data"])
        elif "traffic_data" in context:
            response = await openai_svc.analyze_traffic_patterns(context["traffic_data"])
        else:
            response = await openai_svc.get_sustainability_tips(context)
        
        return OpenAIResponse(
            content=response.content,
            tokens_used=response.tokens_used,
            processing_time_ms=response.processing_time_ms,
            energy_cost=response.energy_cost,
            cache_hit=response.cache_hit,
            model_used=response.model_used
        )
        
    except Exception as e:
        logger.error(f"AI insights error: {e}")
        raise HTTPException(status_code=500, detail=f"AI insights failed: {str(e)}")


# Monitoring and Metrics Endpoints
@router.get("/metrics/services", response_model=Dict[str, ServiceMetricsResponse])
async def get_service_metrics() -> Dict[str, ServiceMetricsResponse]:
    """Get performance metrics for all services."""
    try:
        metrics = {}
        
        # RL Service metrics
        if rl_service and rl_service.is_ready():
            rl_metrics = rl_service.get_service_metrics()
            metrics["rl_agent"] = ServiceMetricsResponse(
                service_name="RL Agent",
                status=rl_metrics["service_status"],
                performance_metrics=rl_metrics["performance"],
                sustainability_metrics=rl_metrics["sustainability"],
                cache_metrics=rl_metrics.get("cache_stats")
            )
        
        # Route Service metrics
        if route_service and route_service.is_ready():
            route_metrics = route_service.get_service_metrics()
            metrics["route_optimizer"] = ServiceMetricsResponse(
                service_name="Route Optimizer",
                status=route_metrics["service_status"],
                performance_metrics=route_metrics["performance"],
                sustainability_metrics={"cpu_optimized": True, "multi_objective": True},
                cache_metrics=route_metrics.get("cache_stats")
            )
        
        # OpenAI Service metrics
        if openai_service and openai_service.is_ready():
            ai_metrics = openai_service.get_service_metrics()
            metrics["openai"] = ServiceMetricsResponse(
                service_name="OpenAI Integration",
                status=ai_metrics["service_status"],
                performance_metrics=ai_metrics["performance"],
                sustainability_metrics=ai_metrics["sustainability"],
                cache_metrics=ai_metrics.get("cache_stats")
            )
        
        return metrics
        
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/metrics/energy", response_model=EnergyMetricsResponse)
async def get_energy_metrics() -> EnergyMetricsResponse:
    """Get current energy and sustainability metrics."""
    try:
        if not energy_monitor:
            raise HTTPException(status_code=503, detail="Energy monitoring not available")
        
        current_metrics = energy_monitor.get_current_metrics()
        sustainability_score = energy_monitor.get_sustainability_score()
        
        return EnergyMetricsResponse(
            timestamp=current_metrics["timestamp"],
            cpu_usage_percent=current_metrics["cpu"]["usage_percent"],
            memory_usage_percent=current_metrics["memory"]["usage_percent"],
            energy_efficiency_score=current_metrics["sustainability"]["energy_efficiency_score"],
            sustainability_grade=sustainability_score["grade"],
            recommendations=energy_monitor._get_efficiency_recommendations(),
            system_info=current_metrics["cpu"]
        )
        
    except Exception as e:
        logger.error(f"Energy metrics error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get energy metrics: {str(e)}")


# Error handler
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP_ERROR",
            message=exc.detail,
            timestamp=time.time()
        ).dict()
    )


@router.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_ERROR",
            message="An unexpected error occurred",
            timestamp=time.time()
        ).dict()
    )