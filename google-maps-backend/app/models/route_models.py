"""
Pydantic models for route optimization and navigation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union, Literal
from datetime import datetime
from enum import Enum


class TravelMode(str, Enum):
    """Supported travel modes"""
    DRIVING = "driving"
    WALKING = "walking"
    BICYCLING = "bicycling" 
    TRANSIT = "transit"


class OptimizationMode(str, Enum):
    """Route optimization preferences"""
    FASTEST = "fastest"
    SHORTEST = "shortest" 
    ECO_FRIENDLY = "eco_friendly"
    BALANCED = "balanced"


class TrafficModel(str, Enum):
    """Traffic model options"""
    BEST_GUESS = "best_guess"
    PESSIMISTIC = "pessimistic"
    OPTIMISTIC = "optimistic"


class Units(str, Enum):
    """Distance/time units"""
    METRIC = "metric"
    IMPERIAL = "imperial"


class Location(BaseModel):
    """Geographic location representation"""
    lat: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    lng: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lat": 28.6139,
                "lng": 77.2090
            }
        }


class LocationInput(BaseModel):
    """Flexible location input (address or coordinates)"""
    address: Optional[str] = Field(None, description="Address string")
    coordinates: Optional[Location] = Field(None, description="Lat/lng coordinates")
    place_id: Optional[str] = Field(None, description="Google Places ID")
    
    @validator('coordinates', 'address', 'place_id')
    def validate_location_input(cls, v, values):
        """Ensure at least one location method is provided"""
        if not any([values.get('address'), v, values.get('place_id')]):
            raise ValueError('At least one of address, coordinates, or place_id must be provided')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "address": "India Gate, New Delhi"
            }
        }


class Waypoint(BaseModel):
    """Route waypoint with optional optimization"""
    location: LocationInput
    stopover: bool = Field(True, description="Whether this is a stopover or just a route point")
    
    class Config:
        json_schema_extra = {
            "example": {
                "location": {"address": "Connaught Place, New Delhi"},
                "stopover": True
            }
        }


class RouteRequest(BaseModel):
    """Route calculation request"""
    origin: LocationInput = Field(..., description="Starting location")
    destination: LocationInput = Field(..., description="Ending location") 
    waypoints: Optional[List[Waypoint]] = Field([], description="Intermediate waypoints")
    travel_mode: TravelMode = Field(TravelMode.DRIVING, description="Transportation mode")
    optimization_mode: OptimizationMode = Field(OptimizationMode.BALANCED, description="Route optimization preference")
    alternatives: bool = Field(False, description="Return alternative routes")
    avoid_highways: bool = Field(False, description="Avoid highways")
    avoid_tolls: bool = Field(False, description="Avoid toll roads")
    avoid_ferries: bool = Field(False, description="Avoid ferries")
    departure_time: Optional[datetime] = Field(None, description="Departure time for traffic-aware routing")
    arrival_time: Optional[datetime] = Field(None, description="Desired arrival time")
    traffic_model: TrafficModel = Field(TrafficModel.BEST_GUESS, description="Traffic prediction model")
    region: Optional[str] = Field("IN", description="Region bias for geocoding")
    language: Optional[str] = Field("en", description="Language for directions")
    units: Units = Field(Units.METRIC, description="Distance and time units")
    
    @validator('waypoints')
    def validate_waypoints_count(cls, v):
        """Validate waypoints count limit"""
        if v and len(v) > 25:
            raise ValueError('Maximum 25 waypoints allowed')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "origin": {"address": "Katraj, Pune"},
                "destination": {"address": "Hinjewadi, Pune"},
                "waypoints": [
                    {"location": {"address": "Shivajinagar, Pune"}}
                ],
                "travel_mode": "driving",
                "optimization_mode": "eco_friendly",
                "alternatives": True,
                "avoid_tolls": False
            }
        }


class RouteComparisonRequest(BaseModel):
    """Compare routes across multiple travel modes"""
    origin: LocationInput
    destination: LocationInput
    travel_modes: List[TravelMode] = Field(..., min_items=1, max_items=4)
    include_alternatives: bool = Field(False)
    departure_time: Optional[datetime] = Field(None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "origin": {"coordinates": {"lat": 28.6139, "lng": 77.2090}},
                "destination": {"coordinates": {"lat": 28.5355, "lng": 77.3910}},
                "travel_modes": ["driving", "transit", "walking"]
            }
        }


class RouteStep(BaseModel):
    """Individual route step/instruction"""
    instruction: str = Field(..., description="Turn-by-turn instruction")
    distance: Dict[str, Union[str, float]] = Field(..., description="Step distance")
    duration: Dict[str, Union[str, int]] = Field(..., description="Step duration")
    start_location: Location = Field(..., description="Step start coordinates")
    end_location: Location = Field(..., description="Step end coordinates")
    polyline: Optional[str] = Field(None, description="Encoded polyline for step")
    travel_mode: str = Field(..., description="Travel mode for this step")
    
    class Config:
        json_schema_extra = {
            "example": {
                "instruction": "Head north on Example Road",
                "distance": {"text": "1.2 km", "value": 1200},
                "duration": {"text": "3 mins", "value": 180},
                "start_location": {"lat": 28.6139, "lng": 77.2090},
                "end_location": {"lat": 28.6150, "lng": 77.2095}
            }
        }


class RouteLeg(BaseModel):
    """Route leg between two waypoints"""
    start_address: str = Field(..., description="Human-readable start address")
    end_address: str = Field(..., description="Human-readable end address")
    start_location: Location = Field(..., description="Start coordinates")
    end_location: Location = Field(..., description="End coordinates")
    distance: Dict[str, Union[str, float]] = Field(..., description="Leg distance")
    duration: Dict[str, Union[str, int]] = Field(..., description="Leg duration")
    duration_in_traffic: Optional[Dict[str, Union[str, int]]] = Field(None, description="Duration with traffic")
    steps: List[RouteStep] = Field(..., description="Turn-by-turn steps")
    
    class Config:
        json_schema_extra = {
            "example": {
                "start_address": "Katraj, Pune, Maharashtra, India",
                "end_address": "Hinjewadi, Pune, Maharashtra, India",
                "distance": {"text": "25.3 km", "value": 25300},
                "duration": {"text": "45 mins", "value": 2700}
            }
        }


class EmissionsData(BaseModel):
    """Environmental impact data"""
    co2_emissions_kg: float = Field(..., description="CO2 emissions in kilograms")
    fuel_consumption_liters: Optional[float] = Field(None, description="Fuel consumption in liters")
    energy_consumption_kwh: Optional[float] = Field(None, description="Energy consumption for EVs")
    eco_score: float = Field(..., ge=0, le=10, description="Environmental score (0-10)")
    comparison_savings: Optional[Dict[str, float]] = Field(None, description="Savings vs other modes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "co2_emissions_kg": 5.2,
                "fuel_consumption_liters": 2.3,
                "eco_score": 6.5,
                "comparison_savings": {
                    "vs_fastest_route": 0.8,
                    "vs_public_transport": -2.1
                }
            }
        }


class Route(BaseModel):
    """Complete route information"""
    summary: str = Field(..., description="Route summary")
    legs: List[RouteLeg] = Field(..., description="Route legs")
    warnings: List[str] = Field([], description="Route warnings")
    waypoint_order: Optional[List[int]] = Field(None, description="Optimized waypoint order")
    overview_polyline: str = Field(..., description="Encoded overview polyline")
    bounds: Dict[str, Location] = Field(..., description="Route bounding box")
    copyrights: str = Field(..., description="Route data copyrights")
    fare: Optional[Dict[str, Any]] = Field(None, description="Fare information for transit")
    emissions: Optional[EmissionsData] = Field(None, description="Environmental impact data")
    
    # Calculated fields
    total_distance: Dict[str, Union[str, float]] = Field(..., description="Total route distance")
    total_duration: Dict[str, Union[str, int]] = Field(..., description="Total route duration")
    total_duration_in_traffic: Optional[Dict[str, Union[str, int]]] = Field(None, description="Total duration with traffic")
    green_credits_earned: float = Field(default=0.0, ge=0, description="Green credits user will earn for this route")
    
    class Config:
        json_schema_extra = {
            "example": {
                "summary": "Katraj to Hinjewadi via Shivajinagar",
                "total_distance": {"text": "25.3 km", "value": 25300},
                "total_duration": {"text": "45 mins", "value": 2700},
                "overview_polyline": "encoded_polyline_string_here"
            }
        }


class RouteAlternative(BaseModel):
    """Route alternative with comparison metrics"""
    route: Route = Field(..., description="Alternative route details")
    comparison_to_primary: Dict[str, Union[str, float]] = Field(..., description="Comparison metrics")
    recommendation_score: float = Field(..., ge=0, le=10, description="Recommendation score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "route": {},  # Route object
                "comparison_to_primary": {
                    "time_difference_minutes": 5,
                    "distance_difference_km": -2.1,
                    "eco_score_difference": 0.8
                },
                "recommendation_score": 7.5
            }
        }


class OptimizedRouteResponse(BaseModel):
    """Response for optimized route calculation"""
    status: str = Field(..., description="Response status")
    request_id: str = Field(..., description="Unique request identifier")
    primary_route: Route = Field(..., description="Primary optimized route")
    alternatives: List[RouteAlternative] = Field([], description="Alternative routes")
    optimization_summary: Dict[str, Any] = Field(..., description="Optimization details")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    geocoding_results: Optional[Dict[str, Any]] = Field(None, description="Geocoding results for inputs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "OK",
                "request_id": "req_12345",
                "primary_route": {},  # Route object
                "alternatives": [],
                "optimization_summary": {
                    "optimization_mode": "eco_friendly",
                    "savings_vs_fastest": {"time": "2 mins", "emissions": "0.5 kg CO2"}
                },
                "processing_time_ms": 250
            }
        }


class RouteComparisonResponse(BaseModel):
    """Response comparing routes across travel modes"""
    status: str = Field(..., description="Response status")
    request_id: str = Field(..., description="Unique request identifier")
    routes_by_mode: Dict[str, Route] = Field(..., description="Routes by travel mode")
    comparison_matrix: Dict[str, Dict[str, Union[str, float]]] = Field(..., description="Cross-mode comparison")
    recommendations: List[Dict[str, Any]] = Field(..., description="Mode recommendations")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "OK",
                "request_id": "req_12346",
                "routes_by_mode": {
                    "driving": {},  # Route object
                    "transit": {},  # Route object
                    "walking": {}   # Route object
                },
                "comparison_matrix": {
                    "time_efficiency": {"driving": 1.0, "transit": 0.8, "walking": 0.2},
                    "eco_friendliness": {"driving": 0.3, "transit": 0.9, "walking": 1.0}
                },
                "recommendations": [
                    {"mode": "transit", "reason": "Best environmental choice", "score": 8.5}
                ]
            }
        }