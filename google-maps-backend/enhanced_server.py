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

# Three-route strategies endpoint
@app.post("/api/v1/routes/three-strategies")
async def get_three_route_strategies(request: ThreeStrategiesRequest):
    """Generate three different route strategies with vehicle-specific optimization suggestions"""
    
    # Simulate processing time
    await asyncio.sleep(0.2)
    
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
    
    # Calculate fuel/energy for each route type with different efficiency factors
    fastest_calc = calculate_fuel_cost_and_consumption(45.2, 0.85, vehicle_type)    # Highway: 85% efficiency due to high speed
    eco_calc = calculate_fuel_cost_and_consumption(52.1, 1.15, vehicle_type)        # Eco-driving: 115% efficiency  
    balanced_calc = calculate_fuel_cost_and_consumption(48.7, 1.0, vehicle_type)    # Normal: 100% base efficiency
    
    # Generate three distinct routes with vehicle-specific calculations
    routes = {
        "fastest": {
            "type": "fastest",
            "color": "#FF6B00",  # Dark Orange
            "total_distance": {"value": 45200, "text": "45.2 km"},
            "total_duration": {"value": 5100, "text": "1 hour 25 mins"},
            "summary": f"Via highways from {origin_info} to {dest_info}",
            "vehicle_type": vehicle_type,
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
            "total_distance": {"value": 52100, "text": "52.1 km"},
            "total_duration": {"value": 6300, "text": "1 hour 45 mins"},
            "summary": f"Via eco-routes from {origin_info} to {dest_info}",
            "vehicle_type": vehicle_type,
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
            "total_distance": {"value": 48700, "text": "48.7 km"},
            "total_duration": {"value": 5520, "text": "1 hour 32 mins"},
            "summary": f"Optimized balance from {origin_info} to {dest_info}",
            "vehicle_type": vehicle_type,
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
    
    # Route comparison summary with vehicle-specific analysis
    route_comparison = {
        "fastest": {
            "distance_km": 45.2,
            "duration_minutes": 85,
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
            "distance_km": 52.1,
            "duration_minutes": 105, 
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
            "distance_km": 48.7,
            "duration_minutes": 92,
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
    
    return {
        "request_id": request_id,
        "processing_time_ms": processing_time,
        "routes": [routes["fastest"], routes["eco_friendly"], routes["balanced"]],
        "route_comparison": route_comparison,
        "fuel_cost_summary": fuel_cost_summary,
        "optimization_suggestions": suggestions,
        "metadata": {
            "origin": request.origin,
            "destination": request.destination,
            "travel_mode": request.travel_mode,
            "vehicle_type": vehicle_type,
            "vehicle_display": vehicle_data["display_name"],
            "timestamp": time.time(),
            "pricing_source": f"Current Indian market rates for {vehicle_data['display_name']}"
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