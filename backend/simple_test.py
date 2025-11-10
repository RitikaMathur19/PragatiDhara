#!/usr/bin/env python3
"""
Simple test to verify our route optimization generates 3 distinct paths
"""
import subprocess
import sys
import time

def test_with_curl_alternative():
    """Test using Python's urllib instead of external curl"""
    import urllib.request
    import urllib.parse
    import json
    
    # Test data
    url = "http://127.0.0.1:8000/optimize-route"
    data = {
        "start_node": "A",
        "end_node": "J", 
        "preferences": {"alpha": 0.5}
    }
    
    # Convert to JSON and encode
    json_data = json.dumps(data).encode('utf-8')
    
    # Create request
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    req.data = json_data
    
    try:
        print("🚀 Testing route optimization API...")
        print(f"📍 Route: A → J")
        print("="*60)
        
        # Make request
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        
        print("✅ API Response received!")
        
        if 'routes' in result:
            routes = result['routes']
            print(f"\n📊 Generated {len(routes)} routes:")
            
            paths = []
            for i, route in enumerate(routes):
                route_type = route.get('type', f'Route {i+1}')
                path = route.get('path', [])
                distance = route.get('distance', 'N/A')
                time_val = route.get('time', 'N/A')
                green_points = route.get('green_points', 'N/A')
                
                paths.append(path)
                
                print(f"\n🛣️  {route_type.upper()}:")
                print(f"   Path: {' → '.join(path) if path else 'No path'}")
                print(f"   Distance: {distance}")
                print(f"   Time: {time_val}")
                print(f"   Green Points: {green_points}")
            
            # Check for path diversity
            print("\n" + "="*60)
            print("🔍 PATH DIVERSITY ANALYSIS:")
            
            unique_paths = []
            for path in paths:
                if path not in unique_paths:
                    unique_paths.append(path)
            
            print(f"   Total routes: {len(paths)}")
            print(f"   Unique paths: {len(unique_paths)}")
            
            if len(unique_paths) == len(paths) and len(paths) >= 3:
                print("🎉 SUCCESS: All routes have distinct paths!")
                print("✅ Problem FIXED: No more identical A→B→D→G→H→I→J for all routes")
            elif len(unique_paths) < len(paths):
                print("❌ ISSUE: Some routes still have identical paths")
                for i, path in enumerate(paths):
                    print(f"   Route {i+1}: {' → '.join(path) if path else 'Empty'}")
            else:
                print("⚠️  Routes generated but need to verify count")
                
        else:
            print("❌ No routes found in response")
            print(f"Response keys: {list(result.keys())}")
            
    except urllib.error.URLError as e:
        print(f"❌ Connection Error: {e}")
        print("🔧 Make sure backend server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_with_curl_alternative()