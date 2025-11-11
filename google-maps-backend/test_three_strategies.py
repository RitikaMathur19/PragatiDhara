#!/usr/bin/env python3
"""
Test script for Google Maps Three-Route Strategy System
Demonstrates the API usage and route comparison features
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8001/api/v1"
TEST_ROUTES = [
    {
        "name": "Pune Tech Route",
        "origin": {"address": "Katraj, Pune, Maharashtra"},
        "destination": {"address": "Hinjewadi Phase 1, Pune, Maharashtra"}
    },
    {
        "name": "Delhi NCR Route", 
        "origin": {"coordinates": {"lat": 28.6139, "lng": 77.2090}},  # India Gate
        "destination": {"coordinates": {"lat": 28.4595, "lng": 77.0266}}  # Gurgaon
    },
    {
        "name": "Mumbai Suburban",
        "origin": {"address": "Andheri East, Mumbai"},
        "destination": {"address": "Bandra Kurla Complex, Mumbai"}
    }
]


async def test_three_route_strategies(session: aiohttp.ClientSession, route_config: Dict[str, Any]):
    """Test the three-route strategy API endpoint"""
    
    print(f"\n🚀 Testing Route: {route_config['name']}")
    print(f"   From: {route_config['origin']}")
    print(f"   To: {route_config['destination']}")
    print("-" * 60)
    
    try:
        # Prepare API request
        payload = {
            "origin": route_config["origin"],
            "destination": route_config["destination"],
            "travel_mode": "driving",
            "departure_time": datetime.now().isoformat()
        }
        
        # Make API request
        async with session.post(
            f"{API_BASE_URL}/routes/three-strategies",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            
            if response.status == 200:
                data = await response.json()
                display_route_results(data)
            else:
                error_text = await response.text()
                print(f"❌ API Error ({response.status}): {error_text}")
                
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")


def display_route_results(data: Dict[str, Any]):
    """Display the three-route strategy results in a formatted manner"""
    
    print(f"✅ Request ID: {data.get('request_id', 'N/A')}")
    print(f"⏱️  Processing Time: {data.get('processing_time_ms', 0)}ms")
    print()
    
    routes = data.get('routes', {})
    comparison = data.get('route_comparison', {})
    
    # Route Summary Table
    print("📊 ROUTE COMPARISON SUMMARY")
    print("=" * 80)
    print(f"{'Strategy':<15} {'Distance':<12} {'Duration':<12} {'CO2 (kg)':<10} {'Eco Score':<10}")
    print("-" * 80)
    
    strategies = ['fastest', 'eco_friendly', 'balanced']
    strategy_icons = {'fastest': '🚀', 'eco_friendly': '🌱', 'balanced': '⚖️'}
    
    for strategy in strategies:
        if strategy in comparison:
            comp = comparison[strategy]
            icon = strategy_icons.get(strategy, '📍')
            print(f"{icon} {strategy.replace('_', ' ').title():<12} "
                  f"{comp['distance_km']} km{'':<6} "
                  f"{comp['duration_minutes']:.0f} mins{'':<6} "
                  f"{comp['co2_emissions_kg']:<10.1f} "
                  f"{comp['eco_score']:<10.1f}")
    
    print("-" * 80)
    
    # Detailed Route Information
    print("\n📋 DETAILED ROUTE INFORMATION")
    print("=" * 50)
    
    for strategy in strategies:
        if strategy in routes:
            route = routes[strategy]
            icon = strategy_icons.get(strategy, '📍')
            
            print(f"\n{icon} {strategy.replace('_', ' ').upper()} ROUTE")
            print(f"   Distance: {route['total_distance']['text']}")
            print(f"   Duration: {route['total_duration']['text']}")
            print(f"   Summary: {route.get('summary', 'N/A')}")
            
            if route.get('emissions'):
                emissions = route['emissions']
                print(f"   CO2 Emissions: {emissions['co2_emissions_kg']} kg")
                print(f"   Eco Score: {emissions['eco_score']}/10")
                
                if emissions.get('fuel_consumption_liters'):
                    print(f"   Fuel Consumption: {emissions['fuel_consumption_liters']:.1f} liters")
            
            # Strategy-specific information
            if route.get('strategy_info'):
                strategy_info = route['strategy_info']
                print(f"   Strategy Focus: {strategy_info.get('strategy_metadata', {}).get('strategy_focus', 'N/A')}")
                
                optimization_factors = strategy_info.get('strategy_metadata', {}).get('optimization_factors', [])
                if optimization_factors:
                    print(f"   Optimization Factors: {', '.join(optimization_factors)}")
    
    # Optimization Suggestions
    suggestions = data.get('optimization_suggestions', [])
    if suggestions:
        print(f"\n💡 OPTIMIZATION SUGGESTIONS")
        print("=" * 50)
        
        for i, suggestion in enumerate(suggestions, 1):
            impact_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(suggestion.get('impact', 'low'), '🔵')
            print(f"{i}. {impact_icon} {suggestion['message']}")
            
            if suggestion.get('savings_minutes'):
                print(f"   ⏱️  Time Savings: {suggestion['savings_minutes']} minutes")
            
            if suggestion.get('co2_savings_kg'):
                print(f"   🌱 CO2 Reduction: {suggestion['co2_savings_kg']:.1f} kg")
            
            if suggestion.get('recommended_times'):
                print(f"   🕐 Best Times: {', '.join(suggestion['recommended_times'])}")
    
    print("\n" + "=" * 80)


async def test_api_health(session: aiohttp.ClientSession):
    """Test API health and connectivity"""
    
    print("🏥 Testing API Health...")
    
    try:
        async with session.get(f"{API_BASE_URL.replace('/api/v1', '')}/health") as response:
            if response.status == 200:
                health_data = await response.json()
                print(f"✅ API Status: {health_data.get('status', 'unknown')}")
                print(f"📄 API Version: {health_data.get('version', 'N/A')}")
                return True
            else:
                print(f"❌ Health Check Failed: {response.status}")
                return False
                
    except Exception as e:
        print(f"❌ Cannot connect to API: {str(e)}")
        print(f"💡 Make sure the server is running on {API_BASE_URL}")
        return False


async def main():
    """Main test function"""
    
    print("🌐 Google Maps Three-Route Strategy Test")
    print("=" * 60)
    
    # Create HTTP session
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        
        # Test API connectivity
        if not await test_api_health(session):
            print("\n💡 Setup Instructions:")
            print("1. Navigate to google-maps-backend directory")
            print("2. Configure .env file with Google Maps API key")
            print("3. Run: uvicorn app.main:app --reload --port 8001")
            return
        
        print("\n🧪 Running Route Strategy Tests...")
        
        # Test each route configuration
        for route_config in TEST_ROUTES:
            await test_three_route_strategies(session, route_config)
            await asyncio.sleep(1)  # Rate limiting
        
        print("\n🎉 All tests completed!")
        print("\n📚 API Documentation available at: http://localhost:8001/docs")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")