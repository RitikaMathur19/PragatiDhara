"""
Routes API endpoints for Google Maps backend
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from fastapi.responses import JSONResponse
import time
import uuid
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..models.route_models import (
    RouteRequest, RouteComparisonRequest, OptimizedRouteResponse,
    RouteComparisonResponse, Route, RouteAlternative, TravelMode,
    OptimizationMode, Location, LocationInput
)
from ..services.google_maps import get_google_maps_service, GoogleMapsService
from ..services.route_strategy import RouteStrategyEngine, RouteOptimizer
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(
    prefix="/routes",
    tags=["routes"],
    responses={404: {"description": "Not found"}}
)


def get_gmaps_service() -> GoogleMapsService:
    """Dependency to get Google Maps service"""
    return get_google_maps_service()


@router.post("/optimize", response_model=OptimizedRouteResponse)
async def optimize_route(
    request: RouteRequest,
    background_tasks: BackgroundTasks,
    req: Request,
    gmaps_service: GoogleMapsService = Depends(get_gmaps_service)
):
    """
    Calculate optimized routes with multiple alternatives
    
    This endpoint provides intelligent route optimization considering:
    - Travel mode preferences (driving, walking, transit, cycling)
    - Optimization criteria (fastest, shortest, eco-friendly, balanced)
    - Real-time traffic conditions
    - Environmental impact calculations
    - Alternative route suggestions
    """
    start_time = time.time()
    request_id = getattr(req.state, 'request_id', str(uuid.uuid4())[:8])
    
    try:
        logger.info(f"Route optimization request {request_id}: {request.origin} → {request.destination}")
        
        # Calculate primary route
        directions_result = await gmaps_service.calculate_directions(request)
        
        if not directions_result or directions_result[0]['status'] != 'OK':
            raise HTTPException(
                status_code=400,
                detail="Failed to calculate route. Please check your locations."
            )
        
        # Process primary route
        primary_route_data = directions_result[0]['routes'][0]
        primary_route = await _process_route_data(
            primary_route_data, 
            request.travel_mode,
            gmaps_service
        )
        
        # Process alternative routes
        alternatives = []
        if request.alternatives and len(directions_result[0]['routes']) > 1:
            for i, alt_route_data in enumerate(directions_result[0]['routes'][1:], 1):
                alt_route = await _process_route_data(
                    alt_route_data,
                    request.travel_mode, 
                    gmaps_service
                )
                
                # Calculate comparison metrics
                comparison_metrics = _calculate_route_comparison(primary_route, alt_route)
                recommendation_score = _calculate_recommendation_score(
                    alt_route, 
                    request.optimization_mode,
                    comparison_metrics
                )
                
                alternatives.append(RouteAlternative(
                    route=alt_route,
                    comparison_to_primary=comparison_metrics,
                    recommendation_score=recommendation_score
                ))
        
        # Generate optimization summary
        optimization_summary = _generate_optimization_summary(
            primary_route,
            alternatives,
            request.optimization_mode
        )
        
        # Calculate processing time
        processing_time = round((time.time() - start_time) * 1000)
        
        response = OptimizedRouteResponse(
            status="OK",
            request_id=request_id,
            primary_route=primary_route,
            alternatives=alternatives,
            optimization_summary=optimization_summary,
            processing_time_ms=processing_time
        )
        
        # Log success
        logger.info(
            f"Route optimization {request_id} completed: "
            f"{processing_time}ms, {len(alternatives)} alternatives"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Route optimization {request_id} failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Route optimization failed: {str(e)}"
        )


@router.post("/compare", response_model=RouteComparisonResponse)
async def compare_routes(
    request: RouteComparisonRequest,
    req: Request,
    gmaps_service: GoogleMapsService = Depends(get_gmaps_service)
):
    """
    Compare routes across multiple travel modes
    
    Analyzes the same route using different transportation methods:
    - Time efficiency comparison
    - Environmental impact analysis  
    - Cost-benefit analysis
    - Comfort and convenience factors
    - Recommendations based on preferences
    """
    start_time = time.time()
    request_id = getattr(req.state, 'request_id', str(uuid.uuid4())[:8])
    
    try:
        logger.info(
            f"Route comparison request {request_id}: "
            f"modes={request.travel_modes}"
        )
        
        # Calculate routes for each travel mode
        route_tasks = []
        for mode in request.travel_modes:
            route_request = RouteRequest(
                origin=request.origin,
                destination=request.destination,
                travel_mode=mode,
                alternatives=request.include_alternatives,
                departure_time=request.departure_time
            )
            
            task = _calculate_single_mode_route(route_request, gmaps_service)
            route_tasks.append((mode, task))
        
        # Execute all route calculations concurrently
        routes_by_mode = {}
        for mode, task in route_tasks:
            try:
                route = await task
                routes_by_mode[mode.value] = route
            except Exception as e:
                logger.warning(f"Failed to calculate route for {mode}: {str(e)}")
        
        # Generate comparison matrix
        comparison_matrix = _generate_comparison_matrix(routes_by_mode)
        
        # Generate recommendations
        recommendations = _generate_mode_recommendations(
            routes_by_mode,
            comparison_matrix
        )
        
        # Calculate processing time
        processing_time = round((time.time() - start_time) * 1000)
        
        response = RouteComparisonResponse(
            status="OK",
            request_id=request_id,
            routes_by_mode=routes_by_mode,
            comparison_matrix=comparison_matrix,
            recommendations=recommendations,
            processing_time_ms=processing_time
        )
        
        logger.info(
            f"Route comparison {request_id} completed: "
            f"{processing_time}ms, {len(routes_by_mode)} modes"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Route comparison {request_id} failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Route comparison failed: {str(e)}"
        )


@router.post("/three-strategies")
async def get_three_route_strategies(
    origin: LocationInput,
    destination: LocationInput,
    travel_mode: TravelMode = TravelMode.DRIVING,
    departure_time: Optional[str] = None,
    req: Request = None,
    gmaps_service: GoogleMapsService = Depends(get_gmaps_service)
):
    """
    Generate 3 strategically different routes for the same trip
    
    Returns three optimized routes:
    1. **FASTEST** - Speed-optimized with real-time traffic
    2. **ECO_FRIENDLY** - Environmental-optimized with lowest emissions  
    3. **BALANCED** - Optimal balance of time, cost, and environmental impact
    
    Each route uses different optimization algorithms and preferences:
    - Different traffic models (optimistic vs realistic)
    - Different road preferences (highways vs local roads)
    - Different optimization criteria (speed vs fuel efficiency vs balance)
    """
    start_time = time.time()
    request_id = getattr(req.state, 'request_id', str(uuid.uuid4())[:8]) if req else str(uuid.uuid4())[:8]
    
    try:
        logger.info(f"Three-strategy route request {request_id}: {origin} → {destination}")
        
        # Parse departure time
        parsed_departure_time = None
        if departure_time:
            try:
                parsed_departure_time = datetime.fromisoformat(departure_time.replace('Z', '+00:00'))
            except ValueError:
                parsed_departure_time = datetime.now()
        
        # Initialize strategy engine
        strategy_engine = RouteStrategyEngine(gmaps_service)
        
        # Generate 3 different route strategies
        routes = await strategy_engine.generate_three_route_strategies(
            origin=origin,
            destination=destination,
            travel_mode=travel_mode,
            departure_time=parsed_departure_time
        )
        
        if not routes:
            raise HTTPException(
                status_code=400,
                detail="Failed to calculate any routes. Please check your locations."
            )
        
        # Generate optimization analysis
        optimization_analysis = RouteOptimizer.analyze_route_patterns(routes)
        
        # Calculate processing time
        processing_time = round((time.time() - start_time) * 1000)
        
        response = {
            "status": "OK",
            "request_id": request_id,
            "routes": {
                "fastest": routes.get("fastest"),
                "eco_friendly": routes.get("eco_friendly"), 
                "balanced": routes.get("balanced")
            },
            "route_comparison": optimization_analysis.get("route_comparison", {}),
            "optimization_suggestions": optimization_analysis.get("optimization_suggestions", []),
            "trip_insights": {
                "total_routes_generated": len(routes),
                "travel_mode": travel_mode.value,
                "departure_time": departure_time,
                "analysis_timestamp": datetime.now().isoformat()
            },
            "processing_time_ms": processing_time
        }
        
        logger.info(
            f"Three-strategy routes {request_id} completed: "
            f"{processing_time}ms, {len(routes)} strategies generated"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Three-strategy routes {request_id} failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Route strategy calculation failed: {str(e)}"
        )


@router.get("/traffic/{route_id}")
async def get_traffic_update(
    route_id: str,
    gmaps_service: GoogleMapsService = Depends(get_gmaps_service)
):
    """
    Get real-time traffic updates for a specific route
    
    Provides current traffic conditions and updated travel times:
    - Real-time traffic delays
    - Alternative route suggestions if significant delays
    - Estimated time adjustments
    - Traffic incident information
    """
    try:
        # This would typically look up stored route data
        # For now, return mock traffic data
        return {
            "route_id": route_id,
            "traffic_status": "moderate",
            "current_delay_minutes": 5,
            "updated_duration": "32 minutes",
            "incidents": [
                {
                    "type": "construction",
                    "severity": "minor",
                    "location": "Highway 1, Exit 15",
                    "delay_minutes": 3
                }
            ],
            "alternative_available": True,
            "last_updated": time.time()
        }
        
    except Exception as e:
        logger.error(f"Traffic update failed for route {route_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get traffic update"
        )


# Helper functions

async def _process_route_data(
    route_data: Dict[str, Any],
    travel_mode: TravelMode,
    gmaps_service: GoogleMapsService
) -> Route:
    """Process raw route data into structured Route object"""
    
    # Calculate emissions
    emissions = gmaps_service.calculate_emissions(route_data, travel_mode)
    
    # Calculate totals
    total_distance = {"text": "0 km", "value": 0}
    total_duration = {"text": "0 mins", "value": 0}
    total_duration_in_traffic = {"text": "0 mins", "value": 0}
    
    legs = []
    for leg_data in route_data.get('legs', []):
        # Process steps
        steps = []
        for step_data in leg_data.get('steps', []):
            step = {
                "instruction": step_data.get('html_instructions', ''),
                "distance": step_data.get('distance', {}),
                "duration": step_data.get('duration', {}),
                "start_location": {
                    "lat": step_data['start_location']['lat'],
                    "lng": step_data['start_location']['lng']
                },
                "end_location": {
                    "lat": step_data['end_location']['lat'], 
                    "lng": step_data['end_location']['lng']
                },
                "polyline": step_data.get('polyline', {}).get('points', ''),
                "travel_mode": step_data.get('travel_mode', travel_mode.value)
            }
            steps.append(step)
        
        # Create leg
        leg = {
            "start_address": leg_data.get('start_address', ''),
            "end_address": leg_data.get('end_address', ''),
            "start_location": {
                "lat": leg_data['start_location']['lat'],
                "lng": leg_data['start_location']['lng']
            },
            "end_location": {
                "lat": leg_data['end_location']['lat'],
                "lng": leg_data['end_location']['lng']
            },
            "distance": leg_data.get('distance', {}),
            "duration": leg_data.get('duration', {}),
            "duration_in_traffic": leg_data.get('duration_in_traffic'),
            "steps": steps
        }
        legs.append(leg)
        
        # Accumulate totals
        total_distance["value"] += leg_data.get('distance', {}).get('value', 0)
        total_duration["value"] += leg_data.get('duration', {}).get('value', 0)
        
        if leg_data.get('duration_in_traffic'):
            total_duration_in_traffic["value"] += leg_data['duration_in_traffic']['value']
    
    # Format total texts
    total_distance["text"] = f"{total_distance['value'] / 1000:.1f} km"
    total_duration["text"] = f"{total_duration['value'] // 60} mins"
    
    if total_duration_in_traffic["value"] > 0:
        total_duration_in_traffic["text"] = f"{total_duration_in_traffic['value'] // 60} mins"
    else:
        total_duration_in_traffic = None
    
    return Route(
        summary=route_data.get('summary', ''),
        legs=legs,
        warnings=route_data.get('warnings', []),
        waypoint_order=route_data.get('waypoint_order'),
        overview_polyline=route_data.get('overview_polyline', {}).get('points', ''),
        bounds={
            "northeast": {
                "lat": route_data['bounds']['northeast']['lat'],
                "lng": route_data['bounds']['northeast']['lng']
            },
            "southwest": {
                "lat": route_data['bounds']['southwest']['lat'], 
                "lng": route_data['bounds']['southwest']['lng']
            }
        },
        copyrights=route_data.get('copyrights', ''),
        fare=route_data.get('fare'),
        emissions=emissions,
        total_distance=total_distance,
        total_duration=total_duration,
        total_duration_in_traffic=total_duration_in_traffic
    )


async def _calculate_single_mode_route(
    request: RouteRequest,
    gmaps_service: GoogleMapsService
) -> Route:
    """Calculate route for a single travel mode"""
    directions_result = await gmaps_service.calculate_directions(request)
    
    if not directions_result or directions_result[0]['status'] != 'OK':
        raise ValueError(f"Failed to calculate route for {request.travel_mode}")
    
    route_data = directions_result[0]['routes'][0]
    return await _process_route_data(route_data, request.travel_mode, gmaps_service)


def _calculate_route_comparison(primary: Route, alternative: Route) -> Dict[str, Any]:
    """Calculate comparison metrics between routes"""
    
    time_diff = alternative.total_duration["value"] - primary.total_duration["value"]
    distance_diff = alternative.total_distance["value"] - primary.total_distance["value"]
    
    emissions_diff = 0
    if primary.emissions and alternative.emissions:
        emissions_diff = alternative.emissions.co2_emissions_kg - primary.emissions.co2_emissions_kg
    
    return {
        "time_difference_minutes": round(time_diff / 60, 1),
        "distance_difference_km": round(distance_diff / 1000, 2),
        "emissions_difference_kg": round(emissions_diff, 2),
        "eco_score_difference": (
            alternative.emissions.eco_score - primary.emissions.eco_score
            if primary.emissions and alternative.emissions else 0
        )
    }


def _calculate_recommendation_score(
    route: Route,
    optimization_mode: OptimizationMode,
    comparison: Dict[str, Any]
) -> float:
    """Calculate recommendation score for alternative route"""
    
    base_score = 5.0
    
    if optimization_mode == OptimizationMode.FASTEST:
        # Prioritize time savings
        if comparison["time_difference_minutes"] < 0:
            base_score += min(3.0, abs(comparison["time_difference_minutes"]) * 0.2)
        else:
            base_score -= min(3.0, comparison["time_difference_minutes"] * 0.1)
    
    elif optimization_mode == OptimizationMode.SHORTEST:
        # Prioritize distance savings
        if comparison["distance_difference_km"] < 0:
            base_score += min(3.0, abs(comparison["distance_difference_km"]) * 0.3)
        else:
            base_score -= min(3.0, comparison["distance_difference_km"] * 0.2)
    
    elif optimization_mode == OptimizationMode.ECO_FRIENDLY:
        # Prioritize emissions savings
        if comparison["emissions_difference_kg"] < 0:
            base_score += min(4.0, abs(comparison["emissions_difference_kg"]) * 0.5)
        else:
            base_score -= min(4.0, comparison["emissions_difference_kg"] * 0.3)
    
    # Add eco score bonus
    if route.emissions:
        base_score += (route.emissions.eco_score - 5.0) * 0.3
    
    return max(0.0, min(10.0, base_score))


def _generate_optimization_summary(
    primary_route: Route,
    alternatives: List[RouteAlternative],
    optimization_mode: OptimizationMode
) -> Dict[str, Any]:
    """Generate optimization summary"""
    
    summary = {
        "optimization_mode": optimization_mode.value,
        "primary_route_stats": {
            "distance": primary_route.total_distance["text"],
            "duration": primary_route.total_duration["text"],
            "eco_score": primary_route.emissions.eco_score if primary_route.emissions else None
        },
        "alternatives_count": len(alternatives)
    }
    
    if alternatives:
        best_alternative = max(alternatives, key=lambda x: x.recommendation_score)
        summary["best_alternative"] = {
            "recommendation_score": best_alternative.recommendation_score,
            "time_difference": best_alternative.comparison_to_primary["time_difference_minutes"],
            "distance_difference": best_alternative.comparison_to_primary["distance_difference_km"]
        }
    
    return summary


def _generate_comparison_matrix(routes_by_mode: Dict[str, Route]) -> Dict[str, Dict[str, float]]:
    """Generate comparison matrix across travel modes"""
    
    if not routes_by_mode:
        return {}
    
    # Normalize metrics (0-1 scale)
    modes = list(routes_by_mode.keys())
    
    # Get min/max values for normalization
    durations = [route.total_duration["value"] for route in routes_by_mode.values()]
    distances = [route.total_distance["value"] for route in routes_by_mode.values()]
    emissions = [
        route.emissions.co2_emissions_kg if route.emissions else 0
        for route in routes_by_mode.values()
    ]
    
    min_duration, max_duration = min(durations), max(durations)
    min_distance, max_distance = min(distances), max(distances)
    min_emissions, max_emissions = min(emissions), max(emissions)
    
    matrix = {}
    
    for mode, route in routes_by_mode.items():
        # Time efficiency (lower duration = higher efficiency)
        time_eff = 1.0
        if max_duration > min_duration:
            time_eff = 1.0 - (route.total_duration["value"] - min_duration) / (max_duration - min_duration)
        
        # Distance efficiency (shorter distance = higher efficiency)
        dist_eff = 1.0
        if max_distance > min_distance:
            dist_eff = 1.0 - (route.total_distance["value"] - min_distance) / (max_distance - min_distance)
        
        # Environmental efficiency (lower emissions = higher efficiency)
        env_eff = 1.0
        if route.emissions and max_emissions > min_emissions:
            env_eff = 1.0 - (route.emissions.co2_emissions_kg - min_emissions) / (max_emissions - min_emissions)
        
        matrix[mode] = {
            "time_efficiency": round(time_eff, 3),
            "distance_efficiency": round(dist_eff, 3),
            "environmental_efficiency": round(env_eff, 3),
            "overall_score": round((time_eff + dist_eff + env_eff * 1.5) / 3.5, 3)
        }
    
    return matrix


def _generate_mode_recommendations(
    routes_by_mode: Dict[str, Route],
    comparison_matrix: Dict[str, Dict[str, float]]
) -> List[Dict[str, Any]]:
    """Generate travel mode recommendations"""
    
    recommendations = []
    
    # Find best modes for different criteria
    if comparison_matrix:
        # Best overall
        best_overall = max(comparison_matrix.items(), key=lambda x: x[1]["overall_score"])
        recommendations.append({
            "mode": best_overall[0],
            "reason": "Best overall balance of time, distance, and environmental impact",
            "score": round(best_overall[1]["overall_score"] * 10, 1)
        })
        
        # Most eco-friendly
        best_eco = max(comparison_matrix.items(), key=lambda x: x[1]["environmental_efficiency"])
        if best_eco[0] != best_overall[0]:
            recommendations.append({
                "mode": best_eco[0],
                "reason": "Most environmentally friendly option",
                "score": round(best_eco[1]["environmental_efficiency"] * 10, 1)
            })
        
        # Fastest
        best_time = max(comparison_matrix.items(), key=lambda x: x[1]["time_efficiency"])
        if best_time[0] not in [best_overall[0], best_eco[0]]:
            recommendations.append({
                "mode": best_time[0],
                "reason": "Fastest travel option",
                "score": round(best_time[1]["time_efficiency"] * 10, 1)
            })
    
    return recommendations