"""
Simple Test Server for Google Maps Backend
This is a minimal version to test the three-route strategy integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import time
import uuid
import asyncio
import random

app = FastAPI(
    title="Google Maps Test Backend",
    description="Simple test server for three-route strategy",
    version="1.0.0"
)

# Vehicle-specific fuel/energy costs (current Indian market rates)
VEHICLE_COSTS = {
    "petrol": {
        "price_per_liter": 110.0,  # ₹110 per liter
        "efficiency_base": 15.0,   # 15 km/L average
        "unit": "L",
        "emission_factor": 2.31    # kg CO2 per liter
    },
    "diesel": {
        "price_per_liter": 95.0,   # ₹95 per liter  
        "efficiency_base": 18.0,   # 18 km/L average
        "unit": "L",
        "emission_factor": 2.68    # kg CO2 per liter
    },
    "cng": {
        "price_per_kg": 85.0,      # ₹85 per kg
        "efficiency_base": 25.0,   # 25 km/kg average
        "unit": "kg",
        "emission_factor": 2.75    # kg CO2 per kg
    },
    "electric": {
        "price_per_kwh": 8.0,      # ₹8 per kWh
        "efficiency_base": 5.0,    # 5 km/kWh average
        "unit": "kWh",
        "emission_factor": 0.82    # kg CO2 per kWh (grid electricity)
    },
    "hybrid_petrol": {
        "price_per_liter": 110.0,  # ₹110 per liter
        "efficiency_base": 22.0,   # 22 km/L average
        "unit": "L", 
        "emission_factor": 1.85    # kg CO2 per liter (better efficiency)
    }
}

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

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

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "google_maps_test_backend", 
        "version": "1.0.0",
        "timestamp": time.time()
    }

# Three-route strategies endpoint
@app.post("/api/v1/routes/three-strategies")
async def get_three_route_strategies(request: ThreeStrategiesRequest):
    """Generate three different route strategies with optimization suggestions"""
    
    # Simulate processing time
    await asyncio.sleep(0.2)  # 200ms simulated processing
    
    request_id = str(uuid.uuid4())[:8]
    processing_start = time.time()
    
    # Extract origin/destination info for simulation
    origin_info = request.origin.get('address', 'Unknown Origin')
    dest_info = request.destination.get('address', 'Unknown Destination')
    vehicle_type = request.vehicle_type or "petrol"
    
    # Get vehicle-specific cost data
    vehicle_data = VEHICLE_COSTS.get(vehicle_type, VEHICLE_COSTS["petrol"])
    
    def calculate_fuel_cost_and_consumption(distance_km: float, route_efficiency_factor: float):
        """Calculate fuel/energy consumption and cost for specific route"""
        base_efficiency = vehicle_data["efficiency_base"]
        actual_efficiency = base_efficiency * route_efficiency_factor
        
        if vehicle_type == "electric":
            energy_consumed = distance_km / actual_efficiency  # kWh
            cost = energy_consumed * vehicle_data["price_per_kwh"]
        elif vehicle_type == "cng":
            fuel_consumed = distance_km / actual_efficiency  # kg
            cost = fuel_consumed * vehicle_data["price_per_kg"]
        else:  # petrol, diesel, hybrid_petrol
            fuel_consumed = distance_km / actual_efficiency  # L
            cost = fuel_consumed * vehicle_data["price_per_liter"]
        
        emissions = fuel_consumed * vehicle_data["emission_factor"]
        
        return {
            "consumption": round(fuel_consumed, 2),
            "cost": round(cost, 2),
            "efficiency": round(actual_efficiency, 1),
            "cost_per_km": round(cost / distance_km, 2),
            "emissions_kg": round(emissions, 2)
        }
    
    # Generate three distinct routes with realistic differences and detailed fuel analysis
    routes = {
        "fastest": {
            "type": "fastest",
            "color": "#FF6B00",  # Dark Orange
            "total_distance": {"value": 45200, "text": "45.2 km"},
            "total_duration": {"value": 5100, "text": "1 hour 25 mins"},
            "summary": f"Via highways from {origin_info} to {dest_info}",
            "emissions": {
                "co2_emissions_kg": 8.4,
                "eco_score": 6.2,
                "fuel_consumption_liters": 3.6
            },
            "fuel_analysis": {
                "fuel_consumption_liters": 3.6,
                "fuel_cost_inr": round(3.6 * FUEL_PRICE_PER_LITER, 2),
                "fuel_efficiency_kmpl": round(45.2 / 3.6, 1),
                "cost_per_km": round((3.6 * FUEL_PRICE_PER_LITER) / 45.2, 2)
            },
            "strategy_info": {
                "strategy_metadata": {
                    "strategy_focus": "Speed optimization with highway preference",
                    "optimization_factors": ["highways", "tolls_allowed", "traffic_avoidance"],
                    "route_characteristics": ["High fuel consumption", "Fast travel time", "Highway tolls"]
                }
            }
        },
        "eco_friendly": {
            "type": "eco-friendly", 
            "color": "#006400",  # Dark Green
            "total_distance": {"value": 52100, "text": "52.1 km"},
            "total_duration": {"value": 6300, "text": "1 hour 45 mins"},
            "summary": f"Via eco-routes from {origin_info} to {dest_info}",
            "emissions": {
                "co2_emissions_kg": 6.2,
                "eco_score": 8.7,
                "fuel_consumption_liters": 2.7
            },
            "fuel_analysis": {
                "fuel_consumption_liters": 2.7,
                "fuel_cost_inr": round(2.7 * FUEL_PRICE_PER_LITER, 2),
                "fuel_efficiency_kmpl": round(52.1 / 2.7, 1),
                "cost_per_km": round((2.7 * FUEL_PRICE_PER_LITER) / 52.1, 2)
            },
            "strategy_info": {
                "strategy_metadata": {
                    "strategy_focus": "Environmental impact minimization",
                    "optimization_factors": ["local_roads", "fuel_efficiency", "emissions_reduction"],
                    "route_characteristics": ["Lowest fuel consumption", "Eco-friendly driving", "No highway tolls"]
                }
            }
        },
        "balanced": {
            "type": "balanced",
            "color": "#000080",  # Dark Blue
            "total_distance": {"value": 48700, "text": "48.7 km"},
            "total_duration": {"value": 5520, "text": "1 hour 32 mins"},
            "summary": f"Optimized balance from {origin_info} to {dest_info}",
            "emissions": {
                "co2_emissions_kg": 7.1,
                "eco_score": 7.5,
                "fuel_consumption_liters": 3.1
            },
            "fuel_analysis": {
                "fuel_consumption_liters": 3.1,
                "fuel_cost_inr": round(3.1 * FUEL_PRICE_PER_LITER, 2),
                "fuel_efficiency_kmpl": round(48.7 / 3.1, 1),
                "cost_per_km": round((3.1 * FUEL_PRICE_PER_LITER) / 48.7, 2)
            },
            "strategy_info": {
                "strategy_metadata": {
                    "strategy_focus": "Multi-criteria optimization",
                    "optimization_factors": ["time_balance", "eco_balance", "cost_efficiency"],
                    "route_characteristics": ["Moderate fuel consumption", "Balanced time-cost ratio", "Selected highways"]
                }
            }
        }
    }
    
    # Calculate fuel savings and cost differences relative to each route
    fastest_cost = routes["fastest"]["fuel_analysis"]["fuel_cost_inr"]
    eco_cost = routes["eco_friendly"]["fuel_analysis"]["fuel_cost_inr"] 
    balanced_cost = routes["balanced"]["fuel_analysis"]["fuel_cost_inr"]
    
    # Route comparison summary with detailed fuel cost analysis
    route_comparison = {
        "fastest": {
            "distance_km": 45.2,
            "duration_minutes": 85,
            "co2_emissions_kg": 8.4,
            "eco_score": 6.2,
            "fuel_cost_inr": fastest_cost,
            "fuel_efficiency_kmpl": routes["fastest"]["fuel_analysis"]["fuel_efficiency_kmpl"],
            "savings_vs_fastest": {"cost": 0, "fuel_liters": 0, "percentage": "0%"},
            "savings_vs_eco": {
                "cost": round(eco_cost - fastest_cost, 2),
                "fuel_liters": round(routes["eco_friendly"]["fuel_analysis"]["fuel_consumption_liters"] - 3.6, 1),
                "percentage": f"{round(((eco_cost - fastest_cost) / fastest_cost) * 100, 1)}%" if fastest_cost > 0 else "0%"
            },
            "savings_vs_balanced": {
                "cost": round(balanced_cost - fastest_cost, 2),
                "fuel_liters": round(routes["balanced"]["fuel_analysis"]["fuel_consumption_liters"] - 3.6, 1),
                "percentage": f"{round(((balanced_cost - fastest_cost) / fastest_cost) * 100, 1)}%" if fastest_cost > 0 else "0%"
            }
        },
        "eco_friendly": {
            "distance_km": 52.1,
            "duration_minutes": 105, 
            "co2_emissions_kg": 6.2,
            "eco_score": 8.7,
            "fuel_cost_inr": eco_cost,
            "fuel_efficiency_kmpl": routes["eco_friendly"]["fuel_analysis"]["fuel_efficiency_kmpl"],
            "savings_vs_fastest": {
                "cost": round(fastest_cost - eco_cost, 2),
                "fuel_liters": round(3.6 - routes["eco_friendly"]["fuel_analysis"]["fuel_consumption_liters"], 1),
                "percentage": f"{round(((fastest_cost - eco_cost) / fastest_cost) * 100, 1)}%" if fastest_cost > 0 else "0%"
            },
            "savings_vs_eco": {"cost": 0, "fuel_liters": 0, "percentage": "0%"},
            "savings_vs_balanced": {
                "cost": round(balanced_cost - eco_cost, 2),
                "fuel_liters": round(routes["balanced"]["fuel_analysis"]["fuel_consumption_liters"] - 2.7, 1),
                "percentage": f"{round(((balanced_cost - eco_cost) / eco_cost) * 100, 1)}%" if eco_cost > 0 else "0%"
            }
        },
        "balanced": {
            "distance_km": 48.7,
            "duration_minutes": 92,
            "co2_emissions_kg": 7.1,
            "eco_score": 7.5,
            "fuel_cost_inr": balanced_cost,
            "fuel_efficiency_kmpl": routes["balanced"]["fuel_analysis"]["fuel_efficiency_kmpl"],
            "savings_vs_fastest": {
                "cost": round(fastest_cost - balanced_cost, 2),
                "fuel_liters": round(3.6 - routes["balanced"]["fuel_analysis"]["fuel_consumption_liters"], 1),
                "percentage": f"{round(((fastest_cost - balanced_cost) / fastest_cost) * 100, 1)}%" if fastest_cost > 0 else "0%"
            },
            "savings_vs_eco": {
                "cost": round(eco_cost - balanced_cost, 2),
                "fuel_liters": round(routes["eco_friendly"]["fuel_analysis"]["fuel_consumption_liters"] - 3.1, 1),
                "percentage": f"{round(((eco_cost - balanced_cost) / eco_cost) * 100, 1)}%" if eco_cost > 0 else "0%"
            },
            "savings_vs_balanced": {"cost": 0, "fuel_liters": 0, "percentage": "0%"}
        }
    }
    
    # Generate fuel-focused optimization suggestions
    fastest_vs_eco_savings = round(fastest_cost - eco_cost, 2)
    fastest_vs_balanced_savings = round(fastest_cost - balanced_cost, 2)
    
    suggestions = [
        {
            "title": "🌱 Choose Eco-Friendly Route for Maximum Fuel Savings",
            "message": f"Eco-friendly route saves ₹{fastest_vs_eco_savings} in fuel costs compared to fastest route",
            "impact": "high",
            "savings_minutes": -20,  # 20 minutes extra
            "fuel_savings_inr": fastest_vs_eco_savings,
            "fuel_savings_liters": round(3.6 - 2.7, 1),
            "co2_savings_kg": round(8.4 - 6.2, 1),
            "route_color": "#006400",
            "details": f"Save {round(3.6 - 2.7, 1)}L fuel • {round(((fastest_vs_eco_savings/fastest_cost)*100), 1)}% cost reduction"
        },
        {
            "title": "⚖️ Balanced Route for Optimal Cost-Time Trade-off", 
            "message": f"Balanced route saves ₹{fastest_vs_balanced_savings} with only 7 minutes extra time",
            "impact": "medium",
            "savings_minutes": -7,   # 7 minutes extra
            "fuel_savings_inr": fastest_vs_balanced_savings,
            "fuel_savings_liters": round(3.6 - 3.1, 1),
            "co2_savings_kg": round(8.4 - 7.1, 1),
            "route_color": "#000080",
            "details": f"Save {round(3.6 - 3.1, 1)}L fuel • Best time-cost balance"
        },
        {
            "title": "🚀 Fastest Route - Premium Speed Choice",
            "message": f"Fastest route costs ₹{round(fastest_cost - eco_cost, 2)} extra but saves 20 minutes",
            "impact": "low",
            "savings_minutes": 20,   # 20 minutes saved
            "fuel_cost_extra": round(fastest_cost - eco_cost, 2),
            "fuel_extra_liters": round(3.6 - 2.7, 1),
            "route_color": "#FF6B00", 
            "details": f"Extra {round(3.6 - 2.7, 1)}L fuel • Premium for time-sensitive travel"
        },
        {
            "title": "⏰ Optimal Departure Times for All Routes",
            "message": "Depart during off-peak hours to improve fuel efficiency by 10-15%",
            "impact": "medium",
            "recommended_times": ["9:30 AM", "1:30 PM", "7:00 PM"],
            "potential_savings_inr": "₹15-25",
            "details": "Avoid 8-10 AM and 5-7 PM for better fuel economy"
        }
    ]
    
    processing_time = round((time.time() - processing_start) * 1000, 1)
    
    # Comprehensive fuel cost summary
    fuel_cost_summary = {
        "fuel_price_per_liter_inr": FUEL_PRICE_PER_LITER,
        "routes_fuel_analysis": {
            "fastest_route": {
                "color": "#FF6B00",
                "fuel_liters": 3.6,
                "fuel_cost_inr": fastest_cost,
                "efficiency_kmpl": routes["fastest"]["fuel_analysis"]["fuel_efficiency_kmpl"],
                "cost_per_km_inr": routes["fastest"]["fuel_analysis"]["cost_per_km"]
            },
            "eco_friendly_route": {
                "color": "#006400", 
                "fuel_liters": 2.7,
                "fuel_cost_inr": eco_cost,
                "efficiency_kmpl": routes["eco_friendly"]["fuel_analysis"]["fuel_efficiency_kmpl"],
                "cost_per_km_inr": routes["eco_friendly"]["fuel_analysis"]["cost_per_km"]
            },
            "balanced_route": {
                "color": "#000080",
                "fuel_liters": 3.1,
                "fuel_cost_inr": balanced_cost,
                "efficiency_kmpl": routes["balanced"]["fuel_analysis"]["fuel_efficiency_kmpl"],
                "cost_per_km_inr": routes["balanced"]["fuel_analysis"]["cost_per_km"]
            }
        },
        "savings_comparison": {
            "eco_vs_fastest": {
                "fuel_saved_liters": round(3.6 - 2.7, 1),
                "cost_saved_inr": round(fastest_cost - eco_cost, 2),
                "percentage_saved": f"{round(((fastest_cost - eco_cost) / fastest_cost) * 100, 1)}%"
            },
            "balanced_vs_fastest": {
                "fuel_saved_liters": round(3.6 - 3.1, 1), 
                "cost_saved_inr": round(fastest_cost - balanced_cost, 2),
                "percentage_saved": f"{round(((fastest_cost - balanced_cost) / fastest_cost) * 100, 1)}%"
            },
            "balanced_vs_eco": {
                "fuel_extra_liters": round(3.1 - 2.7, 1),
                "cost_extra_inr": round(balanced_cost - eco_cost, 2),
                "percentage_extra": f"{round(((balanced_cost - eco_cost) / eco_cost) * 100, 1)}%"
            }
        },
        "recommendations": {
            "most_fuel_efficient": "eco_friendly",
            "best_value": "balanced", 
            "fastest_option": "fastest",
            "monthly_savings_potential_inr": round((fastest_cost - eco_cost) * 20, 2)  # 20 trips per month
        }
    }
    
    return {
        "request_id": request_id,
        "processing_time_ms": processing_time,
        "routes": routes,
        "route_comparison": route_comparison,
        "fuel_cost_summary": fuel_cost_summary,
        "optimization_suggestions": suggestions,
        "metadata": {
            "origin": request.origin,
            "destination": request.destination,
            "travel_mode": request.travel_mode,
            "timestamp": time.time(),
            "fuel_price_source": "Current Indian market rates (₹110/L)"
        }
    }

# Simple route calculation endpoint
@app.post("/api/v1/routes/calculate")
async def calculate_route(request: RouteRequest):
    """Basic route calculation endpoint"""
    
    await asyncio.sleep(0.1)  # Simulate processing
    
    return {
        "request_id": str(uuid.uuid4())[:8],
        "route": {
            "distance": {"value": 42000, "text": "42.0 km"},
            "duration": {"value": 4800, "text": "1 hour 20 mins"},
            "summary": f"Route from {request.origin} to {request.destination}",
        },
        "status": "success"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Google Maps Test Backend API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "three_strategies": "/api/v1/routes/three-strategies",
            "basic_route": "/api/v1/routes/calculate",
            "documentation": "/docs"
        },
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Google Maps Test Backend...")
    print("📍 Server will be available at: http://127.0.0.1:8001")
    print("📚 API Documentation: http://127.0.0.1:8001/docs")
    
    uvicorn.run(
        "simple_server:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )