import requests
import json

def test_route_optimization():
    """Test the route optimization API to verify distinct paths are generated"""
    url = "http://127.0.0.1:8000/optimize-route"
    
    payload = {
        "start_node": "A",
        "end_node": "J",
        "preferences": {
            "alpha": 0.5
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("API Response Success!")
            print("="*50)
            
            # Check if we have routes
            if 'routes' in result:
                routes = result['routes']
                print(f"Number of routes generated: {len(routes)}")
                
                for i, route in enumerate(routes):
                    route_type = route.get('type', f'Route {i+1}')
                    path = route.get('path', [])
                    distance = route.get('distance', 'N/A')
                    time = route.get('time', 'N/A') 
                    green_points = route.get('green_points', 'N/A')
                    
                    print(f"\n{route_type.upper()} Route:")
                    print(f"  Path: {' → '.join(path)}")
                    print(f"  Distance: {distance}")
                    print(f"  Time: {time}")
                    print(f"  Green Points: {green_points}")
                
                # Verify path diversity
                paths = [route.get('path', []) for route in routes]
                unique_paths = set(tuple(path) for path in paths)
                
                print(f"\n{'='*50}")
                print(f"Path Diversity Analysis:")
                print(f"Total routes: {len(paths)}")
                print(f"Unique paths: {len(unique_paths)}")
                
                if len(unique_paths) == len(paths):
                    print("✅ SUCCESS: All routes have distinct paths!")
                else:
                    print("❌ ISSUE: Some routes have identical paths")
                    for i, path in enumerate(paths):
                        print(f"  Route {i+1}: {' → '.join(path)}")
            else:
                print("No routes found in response")
                print(f"Full response: {json.dumps(result, indent=2)}")
                
        else:
            print(f"API Error: Status Code {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server not running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_route_optimization()