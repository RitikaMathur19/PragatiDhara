"""
Enhanced Google Maps Backend with Vehicle-Specific Fuel Cost Analysis
Supports multiple vehicle types: Petrol, Diesel, CNG, Electric, Hybrid
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import time
import uuid
import asyncio
import uvicorn
import random
import os
import json
from datetime import datetime
from pathlib import Path
import aiohttp
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    print(f"✅ Loaded environment from: {env_path}")
except ImportError:
    print("⚠️ python-dotenv not installed. Using system environment variables.")
except Exception as e:
    print(f"⚠️ Could not load .env file: {e}")

app = FastAPI(
    title="PragatiDhara Enhanced Backend",
    description="Vehicle-specific fuel cost analysis with comprehensive savings calculations",
    version="2.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Google Maps API Configuration
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')
MAPS_BASE_URL = "https://maps.googleapis.com/maps/api"
USE_REAL_GMAPS = bool(GOOGLE_MAPS_API_KEY and GOOGLE_MAPS_API_KEY != 'YOUR_API_KEY_HERE')

if USE_REAL_GMAPS:
    print(f"✅ Google Maps API configured - using real route data")
else:
    print(f"⚠️ Google Maps API not configured - using mock data")

# Vehicle-specific fuel/energy costs (current Indian market rates)
VEHICLE_COSTS = {
    "petrol": {
        "price_per_liter": 110.0,  # ₹110 per liter
        "efficiency_base": 15.0,   # 15 km/L average
        "unit": "L",
        "emission_factor": 2.31,   # kg CO2 per liter
        "display_name": "Petrol Car"
    },
    "diesel": {
        "price_per_liter": 95.0,   # ₹95 per liter  
        "efficiency_base": 18.0,   # 18 km/L average
        "unit": "L",
        "emission_factor": 2.68,   # kg CO2 per liter
        "display_name": "Diesel Car"
    },
    "cng": {
        "price_per_kg": 85.0,      # ₹85 per kg
        "efficiency_base": 25.0,   # 25 km/kg average
        "unit": "kg",
        "emission_factor": 2.75,   # kg CO2 per kg
        "display_name": "CNG Vehicle"
    },
    "electric": {
        "price_per_kwh": 8.0,      # ₹8 per kWh
        "efficiency_base": 5.0,    # 5 km/kWh average
        "unit": "kWh",
        "emission_factor": 0.82,   # kg CO2 per kWh (grid electricity)
        "display_name": "Electric Vehicle"
    },
    "hybrid_petrol": {
        "price_per_liter": 110.0,  # ₹110 per liter
        "efficiency_base": 22.0,   # 22 km/L average
        "unit": "L", 
        "emission_factor": 1.85,   # kg CO2 per liter (better efficiency)
        "display_name": "Hybrid Petrol"
    }
}

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
    vehicle_type: Optional[str] = "petrol"  # petrol, diesel, cng, electric, hybrid_petrol

class AIRecommendationRequest(BaseModel):
    routes: List[Dict[str, Any]]  # The three routes data
    vehicle_type: str

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "enhanced_maps_backend", 
        "version": "2.0.0",
        "supported_vehicles": list(VEHICLE_COSTS.keys()),
        "timestamp": time.time()
    }

def calculate_fuel_cost_and_consumption(distance_km: float, route_efficiency_factor: float, vehicle_type: str):
    """Calculate fuel/energy consumption and cost for specific route and vehicle"""
    vehicle_data = VEHICLE_COSTS.get(vehicle_type, VEHICLE_COSTS["petrol"])
    base_efficiency = vehicle_data["efficiency_base"]
    actual_efficiency = base_efficiency * route_efficiency_factor
    
    if vehicle_type == "electric":
        energy_consumed = distance_km / actual_efficiency  # kWh
        cost = energy_consumed * vehicle_data["price_per_kwh"]
        price_per_unit = vehicle_data["price_per_kwh"]
        fuel_consumed = energy_consumed  # For consistency in calculations
    elif vehicle_type == "cng":
        fuel_consumed = distance_km / actual_efficiency  # kg
        cost = fuel_consumed * vehicle_data["price_per_kg"]
        price_per_unit = vehicle_data["price_per_kg"]
    else:  # petrol, diesel, hybrid_petrol
        fuel_consumed = distance_km / actual_efficiency  # L
        cost = fuel_consumed * vehicle_data["price_per_liter"]
        price_per_unit = vehicle_data["price_per_liter"]
    
    emissions = fuel_consumed * vehicle_data["emission_factor"]
    
    return {
        "consumption": round(fuel_consumed, 2),
        "cost": round(cost, 2),
        "efficiency": round(actual_efficiency, 1),
        "cost_per_km": round(cost / distance_km, 2),
        "emissions_kg": round(emissions, 2),
        "unit": vehicle_data["unit"],
        "price_per_unit": price_per_unit,
        "vehicle_display": vehicle_data["display_name"]
    }

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
                return None
    except Exception as e:
        logger.error(f"Error calling Google Maps API: {e}")
        return None

def parse_location(location_data: Dict[str, Any]) -> str:
    """Parse location data to address string for Google Maps API"""
    if 'address' in location_data and location_data['address']:
        return location_data['address']
    elif 'lat' in location_data and 'lng' in location_data:
        return f"{location_data['lat']},{location_data['lng']}"
    else:
        logger.warning(f"Invalid location data: {location_data}")
        return "Pune, Maharashtra, India"  # Default fallback

def calculate_green_credits(distance_km: float, co2_saved_kg: float, optimization_mode: str) -> float:
    """
    Calculate green credits earned for a route based on distance and CO2 savings.
    
    Formula: Base credits (0.5 per km) + Bonus credits (5.0 per kg CO2 saved) × strategy multiplier
    
    Multipliers:
    - eco_friendly: 100% (full credits)
    - balanced: 60% (moderate credits)
    - fastest: 0% (no credits - speed-focused)
    """
    # Base credits for distance
    base_credits = distance_km * 0.5
    
    # Bonus credits for CO2 savings
    bonus_credits = max(0, co2_saved_kg) * 5.0
    
    # Total before multiplier
    total_credits = base_credits + bonus_credits
    
    # Apply strategy multiplier
    multipliers = {
        "eco_friendly": 1.0,   # 100% credits
        "balanced": 0.6,       # 60% credits
        "fastest": 0.0         # 0% credits (no reward for speed-focused)
    }
    
    multiplier = multipliers.get(optimization_mode, 0.6)
    final_credits = total_credits * multiplier
    
    return round(final_credits, 2)

async def generate_llm_recommendations(routes_data: Dict[str, Any], vehicle_type: str) -> Dict[str, Any]:
    """
    Generate personalized route recommendations using LLM analysis.
    Uses OpenAI-compatible API or Ollama, with fallback to rule-based recommendations.
    """
    try:
        from openai import AsyncOpenAI
        
        # Get configuration from environment
        use_openai = os.getenv("USE_OPENAI", "false").lower() in ("true", "1", "yes")
        api_base = os.getenv("OPENAI_API_BASE_URL", "http://34.67.10.255/api/v1")
        api_key = os.getenv("OPENAI_API_KEY", "pass")
        model_name = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-Math-1.5B-Instruct")
        temperature = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
        max_tokens = int(os.getenv("DEFAULT_MAX_TOKENS", "1000"))
        
        # Prepare route data for LLM
        fastest = routes_data.get("fastest", {})
        eco = routes_data.get("eco_friendly", {})
        balanced = routes_data.get("balanced", {})
        
        prompt = f"""You are a sustainability-focused transportation advisor passionate about environmental protection and eco-friendly travel. Your primary mission is to encourage users to choose routes that minimize environmental impact while still being practical. Prioritize eco-friendly and balanced routes that reduce carbon emissions, save fuel, and earn green credits.

IMPORTANT: Unless the time difference is extremely critical (>30 minutes extra), always lean towards recommending eco-friendly or balanced routes. Emphasize the environmental benefits, cost savings, and green credits earned.

Vehicle Type: {vehicle_type.upper()}

Route 1 - FASTEST (Speed-Focused, Higher Environmental Impact):
- Distance: {fastest.get('total_distance', {}).get('text', 'N/A')}
- Duration: {fastest.get('total_duration', {}).get('text', 'N/A')}
- Fuel Cost: ₹{fastest.get('fuel_analysis', {}).get('cost', 'N/A')}
- CO2 Emissions: {fastest.get('emissions', {}).get('co2_emissions_kg', 'N/A')} kg ⚠️
- Green Credits: {fastest.get('green_credits_earned', 0)} (NO REWARD for speed-focused travel)
- Eco Score: {fastest.get('emissions', {}).get('eco_score', 'N/A')}/10

Route 2 - ECO-FRIENDLY (🌱 RECOMMENDED FOR SUSTAINABILITY):
- Distance: {eco.get('total_distance', {}).get('text', 'N/A')}
- Duration: {eco.get('total_duration', {}).get('text', 'N/A')}
- Fuel Cost: ₹{eco.get('fuel_analysis', {}).get('cost', 'N/A')} 💰
- CO2 Emissions: {eco.get('emissions', {}).get('co2_emissions_kg', 'N/A')} kg 🌍
- Green Credits: {eco.get('green_credits_earned', 0)} ⭐ (MAXIMUM REWARD)
- Eco Score: {eco.get('emissions', {}).get('eco_score', 'N/A')}/10 ✅

Route 3 - BALANCED (Good Compromise):
- Distance: {balanced.get('total_distance', {}).get('text', 'N/A')}
- Duration: {balanced.get('total_duration', {}).get('text', 'N/A')}
- Fuel Cost: ₹{balanced.get('fuel_analysis', {}).get('cost', 'N/A')}
- CO2 Emissions: {balanced.get('emissions', {}).get('co2_emissions_kg', 'N/A')} kg
- Green Credits: {balanced.get('green_credits_earned', 0)} (60% reward)
- Eco Score: {balanced.get('emissions', {}).get('eco_score', 'N/A')}/10

Your Task:
Analyze these routes with a strong bias towards environmental sustainability. Calculate the environmental impact difference and make users aware of their carbon footprint choices. Encourage eco-friendly decisions by highlighting:
- Green credits earned (rewards for sustainable choices)
- CO2 emissions saved compared to fastest route
- Long-term cost savings from fuel efficiency
- Contribution to environmental protection
- Small time trade-offs for significant environmental benefits

Provide a JSON response with:
1. "recommended_route": Prefer "eco_friendly" unless time difference is extreme. Use "balanced" as second choice. Only recommend "fastest" if time savings are critical (>30 min) AND user explicitly needs speed.
2. "reasoning": Emphasize environmental benefits, green credits, and sustainability impact. Make it compelling and motivational. (max 2 sentences)
3. "key_insights": array of 3 insights that highlight environmental benefits, cost savings, and sustainability impact
4. "best_for_scenarios": object with keys "time_critical", "cost_conscious", "eco_conscious" - remember that eco_conscious should ALWAYS be "eco_friendly"

Format as valid JSON only, no markdown."""

        # Check if we should try OpenAI or skip directly to Ollama
        if not use_openai:
            print("ℹ️ USE_OPENAI=false, skipping OpenAI and using Ollama directly")
            raise ValueError("OpenAI disabled by configuration")

        try:
            # Try primary OpenAI-compatible endpoint
            print(f"🔄 Attempting OpenAI-compatible endpoint: {api_base}")
            client = AsyncOpenAI(
                base_url=api_base,
                api_key=api_key
            )
            
            response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a passionate environmental advocate and sustainable transportation expert. Your mission is to guide users toward eco-friendly travel choices that reduce carbon emissions and protect our planet. Always prioritize sustainability and environmental impact in your recommendations. Make users feel good about choosing green options and highlight the positive impact of their choices."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            llm_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                # Remove markdown code blocks if present
                clean_text = llm_text.replace('```json', '').replace('```', '').strip()
                llm_data = json.loads(clean_text)
                
                print(f"✅ OpenAI-compatible endpoint successful: {model_name}")
                return {
                    "source": "openai_compatible",
                    "model": model_name,
                    "timestamp": datetime.now().isoformat(),
                    **llm_data
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, return text response with eco-friendly default
                return {
                    "source": "openai_compatible_text",
                    "model": model_name,
                    "timestamp": datetime.now().isoformat(),
                    "recommended_route": "eco_friendly",  # Default to eco-friendly
                    "reasoning": llm_text[:200] if llm_text else "Choose eco-friendly for maximum environmental benefit and green credits!",
                    "key_insights": [
                        "🌱 Eco-friendly route reduces carbon emissions",
                        "💰 Save money while protecting the environment", 
                        "⭐ Earn maximum green credits for sustainable travel"
                    ],
                    "best_for_scenarios": {
                        "time_critical": "balanced",
                        "cost_conscious": "eco_friendly",
                        "eco_conscious": "eco_friendly"
                    }
                }
                
        except Exception as primary_error:
            print(f"⚠️ Primary LLM endpoint failed: {primary_error}")
            
            # Try Ollama fallback
            try:
                print("🔄 Attempting Ollama fallback...")
                ollama_base = os.getenv("OLLAMA_API_BASE_URL", "http://localhost:11434/v1")
                ollama_model = os.getenv("OLLAMA_MODEL_NAME", "gemma3:1b")
                ollama_key = os.getenv("OLLAMA_API_KEY", "ollama")
                
                print(f"📍 Ollama endpoint: {ollama_base}, model: {ollama_model}")
                
                client = AsyncOpenAI(
                    base_url=ollama_base,
                    api_key=ollama_key
                )
                
                response = await client.chat.completions.create(
                    model=ollama_model,
                    messages=[
                        {"role": "system", "content": "You are a passionate environmental advocate and sustainable transportation expert. Your mission is to guide users toward eco-friendly travel choices that reduce carbon emissions and protect our planet. Always prioritize sustainability and environmental impact in your recommendations. Make users feel good about choosing green options and highlight the positive impact of their choices."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                llm_text = response.choices[0].message.content.strip()
                clean_text = llm_text.replace('```json', '').replace('```', '').strip()
                
                try:
                    llm_data = json.loads(clean_text)
                    print(f"✅ Ollama endpoint successful: {ollama_model}")
                    return {
                        "source": "ollama",
                        "model": ollama_model,
                        "timestamp": datetime.now().isoformat(),
                        **llm_data
                    }
                except json.JSONDecodeError:
                    print(f"⚠️ Ollama JSON parse failed, using fallback")
                    return {
                        "source": "ollama_text",
                        "model": ollama_model,
                        "timestamp": datetime.now().isoformat(),
                        "recommended_route": "eco_friendly",  # Default to eco-friendly
                        "reasoning": llm_text[:200] if llm_text else "Choose eco-friendly for maximum environmental benefit!",
                        "key_insights": [
                            "🌱 Eco-friendly route reduces carbon emissions",
                            "💰 Save money while protecting the environment",
                            "⭐ Earn maximum green credits for sustainable travel"
                        ],
                        "best_for_scenarios": {
                            "time_critical": "balanced",
                            "cost_conscious": "eco_friendly",
                            "eco_conscious": "eco_friendly"
                        }
                    }
            except Exception as ollama_error:
                print(f"❌ Ollama fallback also failed: {ollama_error}")
                raise ValueError("All LLM endpoints unavailable")
            
    except Exception as e:
        # Fallback to rule-based recommendations
        print(f"ℹ️ LLM unavailable, using rule-based recommendations: {e}")
        return generate_rule_based_recommendations(routes_data, vehicle_type)

def generate_rule_based_recommendations(routes_data: Dict[str, Any], vehicle_type: str) -> Dict[str, Any]:
    """Generate intelligent sustainability-focused recommendations based on route analysis rules"""
    
    fastest = routes_data.get("fastest", {})
    eco = routes_data.get("eco_friendly", {})
    balanced = routes_data.get("balanced", {})
    
    # Extract key metrics
    fastest_cost = fastest.get('fuel_analysis', {}).get('cost', 999)
    eco_cost = eco.get('fuel_analysis', {}).get('cost', 999)
    balanced_cost = balanced.get('fuel_analysis', {}).get('cost', 999)
    
    fastest_duration = fastest.get('total_duration', {}).get('value', 9999) / 60  # Convert to minutes
    eco_duration = eco.get('total_duration', {}).get('value', 9999) / 60
    balanced_duration = balanced.get('total_duration', {}).get('value', 9999) / 60
    
    eco_credits = eco.get('green_credits_earned', 0)
    balanced_credits = balanced.get('green_credits_earned', 0)
    
    fastest_co2 = fastest.get('emissions', {}).get('co2_emissions_kg', 0)
    eco_co2 = eco.get('emissions', {}).get('co2_emissions_kg', 0)
    balanced_co2 = balanced.get('emissions', {}).get('co2_emissions_kg', 0)
    
    # Calculate savings
    cost_savings_eco = fastest_cost - eco_cost
    time_diff_eco = eco_duration - fastest_duration
    co2_saved_eco = fastest_co2 - eco_co2
    
    cost_savings_balanced = fastest_cost - balanced_cost
    time_diff_balanced = balanced_duration - fastest_duration
    co2_saved_balanced = fastest_co2 - balanced_co2
    
    # Sustainability-focused decision logic (strongly prefer eco-friendly)
    if time_diff_eco < 40:  # If eco route takes less than 40 min extra
        recommended = "eco_friendly"
        reasoning = f"🌱 Eco-friendly route saves {co2_saved_eco:.1f}kg CO2 and ₹{cost_savings_eco:.0f} with only {time_diff_eco:.0f} minutes extra time. Earn {eco_credits:.0f} green credits while protecting the environment!"
    elif time_diff_balanced < 20:  # If balanced is close in time
        recommended = "balanced"
        reasoning = f"⚖️ Balanced route offers great sustainability with {co2_saved_balanced:.1f}kg CO2 reduction and ₹{cost_savings_balanced:.0f} savings. A smart eco-conscious choice that respects your time!"
    elif cost_savings_eco > 30:  # If eco saves significant money
        recommended = "eco_friendly"
        reasoning = f"💰🌍 Eco-friendly route delivers substantial ₹{cost_savings_eco:.0f} savings and {co2_saved_eco:.1f}kg CO2 reduction. Your wallet and planet both benefit!"
    elif time_diff_eco > 50:  # Only if eco takes way too long
        recommended = "balanced"
        reasoning = f"⚖️ Balanced route provides the best compromise - {co2_saved_balanced:.1f}kg CO2 saved with minimal time impact. A responsible choice for sustainable {vehicle_type} travel."
    else:  # Default to eco-friendly
        recommended = "eco_friendly"
        reasoning = f"🌱 Eco-friendly route is the sustainable choice - reduce your carbon footprint by {co2_saved_eco:.1f}kg and save ₹{cost_savings_eco:.0f}. Every eco-friendly trip makes a difference!"
    
    # Generate sustainability-focused insights
    insights = [
        f"🌿 Choosing eco-friendly saves {co2_saved_eco:.1f}kg CO2 - equivalent to planting {int(co2_saved_eco * 0.5)} tree(s)!",
        f"⭐ Earn {eco_credits:.0f} green credits with eco route vs {balanced_credits:.0f} with balanced (0 for fastest)",
        f"💰 Annual savings potential: ₹{cost_savings_eco * 240:.0f} if you choose eco-friendly for daily commutes"
    ]
    
    return {
        "source": "rule_based",
        "timestamp": datetime.now().isoformat(),
        "recommended_route": recommended,
        "reasoning": reasoning,
        "key_insights": insights,
        "best_for_scenarios": {
            "time_critical": "balanced" if time_diff_eco > 30 else "eco_friendly",  # Even for time-critical, prefer eco if possible
            "cost_conscious": "eco_friendly",  # Eco is almost always cheapest
            "eco_conscious": "eco_friendly"  # Always eco for environmental focus
        },
        "environmental_impact": {
            "co2_saved_by_eco": f"{co2_saved_eco:.2f} kg",
            "co2_saved_by_balanced": f"{co2_saved_balanced:.2f} kg",
            "trees_equivalent": f"{int(co2_saved_eco * 0.5)} trees planted",
            "sustainability_score": "high" if recommended == "eco_friendly" else "medium"
        },
        "cost_analysis": {
            "cheapest_route": "eco_friendly" if eco_cost <= min(fastest_cost, balanced_cost) else "balanced",
            "max_savings": f"₹{cost_savings_eco:.2f}",
            "time_vs_sustainability_ratio": "excellent" if time_diff_eco < 20 else "good" if time_diff_eco < 40 else "moderate"
        }
    }

# Three-route strategies endpoint
@app.post("/api/v1/routes/three-strategies")
async def get_three_route_strategies(request: ThreeStrategiesRequest):
    """Generate three different route strategies with vehicle-specific optimization suggestions"""
    
    request_id = str(uuid.uuid4())[:8]
    processing_start = time.time()
    
    # Extract request info
    origin_info = request.origin.get('address', 'Unknown Origin')
    dest_info = request.destination.get('address', 'Unknown Destination')
    vehicle_type = request.vehicle_type or "petrol"
    
    # Validate vehicle type
    if vehicle_type not in VEHICLE_COSTS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported vehicle type: {vehicle_type}. Supported: {list(VEHICLE_COSTS.keys())}"
        )
    
    vehicle_data = VEHICLE_COSTS[vehicle_type]
    
    # Try to get real Google Maps data if API key is configured
    real_routes_data = None
    if USE_REAL_GMAPS:
        logger.info(f"🗺️ Fetching real routes from Google Maps API: {origin_info} → {dest_info}")
        try:
            origin = parse_location(request.origin)
            destination = parse_location(request.destination)
            
            async with aiohttp.ClientSession() as session:
                route_data = {}
                
                # Define three route strategies with Google Maps API parameters
                strategies = {
                    'fastest': {
                        'avoid': [],  # No restrictions
                        'description': 'Speed optimization with highway preference'
                    },
                    'eco_friendly': {
                        'avoid': ['highways', 'tolls'],  # Avoid highways and tolls
                        'description': 'Environmental impact minimization'
                    },
                    'balanced': {
                        'avoid': ['tolls'],  # Avoid only tolls
                        'description': 'Multi-criteria optimization'
                    }
                }
                
                for strategy_name, strategy_config in strategies.items():
                    params = {
                        'origin': origin,
                        'destination': destination,
                        'mode': 'driving',
                        'departure_time': 'now',
                        'alternatives': 'false'
                    }
                    
                    # Add avoid parameters
                    if strategy_config['avoid']:
                        params['avoid'] = '|'.join(strategy_config['avoid'])
                    
                    gmaps_result = await call_google_maps_api(session, 'directions/json', params)
                    
                    if gmaps_result and gmaps_result.get('status') == 'OK' and gmaps_result.get('routes'):
                        route = gmaps_result['routes'][0]
                        leg = route['legs'][0]
                        
                        distance_meters = leg['distance']['value']
                        distance_km = distance_meters / 1000
                        duration_seconds = leg['duration']['value']
                        
                        route_data[strategy_name] = {
                            'distance_km': distance_km,
                            'distance_meters': distance_meters,
                            'distance_text': leg['distance']['text'],
                            'duration_seconds': duration_seconds,
                            'duration_text': leg['duration']['text'],
                            'summary': route.get('summary', f"{strategy_name} route"),
                            'start_address': leg.get('start_address', origin_info),
                            'end_address': leg.get('end_address', dest_info)
                        }
                        logger.info(f"  ✅ {strategy_name}: {distance_km:.1f} km, {duration_seconds//60} min")
                    else:
                        logger.warning(f"  ⚠️ No route found for {strategy_name} strategy")
                
                if len(route_data) == 3:
                    real_routes_data = route_data
                    logger.info(f"✅ Successfully fetched all 3 real routes from Google Maps")
                else:
                    logger.warning(f"⚠️ Only got {len(route_data)}/3 routes, falling back to mock data")
                    
        except Exception as e:
            logger.error(f"❌ Error fetching Google Maps data: {e}")
            logger.info(f"ℹ️ Falling back to mock data")
    
    # Use real data if available, otherwise use mock data
    if real_routes_data:
        # Calculate with REAL route data
        fastest_data = real_routes_data['fastest']
        eco_data = real_routes_data['eco_friendly']
        balanced_data = real_routes_data['balanced']
        
        # Adjust efficiency factors based on route type
        fastest_calc = calculate_fuel_cost_and_consumption(fastest_data['distance_km'], 0.85, vehicle_type)
        eco_calc = calculate_fuel_cost_and_consumption(eco_data['distance_km'], 1.15, vehicle_type)
        balanced_calc = calculate_fuel_cost_and_consumption(balanced_data['distance_km'], 1.0, vehicle_type)
        
        # Use real distance and duration
        routes_distances = {
            'fastest': {'km': fastest_data['distance_km'], 'meters': fastest_data['distance_meters'], 'text': fastest_data['distance_text'], 'duration_sec': fastest_data['duration_seconds'], 'duration_text': fastest_data['duration_text'], 'summary': fastest_data['summary']},
            'eco_friendly': {'km': eco_data['distance_km'], 'meters': eco_data['distance_meters'], 'text': eco_data['distance_text'], 'duration_sec': eco_data['duration_seconds'], 'duration_text': eco_data['duration_text'], 'summary': eco_data['summary']},
            'balanced': {'km': balanced_data['distance_km'], 'meters': balanced_data['distance_meters'], 'text': balanced_data['distance_text'], 'duration_sec': balanced_data['duration_seconds'], 'duration_text': balanced_data['duration_text'], 'summary': balanced_data['summary']}
        }
        data_source = "google_maps_api"
    else:
        # Use MOCK data (fallback)
        await asyncio.sleep(0.2)  # Simulate processing
        
        fastest_calc = calculate_fuel_cost_and_consumption(45.2, 0.85, vehicle_type)
        eco_calc = calculate_fuel_cost_and_consumption(52.1, 1.15, vehicle_type)
        balanced_calc = calculate_fuel_cost_and_consumption(48.7, 1.0, vehicle_type)
        
        routes_distances = {
            'fastest': {'km': 45.2, 'meters': 45200, 'text': '45.2 km', 'duration_sec': 5100, 'duration_text': '1 hour 25 mins', 'summary': f'Via highways from {origin_info} to {dest_info}'},
            'eco_friendly': {'km': 52.1, 'meters': 52100, 'text': '52.1 km', 'duration_sec': 6300, 'duration_text': '1 hour 45 mins', 'summary': f'Via eco-routes from {origin_info} to {dest_info}'},
            'balanced': {'km': 48.7, 'meters': 48700, 'text': '48.7 km', 'duration_sec': 5520, 'duration_text': '1 hour 32 mins', 'summary': f'Optimized balance from {origin_info} to {dest_info}'}
        }
        data_source = "mock_data"
    
    # Calculate CO2 savings compared to fastest route (baseline)
    fastest_co2 = fastest_calc["emissions_kg"]
    eco_co2_saved = fastest_co2 - eco_calc["emissions_kg"]
    balanced_co2_saved = fastest_co2 - balanced_calc["emissions_kg"]
    
    # Calculate green credits for each route
    fastest_credits = calculate_green_credits(routes_distances['fastest']['km'], 0, "fastest")
    eco_credits = calculate_green_credits(routes_distances['eco_friendly']['km'], eco_co2_saved, "eco_friendly")
    balanced_credits = calculate_green_credits(routes_distances['balanced']['km'], balanced_co2_saved, "balanced")
    
    # Generate three distinct routes with vehicle-specific calculations
    routes = {
        "fastest": {
            "type": "fastest",
            "color": "#FF6B00",  # Dark Orange
            "total_distance": {"value": routes_distances['fastest']['meters'], "text": routes_distances['fastest']['text']},
            "total_duration": {"value": routes_distances['fastest']['duration_sec'], "text": routes_distances['fastest']['duration_text']},
            "summary": routes_distances['fastest']['summary'],
            "vehicle_type": vehicle_type,
            "green_credits_earned": fastest_credits,
            "emissions": {
                "co2_emissions_kg": fastest_calc["emissions_kg"],
                "eco_score": 6.2 if vehicle_type != "electric" else 9.2,
                "fuel_consumption_liters": fastest_calc["consumption"]
            },
            "fuel_analysis": fastest_calc,
            "strategy_info": {
                "strategy_metadata": {
                    "strategy_focus": "Speed optimization with highway preference",
                    "optimization_factors": ["highways", "tolls_allowed", "traffic_avoidance"],
                    "route_characteristics": [
                        f"Higher {vehicle_data['unit']} consumption" if vehicle_type != "electric" else "Higher kWh consumption",
                        "Fast travel time", 
                        "Highway tolls applicable"
                    ]
                }
            }
        },
        "eco_friendly": {
            "type": "eco-friendly", 
            "color": "#006400",  # Dark Green
            "total_distance": {"value": routes_distances['eco_friendly']['meters'], "text": routes_distances['eco_friendly']['text']},
            "total_duration": {"value": routes_distances['eco_friendly']['duration_sec'], "text": routes_distances['eco_friendly']['duration_text']},
            "summary": routes_distances['eco_friendly']['summary'],
            "vehicle_type": vehicle_type,
            "green_credits_earned": eco_credits,
            "emissions": {
                "co2_emissions_kg": eco_calc["emissions_kg"],
                "eco_score": 8.7 if vehicle_type != "electric" else 9.8,
                "fuel_consumption_liters": eco_calc["consumption"]
            },
            "fuel_analysis": eco_calc,
            "strategy_info": {
                "strategy_metadata": {
                    "strategy_focus": "Environmental impact minimization",
                    "optimization_factors": ["local_roads", "fuel_efficiency", "emissions_reduction"],
                    "route_characteristics": [
                        f"Lowest {vehicle_data['unit']} consumption" if vehicle_type != "electric" else "Lowest kWh consumption",
                        "Eco-friendly driving", 
                        "No highway tolls"
                    ]
                }
            }
        },
        "balanced": {
            "type": "balanced",
            "color": "#000080",  # Dark Blue
            "total_distance": {"value": routes_distances['balanced']['meters'], "text": routes_distances['balanced']['text']},
            "total_duration": {"value": routes_distances['balanced']['duration_sec'], "text": routes_distances['balanced']['duration_text']},
            "summary": routes_distances['balanced']['summary'],
            "vehicle_type": vehicle_type,
            "green_credits_earned": balanced_credits,
            "emissions": {
                "co2_emissions_kg": balanced_calc["emissions_kg"],
                "eco_score": 7.5 if vehicle_type != "electric" else 9.5,
                "fuel_consumption_liters": balanced_calc["consumption"]
            },
            "fuel_analysis": balanced_calc,
            "strategy_info": {
                "strategy_metadata": {
                    "strategy_focus": "Multi-criteria optimization",
                    "optimization_factors": ["time_balance", "eco_balance", "cost_efficiency"],
                    "route_characteristics": [
                        f"Moderate {vehicle_data['unit']} consumption" if vehicle_type != "electric" else "Moderate kWh consumption",
                        "Balanced time-cost ratio", 
                        "Selected highways only"
                    ]
                }
            }
        }
    }
    
    # Calculate detailed savings comparison
    fastest_cost = fastest_calc["cost"]
    eco_cost = eco_calc["cost"]
    balanced_cost = balanced_calc["cost"]
    
    # Route comparison summary with vehicle-specific analysis using ACTUAL route distances
    route_comparison = {
        "fastest": {
            "distance_km": routes_distances['fastest']['km'],
            "duration_minutes": routes_distances['fastest']['duration_sec'] // 60,
            "co2_emissions_kg": fastest_calc["emissions_kg"],
            "eco_score": routes["fastest"]["emissions"]["eco_score"],
            "fuel_cost_inr": fastest_cost,
            "fuel_efficiency": fastest_calc["efficiency"],
            "savings_vs_fastest": {"cost": 0, "fuel": 0, "percentage": "0%"},
            "savings_vs_eco": {
                "cost": round(eco_cost - fastest_cost, 2),
                "fuel": round(eco_calc["consumption"] - fastest_calc["consumption"], 2),
                "percentage": f"{round(((eco_cost - fastest_cost) / fastest_cost) * 100, 1)}%" if fastest_cost > 0 else "0%"
            },
            "savings_vs_balanced": {
                "cost": round(balanced_cost - fastest_cost, 2),
                "fuel": round(balanced_calc["consumption"] - fastest_calc["consumption"], 2),
                "percentage": f"{round(((balanced_cost - fastest_cost) / fastest_cost) * 100, 1)}%" if fastest_cost > 0 else "0%"
            }
        },
        "eco_friendly": {
            "distance_km": routes_distances['eco_friendly']['km'],
            "duration_minutes": routes_distances['eco_friendly']['duration_sec'] // 60, 
            "co2_emissions_kg": eco_calc["emissions_kg"],
            "eco_score": routes["eco_friendly"]["emissions"]["eco_score"],
            "fuel_cost_inr": eco_cost,
            "fuel_efficiency": eco_calc["efficiency"],
            "savings_vs_fastest": {
                "cost": round(fastest_cost - eco_cost, 2),
                "fuel": round(fastest_calc["consumption"] - eco_calc["consumption"], 2),
                "percentage": f"{round(((fastest_cost - eco_cost) / fastest_cost) * 100, 1)}%" if fastest_cost > 0 else "0%"
            },
            "savings_vs_eco": {"cost": 0, "fuel": 0, "percentage": "0%"},
            "savings_vs_balanced": {
                "cost": round(balanced_cost - eco_cost, 2),
                "fuel": round(balanced_calc["consumption"] - eco_calc["consumption"], 2),
                "percentage": f"{round(((balanced_cost - eco_cost) / eco_cost) * 100, 1)}%" if eco_cost > 0 else "0%"
            }
        },
        "balanced": {
            "distance_km": routes_distances['balanced']['km'],
            "duration_minutes": routes_distances['balanced']['duration_sec'] // 60,
            "co2_emissions_kg": balanced_calc["emissions_kg"],
            "eco_score": routes["balanced"]["emissions"]["eco_score"],
            "fuel_cost_inr": balanced_cost,
            "fuel_efficiency": balanced_calc["efficiency"],
            "savings_vs_fastest": {
                "cost": round(fastest_cost - balanced_cost, 2),
                "fuel": round(fastest_calc["consumption"] - balanced_calc["consumption"], 2),
                "percentage": f"{round(((fastest_cost - balanced_cost) / fastest_cost) * 100, 1)}%" if fastest_cost > 0 else "0%"
            },
            "savings_vs_eco": {
                "cost": round(eco_cost - balanced_cost, 2),
                "fuel": round(eco_calc["consumption"] - balanced_calc["consumption"], 2),
                "percentage": f"{round(((eco_cost - balanced_cost) / eco_cost) * 100, 1)}%" if eco_cost > 0 else "0%"
            },
            "savings_vs_balanced": {"cost": 0, "fuel": 0, "percentage": "0%"}
        }
    }
    
    # Generate vehicle-specific optimization suggestions
    fastest_vs_eco_savings = round(fastest_cost - eco_cost, 2)
    fastest_vs_balanced_savings = round(fastest_cost - balanced_cost, 2)
    
    suggestions = [
        {
            "title": f"🌱 Choose Eco-Friendly Route for Maximum {vehicle_data['display_name']} Savings",
            "message": f"Eco-friendly route saves ₹{fastest_vs_eco_savings} in {vehicle_type} costs compared to fastest route",
            "impact": "high",
            "savings_minutes": -20,
            "fuel_savings_inr": fastest_vs_eco_savings,
            "fuel_savings_amount": round(fastest_calc["consumption"] - eco_calc["consumption"], 2),
            "co2_savings_kg": round(fastest_calc["emissions_kg"] - eco_calc["emissions_kg"], 2),
            "route_color": "#006400",
            "details": f"Save {round(fastest_calc['consumption'] - eco_calc['consumption'], 2)}{vehicle_data['unit']} • {round(((fastest_vs_eco_savings/fastest_cost)*100), 1) if fastest_cost > 0 else 0}% cost reduction",
            "vehicle_specific": f"Optimized for {vehicle_data['display_name']} efficiency"
        },
        {
            "title": f"⚖️ Balanced Route for Optimal {vehicle_data['display_name']} Cost-Time Trade-off", 
            "message": f"Balanced route saves ₹{fastest_vs_balanced_savings} with only 7 minutes extra time",
            "impact": "medium",
            "savings_minutes": -7,
            "fuel_savings_inr": fastest_vs_balanced_savings,
            "fuel_savings_amount": round(fastest_calc["consumption"] - balanced_calc["consumption"], 2),
            "co2_savings_kg": round(fastest_calc["emissions_kg"] - balanced_calc["emissions_kg"], 2),
            "route_color": "#000080",
            "details": f"Save {round(fastest_calc['consumption'] - balanced_calc['consumption'], 2)}{vehicle_data['unit']} • Best time-cost balance",
            "vehicle_specific": f"Ideal compromise for {vehicle_data['display_name']} users"
        },
        {
            "title": f"🚀 Fastest Route - Premium {vehicle_data['display_name']} Speed Choice",
            "message": f"Fastest route costs ₹{round(fastest_cost - eco_cost, 2)} extra but saves 20 minutes",
            "impact": "low",
            "savings_minutes": 20,
            "fuel_cost_extra": round(fastest_cost - eco_cost, 2),
            "fuel_extra_amount": round(fastest_calc["consumption"] - eco_calc["consumption"], 2),
            "route_color": "#FF6B00", 
            "details": f"Extra {round(fastest_calc['consumption'] - eco_calc['consumption'], 2)}{vehicle_data['unit']} • Premium for time-sensitive travel",
            "vehicle_specific": f"Highway optimized for {vehicle_data['display_name']}"
        }
    ]
    
    processing_time = round((time.time() - processing_start) * 1000, 1)
    
    # Comprehensive vehicle-specific fuel cost summary
    fuel_cost_summary = {
        "vehicle_info": {
            "type": vehicle_type,
            "display_name": vehicle_data["display_name"],
            "unit": vehicle_data["unit"],
            "price_per_unit": vehicle_data.get("price_per_liter", vehicle_data.get("price_per_kg", vehicle_data.get("price_per_kwh"))),
            "base_efficiency": f"{vehicle_data['efficiency_base']} km/{vehicle_data['unit']}"
        },
        "routes_analysis": {
            "fastest_route": {
                "color": "#FF6B00",
                "consumption": fastest_calc["consumption"],
                "cost": fastest_cost,
                "efficiency": fastest_calc["efficiency"],
                "cost_per_km": fastest_calc["cost_per_km"]
            },
            "eco_friendly_route": {
                "color": "#006400", 
                "consumption": eco_calc["consumption"],
                "cost": eco_cost,
                "efficiency": eco_calc["efficiency"],
                "cost_per_km": eco_calc["cost_per_km"]
            },
            "balanced_route": {
                "color": "#000080",
                "consumption": balanced_calc["consumption"],
                "cost": balanced_cost,
                "efficiency": balanced_calc["efficiency"],
                "cost_per_km": balanced_calc["cost_per_km"]
            }
        },
        "savings_comparison": {
            "eco_vs_fastest": {
                "amount_saved": round(fastest_calc["consumption"] - eco_calc["consumption"], 2),
                "cost_saved_inr": round(fastest_cost - eco_cost, 2),
                "percentage_saved": f"{round(((fastest_cost - eco_cost) / fastest_cost) * 100, 1)}%" if fastest_cost > 0 else "0%"
            },
            "balanced_vs_fastest": {
                "amount_saved": round(fastest_calc["consumption"] - balanced_calc["consumption"], 2),
                "cost_saved_inr": round(fastest_cost - balanced_cost, 2),
                "percentage_saved": f"{round(((fastest_cost - balanced_cost) / fastest_cost) * 100, 1)}%" if fastest_cost > 0 else "0%"
            }
        },
        "monthly_projections": {
            "trips_per_month": 20,
            "eco_monthly_savings": round((fastest_cost - eco_cost) * 20, 2),
            "balanced_monthly_savings": round((fastest_cost - balanced_cost) * 20, 2),
            "annual_potential_eco": round((fastest_cost - eco_cost) * 240, 2),  # 20 trips * 12 months
            "annual_potential_balanced": round((fastest_cost - balanced_cost) * 240, 2)
        },
        "recommendations": {
            "most_economical": "eco_friendly",
            "best_value": "balanced", 
            "fastest_option": "fastest",
            "best_for_environment": "eco_friendly" if vehicle_type != "electric" else "All routes (zero local emissions)"
        }
    }
    
    # AI recommendations are now loaded separately via /ai-recommendations endpoint
    # This keeps the main response fast and non-blocking
    
    return {
        "request_id": request_id,
        "processing_time_ms": processing_time,
        "routes": [routes["fastest"], routes["eco_friendly"], routes["balanced"]],
        "route_comparison": route_comparison,
        "fuel_cost_summary": fuel_cost_summary,
        "optimization_suggestions": suggestions,
        "data_source": data_source,  # Indicates if using real Google Maps or mock data
        "metadata": {
            "origin": request.origin,
            "destination": request.destination,
            "travel_mode": request.travel_mode,
            "vehicle_type": vehicle_type,
            "vehicle_display": vehicle_data["display_name"],
            "timestamp": time.time(),
            "pricing_source": f"Current Indian market rates for {vehicle_data['display_name']}",
            "google_maps_enabled": USE_REAL_GMAPS
        }
    }

# Simple route calculation endpoint
@app.post("/api/v1/routes/calculate")
async def calculate_route(request: RouteRequest):
    """Basic route calculation endpoint"""
    
    await asyncio.sleep(0.1)
    
    return {
        "request_id": str(uuid.uuid4())[:8],
        "route": {
            "distance": {"value": 42000, "text": "42.0 km"},
            "duration": {"value": 4800, "text": "1 hour 20 mins"},
            "summary": f"Route from {request.origin} to {request.destination}",
        },
        "status": "success"
    }

# AI Recommendations endpoint (separate for async loading)
@app.post("/api/v1/routes/ai-recommendations")
async def get_ai_recommendations(request: AIRecommendationRequest):
    """
    Generate AI-powered route recommendations asynchronously.
    This endpoint can be called separately to avoid blocking the main route response.
    """
    try:
        # Convert routes list to dict format expected by the function
        routes_dict = {}
        for route in request.routes:
            route_type = route.get('type', '')
            if route_type == 'fastest':
                routes_dict['fastest'] = route
            elif route_type == 'eco-friendly':
                routes_dict['eco_friendly'] = route
            elif route_type == 'balanced':
                routes_dict['balanced'] = route
        
        # Generate recommendations
        recommendations = await generate_llm_recommendations(routes_dict, request.vehicle_type)
        
        return {
            "success": True,
            "recommendations": recommendations,
            "timestamp": time.time()
        }
    except Exception as e:
        # Return error but don't fail - fall back to rule-based
        print(f"AI recommendations error: {e}")
        return {
            "success": False,
            "error": str(e),
            "recommendations": generate_rule_based_recommendations(
                {route.get('type', ''): route for route in request.routes},
                request.vehicle_type
            ),
            "timestamp": time.time()
        }

# Get available vehicle types
@app.get("/api/v1/vehicles")
async def get_vehicle_types():
    """Get all supported vehicle types with their specifications"""
    return {
        "supported_vehicles": {
            vehicle_type: {
                "display_name": data["display_name"],
                "unit": data["unit"],
                "base_efficiency": f"{data['efficiency_base']} km/{data['unit']}",
                "fuel_cost_per_unit": data.get("price_per_liter", data.get("price_per_kg", data.get("price_per_kwh"))),
                "emission_factor": f"{data['emission_factor']} kg CO₂/{data['unit']}"
            }
            for vehicle_type, data in VEHICLE_COSTS.items()
        },
        "recommended_defaults": {
            "city_driving": "petrol",
            "highway_driving": "diesel",
            "environmental_focus": "electric",
            "cost_effective": "cng",
            "balanced_option": "hybrid_petrol"
        }
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "PragatiDhara Enhanced Backend API",
        "version": "2.0.0",
        "features": [
            "Vehicle-specific fuel cost analysis",
            "Multi-vehicle support (Petrol, Diesel, CNG, Electric, Hybrid)",
            "Comprehensive savings calculations",
            "Route optimization strategies",
            "Environmental impact assessment"
        ],
        "endpoints": {
            "health": "/health",
            "vehicles": "/api/v1/vehicles",
            "three_strategies": "/api/v1/routes/three-strategies",
            "basic_route": "/api/v1/routes/calculate",
            "documentation": "/docs"
        },
        "supported_vehicles": list(VEHICLE_COSTS.keys()),
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
if __name__ == "__main__":
    print("🚀 Starting PragatiDhara Enhanced Backend...")
    print("📍 Server will be available at: http://127.0.0.1:8001")
    print("📚 API Documentation: http://127.0.0.1:8001/docs")
    print("🚗 Supported Vehicles:", ", ".join(VEHICLE_COSTS.keys()))
    
    uvicorn.run(
        "enhanced_server:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )