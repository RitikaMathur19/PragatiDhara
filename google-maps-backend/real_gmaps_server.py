"""
Real Google Maps Backend with Routes API Integration
This replaces the mock simple_server.py with actual Google Maps API calls
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
import time
import uuid
import asyncio
import aiohttp
import logging
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="PragatiDhara Google Maps Backend",
    description="Real Google Maps Routes API integration for sustainable route optimization",
    version="2.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Configuration
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', 'YOUR_API_KEY_HERE')
MAPS_BASE_URL = "https://maps.googleapis.com/maps/api"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request models
class RouteRequest(BaseModel):
    origin: Dict[str, Any]
    destination: Dict[str, Any]
    travel_mode: Optional[str] = "driving"
    departure_time: Optional[str] = None

class ThreeStrategiesRequest(BaseModel):
    origin: Dict[str, Any]
    destination: Dict[str, Any]
    travel_mode: Optional[str] = "driving"
    departure_time: Optional[str] = None

# Helper functions
async def call_google_maps_api(session: aiohttp.ClientSession, endpoint: str, params: Dict[str, Any]):
    """Make async call to Google Maps API"""
    params['key'] = GOOGLE_MAPS_API_KEY
    
    try:
        async with session.get(f"{MAPS_BASE_URL}/{endpoint}", params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                logger.error(f"Google Maps API error: {response.status} - {error_text}")
                raise HTTPException(status_code=response.status, detail=f"Google Maps API error: {error_text}")
    except aiohttp.ClientError as e:
        logger.error(f"Network error calling Google Maps API: {e}")
        raise HTTPException(status_code=503, detail=f"Network error: {str(e)}")

def parse_location(location_data: Dict[str, Any]) -> str:
    """Parse location data to address string"""
    if 'address' in location_data:
        return location_data['address']
    elif 'lat' in location_data and 'lng' in location_data:
        return f"{location_data['lat']},{location_data['lng']}"
    else:
        # Default locations based on node letters (Pune area)
        default_locations = {
            'A': 'Katraj, Pune, Maharashtra, India',
            'B': 'Swargate, Pune, Maharashtra, India', 
            'C': 'Deccan Gymkhana, Pune, Maharashtra, India',
            'D': 'Shivajinagar, Pune, Maharashtra, India',
            'E': 'University Circle, Pune, Maharashtra, India',
            'F': 'Kothrud Bypass, Pune, Maharashtra, India',
            'G': 'Balewadi Stadium, Pune, Maharashtra, India',
            'H': 'Baner, Pune, Maharashtra, India',
            'I': 'Wakad, Pune, Maharashtra, India',
            'J': 'Hinjawadi Phase 1, Pune, Maharashtra, India'
        }
        
        node = location_data.get('node', 'A')
        return default_locations.get(node, 'Pune, Maharashtra, India')

def calculate_emissions(distance_meters: int, route_type: str) -> Dict[str, float]:
    """Calculate CO2 emissions based on route type and distance"""
    distance_km = distance_meters / 1000.0
    
    # Emissions factors (kg CO2 per km)
    base_emission_factor = 0.18  # Average car emissions
    
    # Route-specific multipliers
    emission_multipliers = {
        'fastest': 1.2,      # Higher emissions due to highway/high-speed driving
        'eco-friendly': 0.7,  # Lower emissions due to eco-driving
        'balanced': 1.0       # Standard emissions
    }
    
    multiplier = emission_multipliers.get(route_type, 1.0)
    co2_emissions_kg = distance_km * base_emission_factor * multiplier
    
    # Fuel consumption (assuming 15 km/L efficiency)
    fuel_consumption_liters = distance_km / 15.0 * multiplier
    
    # Eco score (1-10 scale, higher is better)
    eco_score = max(1.0, 10.0 - (co2_emissions_kg / distance_km * 50))
    
    return {
        'co2_emissions_kg': round(co2_emissions_kg, 2),
        'eco_score': round(eco_score, 1),
        'fuel_consumption_liters': round(fuel_consumption_liters, 2)
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    api_key_status = "configured" if GOOGLE_MAPS_API_KEY != 'YOUR_API_KEY_HERE' else "not_configured"
    
    return {
        "status": "healthy",
        "service": "pragati_dhara_google_maps_backend", 
        "version": "2.0.0",
        "api_key_status": api_key_status,
        "timestamp": time.time()
    }

# Three-route strategies endpoint with real Google Maps integration
@app.post("/api/v1/routes/three-strategies")
async def get_three_route_strategies(request: ThreeStrategiesRequest):
    """Get three different route strategies using real Google Maps Directions API"""
    
    if GOOGLE_MAPS_API_KEY == 'YOUR_API_KEY_HERE':
        # Fallback to mock data if API key not configured
        logger.warning("Google Maps API key not configured, using mock data")
        return await get_mock_three_strategies(request)
    
    processing_start = time.time()
    request_id = str(uuid.uuid4())[:8]
    
    # Parse origin and destination
    origin = parse_location(request.origin)
    destination = parse_location(request.destination)
    
    logger.info(f"Calculating routes from {origin} to {destination}")
    
    async with aiohttp.ClientSession() as session:
        routes = {}
        
        # Define three route strategies
        strategies = {
            'fastest': {
                'avoid': [],
                'mode': 'driving',
                'optimize_for': 'time'
            },
            'eco_friendly': {
                'avoid': ['highways', 'tolls'],
                'mode': 'driving', 
                'optimize_for': 'fuel_efficiency'
            },
            'balanced': {
                'avoid': ['tolls'],
                'mode': 'driving',
                'optimize_for': 'balance'
            }
        }
        
        for strategy_name, strategy_config in strategies.items():
            params = {
                'origin': origin,
                'destination': destination,
                'mode': strategy_config['mode'],
                'departure_time': 'now',
                'traffic_model': 'best_guess',
                'alternatives': 'true'
            }
            
            # Add avoid parameters
            if strategy_config['avoid']:
                params['avoid'] = '|'.join(strategy_config['avoid'])
            
            try:
                directions_data = await call_google_maps_api(session, 'directions/json', params)
                
                if directions_data['status'] == 'OK' and directions_data['routes']:
                    route = directions_data['routes'][0]  # Get best route
                    leg = route['legs'][0]  # Get first leg
                    
                    # Calculate emissions
                    distance_meters = leg['distance']['value']
                    emissions = calculate_emissions(distance_meters, strategy_name)
                    
                    routes[strategy_name] = {
                        "total_distance": leg['distance'],
                        "total_duration": leg['duration'],
                        "summary": route.get('summary', f"Route via {strategy_name} strategy"),
                        "emissions": emissions,
                        "strategy_info": {
                            "strategy_metadata": {
                                "strategy_focus": strategy_config.get('optimize_for', 'general'),
                                "optimization_factors": strategy_config.get('avoid', []),
                                "polyline": route.get('overview_polyline', {}).get('points', ''),
                                "bounds": route.get('bounds', {}),
                                "warnings": route.get('warnings', [])
                            }
                        },
                        "raw_google_data": {
                            "distance_meters": distance_meters,
                            "duration_seconds": leg['duration']['value'],
                            "start_address": leg['start_address'],
                            "end_address": leg['end_address']
                        }
                    }
                else:
                    logger.error(f"No routes found for {strategy_name}: {directions_data}")
                    
            except Exception as e:
                logger.error(f"Error getting {strategy_name} route: {e}")
                # Use fallback data for this strategy
                routes[strategy_name] = await get_fallback_route_data(strategy_name, origin, destination)
        
        # If no routes found, use mock data
        if not routes:
            logger.warning("No routes found from Google Maps API, using mock data")
            return await get_mock_three_strategies(request)
        
        # Generate route comparison
        route_comparison = {}
        for strategy_name, route_data in routes.items():
            if 'raw_google_data' in route_data:
                route_comparison[strategy_name] = {
                    "distance_km": round(route_data['raw_google_data']['distance_meters'] / 1000, 1),
                    "duration_minutes": round(route_data['raw_google_data']['duration_seconds'] / 60),
                    "co2_emissions_kg": route_data['emissions']['co2_emissions_kg'],
                    "eco_score": route_data['emissions']['eco_score']
                }
        
        # Generate optimization suggestions
        suggestions = generate_optimization_suggestions(route_comparison)
        
        processing_time = round((time.time() - processing_start) * 1000, 1)
        
        return {
            "request_id": request_id,
            "processing_time_ms": processing_time,
            "routes": routes,
            "route_comparison": route_comparison,
            "optimization_suggestions": suggestions,
            "api_status": "real_google_maps_api",
            "metadata": {
                "origin": request.origin,
                "destination": request.destination,
                "travel_mode": request.travel_mode,
                "timestamp": time.time(),
                "origin_address": origin,
                "destination_address": destination
            }
        }

async def get_fallback_route_data(strategy_name: str, origin: str, destination: str):
    """Fallback route data when Google Maps API fails"""
    base_time = 45  # minutes
    base_distance = 35  # km
    
    multipliers = {
        'fastest': {'time': 0.8, 'distance': 0.9, 'emissions': 1.2},
        'eco_friendly': {'time': 1.3, 'distance': 1.2, 'emissions': 0.7}, 
        'balanced': {'time': 1.0, 'distance': 1.0, 'emissions': 1.0}
    }
    
    mult = multipliers.get(strategy_name, multipliers['balanced'])
    
    duration_minutes = int(base_time * mult['time'])
    distance_km = base_distance * mult['distance']
    distance_meters = int(distance_km * 1000)
    
    emissions = calculate_emissions(distance_meters, strategy_name)
    
    return {
        "total_distance": {"value": distance_meters, "text": f"{distance_km:.1f} km"},
        "total_duration": {"value": duration_minutes * 60, "text": f"{duration_minutes} mins"},
        "summary": f"Fallback route from {origin} to {destination}",
        "emissions": emissions,
        "strategy_info": {
            "strategy_metadata": {
                "strategy_focus": f"{strategy_name} optimization (fallback)",
                "optimization_factors": ["fallback_mode"]
            }
        }
    }

async def get_mock_three_strategies(request: ThreeStrategiesRequest):
    """Fallback to mock data when API key not available"""
    # Import the mock response from simple_server.py logic
    from simple_server import app as mock_app
    
    # Simulate the mock response
    await asyncio.sleep(0.1)
    
    return {
        "request_id": str(uuid.uuid4())[:8],
        "processing_time_ms": 100,
        "api_status": "mock_fallback",
        "routes": {
            "fastest": {
                "total_distance": {"value": 45200, "text": "45.2 km"},
                "total_duration": {"value": 5100, "text": "1 hour 25 mins"},
                "summary": "Mock fastest route (API key needed for real data)",
                "emissions": {"co2_emissions_kg": 8.4, "eco_score": 6.2, "fuel_consumption_liters": 3.6}
            },
            "eco_friendly": {
                "total_distance": {"value": 52100, "text": "52.1 km"},
                "total_duration": {"value": 6300, "text": "1 hour 45 mins"}, 
                "summary": "Mock eco-friendly route (API key needed for real data)",
                "emissions": {"co2_emissions_kg": 6.2, "eco_score": 8.7, "fuel_consumption_liters": 2.7}
            },
            "balanced": {
                "total_distance": {"value": 48700, "text": "48.7 km"},
                "total_duration": {"value": 5520, "text": "1 hour 32 mins"},
                "summary": "Mock balanced route (API key needed for real data)", 
                "emissions": {"co2_emissions_kg": 7.1, "eco_score": 7.5, "fuel_consumption_liters": 3.1}
            }
        }
    }

def generate_optimization_suggestions(route_comparison: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate optimization suggestions based on route comparison"""
    suggestions = []
    
    if 'fastest' in route_comparison and 'eco_friendly' in route_comparison:
        time_diff = route_comparison['eco_friendly']['duration_minutes'] - route_comparison['fastest']['duration_minutes']
        co2_savings = route_comparison['fastest']['co2_emissions_kg'] - route_comparison['eco_friendly']['co2_emissions_kg']
        
        if co2_savings > 0:
            suggestions.append({
                "message": f"Eco-friendly route saves {co2_savings:.1f}kg CO₂ with only {time_diff} extra minutes",
                "impact": "high" if co2_savings > 2 else "medium",
                "co2_savings_kg": co2_savings,
                "time_cost_minutes": time_diff
            })
    
    suggestions.append({
        "message": "Consider carpooling or public transport for even lower emissions",
        "impact": "high",
        "co2_savings_kg": 0,
        "rationale": "Public transport can reduce emissions by 45-65%"
    })
    
    return suggestions

# Root endpoint
@app.get("/")
async def root():
    api_key_status = "✅ Configured" if GOOGLE_MAPS_API_KEY != 'YOUR_API_KEY_HERE' else "❌ Not configured"
    
    return {
        "message": "PragatiDhara Google Maps Backend API",
        "version": "2.0.0",
        "api_key_status": api_key_status,
        "endpoints": {
            "health": "/health",
            "three_strategies": "/api/v1/routes/three-strategies",
            "documentation": "/docs"
        },
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    
    api_status = "✅" if GOOGLE_MAPS_API_KEY != 'YOUR_API_KEY_HERE' else "❌"
    
    print("🚀 Starting PragatiDhara Google Maps Backend...")
    print(f"📍 Server will be available at: http://127.0.0.1:8001")
    print(f"📚 API Documentation: http://127.0.0.1:8001/docs")
    print(f"🔑 Google Maps API Key: {api_status}")
    
    if GOOGLE_MAPS_API_KEY == 'YOUR_API_KEY_HERE':
        print("⚠️  WARNING: Google Maps API key not configured!")
        print("📖 See GOOGLE_MAPS_SETUP.md for setup instructions")
        print("🔄 Falling back to mock data for now...")
    
    uvicorn.run(
        "real_gmaps_server:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )