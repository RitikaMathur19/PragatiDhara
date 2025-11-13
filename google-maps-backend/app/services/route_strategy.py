"""
Enhanced Route Strategy Engine for Google Maps Backend
Generates 3 distinct route types with optimization algorithms
"""

from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import logging
from datetime import datetime, timedelta
import asyncio

from ..models.route_models import (
    RouteRequest, Route, TravelMode, OptimizationMode, 
    TrafficModel, LocationInput
)
from ..services.google_maps import GoogleMapsService
from ..services.green_credits_service import GreenCreditsService

logger = logging.getLogger(__name__)


class RouteStrategy(str, Enum):
    """Three distinct route strategies"""
    FASTEST = "fastest"           # Speed-optimized route
    ECO_FRIENDLY = "eco_friendly" # Environmental-optimized route  
    BALANCED = "balanced"         # Balance of time, cost, and environment


class RouteStrategyEngine:
    """
    Advanced route strategy engine that generates 3 distinct route types:
    1. FASTEST - Speed-optimized with real-time traffic
    2. ECO_FRIENDLY - Environmental-optimized with lowest emissions
    3. BALANCED - Optimal balance of time, cost, and environmental impact
    """
    
    def __init__(self, gmaps_service: GoogleMapsService):
        self.gmaps_service = gmaps_service
        self.green_credits_service = GreenCreditsService()
        
    async def generate_three_route_strategies(
        self, 
        origin: LocationInput, 
        destination: LocationInput,
        travel_mode: TravelMode = TravelMode.DRIVING,
        departure_time: Optional[datetime] = None
    ) -> Dict[str, Route]:
        """
        Generate 3 strategically different routes for the same origin/destination
        
        Returns:
            Dict with keys: 'fastest', 'eco_friendly', 'balanced'
        """
        
        # Execute all 3 strategies concurrently
        tasks = [
            self._calculate_fastest_route(origin, destination, travel_mode, departure_time),
            self._calculate_eco_friendly_route(origin, destination, travel_mode, departure_time),
            self._calculate_balanced_route(origin, destination, travel_mode, departure_time)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        routes = {}
        strategy_names = ["fastest", "eco_friendly", "balanced"]
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to calculate {strategy_names[i]} route: {result}")
                continue
            routes[strategy_names[i]] = result
            
        return routes
    
    async def _calculate_fastest_route(
        self, 
        origin: LocationInput, 
        destination: LocationInput,
        travel_mode: TravelMode,
        departure_time: Optional[datetime]
    ) -> Route:
        """
        Strategy 1: FASTEST ROUTE
        - Prioritizes speed and minimal travel time
        - Uses real-time traffic data
        - May include highways and toll roads for speed
        - Optimistic traffic model for best-case scenarios
        """
        
        request = RouteRequest(
            origin=origin,
            destination=destination,
            travel_mode=travel_mode,
            optimization_mode=OptimizationMode.FASTEST,
            alternatives=False,
            avoid_highways=False,  # Allow highways for speed
            avoid_tolls=False,     # Allow tolls for speed
            avoid_ferries=True,    # Avoid ferries (usually slower)
            departure_time=departure_time or datetime.now(),
            traffic_model=TrafficModel.OPTIMISTIC,  # Best-case traffic
            region="IN",
            language="en"
        )
        
        directions = await self.gmaps_service.calculate_directions(request)
        
        if not directions or directions[0]['status'] != 'OK':
            raise ValueError("Failed to calculate fastest route")
            
        route_data = directions[0]['routes'][0]
        route = await self._process_route_with_strategy_metadata(
            route_data, 
            travel_mode, 
            RouteStrategy.FASTEST,
            {
                "strategy_focus": "Minimum travel time",
                "traffic_optimization": "Real-time traffic with optimistic model",
                "road_preferences": "Highways and toll roads allowed for speed",
                "optimization_factors": ["travel_time", "traffic_conditions", "road_efficiency"]
            }
        )
        
        return route
    
    async def _calculate_eco_friendly_route(
        self, 
        origin: LocationInput, 
        destination: LocationInput,
        travel_mode: TravelMode,
        departure_time: Optional[datetime]
    ) -> Route:
        """
        Strategy 2: ECO-FRIENDLY ROUTE
        - Minimizes environmental impact and fuel consumption
        - Avoids highways when possible (lower speeds = better fuel efficiency)
        - Prefers routes with less traffic congestion
        - Optimizes for steady speeds and fewer stops
        """
        
        request = RouteRequest(
            origin=origin,
            destination=destination,
            travel_mode=travel_mode,
            optimization_mode=OptimizationMode.ECO_FRIENDLY,
            alternatives=True,  # Get alternatives to find most eco-friendly
            avoid_highways=True,    # Highways = higher speeds = more fuel consumption
            avoid_tolls=False,      # Tolls may have less traffic = more efficient
            avoid_ferries=True,
            departure_time=departure_time or datetime.now(),
            traffic_model=TrafficModel.BEST_GUESS,  # Realistic traffic for efficiency
            region="IN",
            language="en"
        )
        
        directions = await self.gmaps_service.calculate_directions(request)
        
        if not directions or directions[0]['status'] != 'OK':
            raise ValueError("Failed to calculate eco-friendly route")
        
        # Select the most eco-friendly route from alternatives
        best_route_data = self._select_most_eco_friendly_route(directions[0]['routes'])
        
        route = await self._process_route_with_strategy_metadata(
            best_route_data,
            travel_mode,
            RouteStrategy.ECO_FRIENDLY,
            {
                "strategy_focus": "Minimum environmental impact and fuel consumption",
                "traffic_optimization": "Avoid congested areas for steady speeds",
                "road_preferences": "Local roads preferred over highways",
                "optimization_factors": ["fuel_efficiency", "co2_emissions", "steady_speeds", "fewer_stops"]
            }
        )
        
        return route
    
    async def _calculate_balanced_route(
        self, 
        origin: LocationInput, 
        destination: LocationInput,
        travel_mode: TravelMode,
        departure_time: Optional[datetime]
    ) -> Route:
        """
        Strategy 3: BALANCED ROUTE
        - Optimizes for best overall experience
        - Balances time, cost, comfort, and environmental impact
        - Uses moderate traffic assumptions
        - Considers road quality and driver experience
        """
        
        request = RouteRequest(
            origin=origin,
            destination=destination,
            travel_mode=travel_mode,
            optimization_mode=OptimizationMode.BALANCED,
            alternatives=True,
            avoid_highways=False,   # Use highways strategically
            avoid_tolls=True,       # Avoid tolls for cost savings
            avoid_ferries=True,
            departure_time=departure_time or datetime.now(),
            traffic_model=TrafficModel.BEST_GUESS,  # Realistic traffic model
            region="IN",
            language="en"
        )
        
        directions = await self.gmaps_service.calculate_directions(request)
        
        if not directions or directions[0]['status'] != 'OK':
            raise ValueError("Failed to calculate balanced route")
        
        # Select the most balanced route from alternatives
        best_route_data = self._select_most_balanced_route(directions[0]['routes'])
        
        route = await self._process_route_with_strategy_metadata(
            best_route_data,
            travel_mode,
            RouteStrategy.BALANCED,
            {
                "strategy_focus": "Optimal balance of time, cost, and environmental impact",
                "traffic_optimization": "Realistic traffic with moderate assumptions",
                "road_preferences": "Strategic use of highways, avoid tolls",
                "optimization_factors": ["travel_time", "fuel_cost", "comfort", "environmental_impact"]
            }
        )
        
        return route
    
    def _select_most_eco_friendly_route(self, routes: List[Dict]) -> Dict:
        """Select the route with lowest environmental impact"""
        if len(routes) == 1:
            return routes[0]
        
        best_route = routes[0]
        best_score = float('inf')
        
        for route in routes:
            # Calculate eco-friendliness score based on:
            # - Total distance (shorter = better)
            # - Highway usage (less = better for fuel efficiency)
            # - Traffic conditions (smoother = better)
            
            total_distance = sum(leg['distance']['value'] for leg in route['legs'])
            
            # Estimate highway usage from route summary
            highway_penalty = 1.2 if 'highway' in route.get('summary', '').lower() else 1.0
            
            # Environmental score (lower is better)
            eco_score = total_distance * highway_penalty
            
            if eco_score < best_score:
                best_score = eco_score
                best_route = route
        
        return best_route
    
    def _select_most_balanced_route(self, routes: List[Dict]) -> Dict:
        """Select the route with best overall balance"""
        if len(routes) == 1:
            return routes[0]
        
        best_route = routes[0]
        best_score = 0
        
        for route in routes:
            # Calculate balanced score considering:
            # - Time efficiency (40% weight)
            # - Distance efficiency (30% weight)  
            # - Cost efficiency (20% weight)
            # - Comfort (10% weight)
            
            total_duration = sum(leg['duration']['value'] for leg in route['legs'])
            total_distance = sum(leg['distance']['value'] for leg in route['legs'])
            
            # Normalize scores (lower duration/distance = higher score)
            time_score = max(0, 100 - (total_duration / 60))  # Convert to minutes
            distance_score = max(0, 100 - (total_distance / 1000))  # Convert to km
            
            # Cost score (avoid tolls = higher score)
            cost_score = 80 if 'toll' not in route.get('summary', '').lower() else 60
            
            # Comfort score (fewer turns and highway usage)
            total_steps = sum(len(leg['steps']) for leg in route['legs'])
            comfort_score = max(0, 100 - total_steps * 2)
            
            # Weighted balanced score
            balanced_score = (
                time_score * 0.4 +
                distance_score * 0.3 + 
                cost_score * 0.2 +
                comfort_score * 0.1
            )
            
            if balanced_score > best_score:
                best_score = balanced_score
                best_route = route
        
        return best_route
    
    async def _process_route_with_strategy_metadata(
        self,
        route_data: Dict[str, Any],
        travel_mode: TravelMode,
        strategy: RouteStrategy,
        strategy_metadata: Dict[str, Any]
    ) -> Route:
        """Process route data with strategy-specific metadata"""
        
        # Calculate emissions with strategy-specific factors
        emissions = self.gmaps_service.calculate_emissions(route_data, travel_mode)
        
        # Apply strategy-specific emissions adjustments
        if strategy == RouteStrategy.ECO_FRIENDLY:
            # Bonus points for eco-friendly routes
            emissions.eco_score = min(10.0, emissions.eco_score + 1.5)
        elif strategy == RouteStrategy.FASTEST:
            # Penalty for speed-focused routes (usually less eco-friendly)
            emissions.eco_score = max(0.0, emissions.eco_score - 0.5)
        
        # Process route similar to existing logic but add strategy metadata
        route = await self._convert_to_route_object(route_data, travel_mode, emissions)
        
        # Add strategy-specific metadata
        if not hasattr(route, 'strategy_info'):
            route.strategy_info = {}
        
        route.strategy_info = {
            "strategy_type": strategy.value,
            "strategy_metadata": strategy_metadata,
            "optimization_timestamp": datetime.now().isoformat()
        }
        
        # Calculate green credits based on strategy type
        optimization_mode_map = {
            RouteStrategy.FASTEST: "fastest",
            RouteStrategy.ECO_FRIENDLY: "eco_friendly",
            RouteStrategy.BALANCED: "balanced"
        }
        
        optimization_mode = optimization_mode_map.get(strategy, "balanced")
        route.green_credits_earned = self.green_credits_service.calculate_credits_for_route(
            route=route,
            optimization_mode=optimization_mode
        )
        
        return route
    
    async def _convert_to_route_object(
        self, 
        route_data: Dict[str, Any], 
        travel_mode: TravelMode, 
        emissions
    ) -> Route:
        """Convert Google Maps route data to Route object"""
        
        # Calculate totals
        total_distance = {"text": "0 km", "value": 0}
        total_duration = {"text": "0 mins", "value": 0}
        
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
        
        # Format total texts
        total_distance["text"] = f"{total_distance['value'] / 1000:.1f} km"
        total_duration["text"] = f"{total_duration['value'] // 60} mins"
        
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
            total_duration_in_traffic=route_data.get('legs', [{}])[0].get('duration_in_traffic')
        )


class RouteOptimizer:
    """Advanced optimization suggestions for future trips"""
    
    @staticmethod
    def analyze_route_patterns(routes: Dict[str, Route]) -> Dict[str, Any]:
        """
        Analyze route patterns and provide optimization suggestions
        """
        
        if not routes:
            return {"suggestions": [], "analysis": "No routes available for analysis"}
        
        analysis = {
            "route_comparison": {},
            "optimization_suggestions": [],
            "best_route_by_criteria": {},
            "traffic_insights": {},
            "cost_analysis": {},
            "environmental_impact": {}
        }
        
        # Compare routes
        for strategy, route in routes.items():
            analysis["route_comparison"][strategy] = {
                "distance_km": round(route.total_distance["value"] / 1000, 1),
                "duration_minutes": round(route.total_duration["value"] / 60, 1),
                "eco_score": route.emissions.eco_score if route.emissions else 0,
                "co2_emissions_kg": route.emissions.co2_emissions_kg if route.emissions else 0
            }
        
        # Generate optimization suggestions
        suggestions = []
        
        # Time-based suggestions
        fastest_route = min(routes.items(), key=lambda x: x[1].total_duration["value"])
        suggestions.append({
            "type": "time_optimization",
            "message": f"For fastest travel, use {fastest_route[0]} route - saves up to {_calculate_time_savings(routes, fastest_route[1])} minutes",
            "impact": "high",
            "savings_minutes": _calculate_time_savings(routes, fastest_route[1])
        })
        
        # Environmental suggestions
        eco_route = max(routes.items(), key=lambda x: x[1].emissions.eco_score if x[1].emissions else 0)
        suggestions.append({
            "type": "environmental_optimization", 
            "message": f"For lowest environmental impact, use {eco_route[0]} route - reduces CO2 by up to {_calculate_co2_savings(routes, eco_route[1]):.1f} kg",
            "impact": "medium",
            "co2_savings_kg": _calculate_co2_savings(routes, eco_route[1])
        })
        
        # Traffic-based suggestions
        suggestions.append({
            "type": "traffic_optimization",
            "message": "For consistent travel times, avoid peak hours (8-10 AM, 5-7 PM) or use public transit during these times",
            "impact": "high",
            "recommended_times": ["6:00-8:00 AM", "10:00 AM-4:00 PM", "7:00-10:00 PM"]
        })
        
        analysis["optimization_suggestions"] = suggestions
        
        return analysis


def _calculate_time_savings(routes: Dict[str, Route], fastest_route: Route) -> int:
    """Calculate time savings compared to slowest route"""
    if not routes:
        return 0
    
    slowest_time = max(route.total_duration["value"] for route in routes.values())
    fastest_time = fastest_route.total_duration["value"]
    
    return round((slowest_time - fastest_time) / 60)


def _calculate_co2_savings(routes: Dict[str, Route], eco_route: Route) -> float:
    """Calculate CO2 savings compared to highest emission route"""
    if not routes:
        return 0.0
    
    emissions = [route.emissions.co2_emissions_kg for route in routes.values() if route.emissions]
    if not emissions:
        return 0.0
    
    highest_emissions = max(emissions)
    eco_emissions = eco_route.emissions.co2_emissions_kg if eco_route.emissions else 0
    
    return max(0.0, highest_emissions - eco_emissions)