"""
Google Maps Platform integration service
Core service for interacting with Google Maps APIs
"""

import googlemaps
import asyncio
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor
import json

from ..config import get_settings
from ..models.route_models import (
    Location, LocationInput, RouteRequest, Route, RouteLeg, RouteStep,
    EmissionsData, TravelMode, OptimizationMode, TrafficModel
)

logger = logging.getLogger(__name__)
settings = get_settings()


class GoogleMapsService:
    """Core Google Maps Platform service"""
    
    def __init__(self):
        """Initialize Google Maps client"""
        self.client = googlemaps.Client(key=settings.google_maps_api_key)
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Request tracking for rate limiting
        self.request_count = 0
        self.daily_requests = 0
        self.last_request_time = time.time()
        self.request_times = []
        
    async def _execute_sync_operation(self, func, *args, **kwargs) -> Any:
        """Execute synchronous Google Maps operation asynchronously"""
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                self.executor, 
                lambda: func(*args, **kwargs)
            )
            self._track_request()
            return result
        except Exception as e:
            logger.error(f"Google Maps API error: {str(e)}")
            raise
    
    def _track_request(self):
        """Track API requests for rate limiting"""
        current_time = time.time()
        self.request_count += 1
        self.daily_requests += 1
        self.request_times.append(current_time)
        
        # Remove requests older than 1 minute
        minute_ago = current_time - 60
        self.request_times = [t for t in self.request_times if t > minute_ago]
        
        # Check rate limits
        if len(self.request_times) > settings.rate_limit_per_minute:
            logger.warning(f"Rate limit approached: {len(self.request_times)} requests in last minute")
        
        if self.daily_requests > settings.daily_quota_limit:
            logger.error(f"Daily quota exceeded: {self.daily_requests} requests")
    
    def _resolve_location_input(self, location: LocationInput) -> Union[str, Tuple[float, float], str]:
        """Resolve location input to format expected by Google Maps API"""
        if location.coordinates:
            return (location.coordinates.lat, location.coordinates.lng)
        elif location.place_id:
            return f"place_id:{location.place_id}"
        elif location.address:
            return location.address
        else:
            raise ValueError("Invalid location input: no address, coordinates, or place_id provided")
    
    async def geocode_address(self, address: str, region: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Geocode an address to coordinates
        
        Args:
            address: Address string to geocode
            region: Region bias for geocoding
            
        Returns:
            List of geocoding results
        """
        try:
            result = await self._execute_sync_operation(
                self.client.geocode,
                address,
                region=region or settings.geocoding_region
            )
            
            logger.info(f"Geocoded address '{address}': {len(result)} results")
            return result
            
        except Exception as e:
            logger.error(f"Geocoding failed for '{address}': {str(e)}")
            raise
    
    async def reverse_geocode(self, lat: float, lng: float) -> List[Dict[str, Any]]:
        """
        Reverse geocode coordinates to address
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            List of reverse geocoding results
        """
        try:
            result = await self._execute_sync_operation(
                self.client.reverse_geocode,
                (lat, lng)
            )
            
            logger.info(f"Reverse geocoded ({lat}, {lng}): {len(result)} results")
            return result
            
        except Exception as e:
            logger.error(f"Reverse geocoding failed for ({lat}, {lng}): {str(e)}")
            raise
    
    async def calculate_directions(self, request: RouteRequest) -> Dict[str, Any]:
        """
        Calculate directions using Google Maps Directions API
        
        Args:
            request: Route calculation request
            
        Returns:
            Directions API response
        """
        try:
            # Resolve locations
            origin = self._resolve_location_input(request.origin)
            destination = self._resolve_location_input(request.destination)
            
            # Prepare waypoints
            waypoints = []
            if request.waypoints:
                for waypoint in request.waypoints:
                    wp_location = self._resolve_location_input(waypoint.location)
                    waypoints.append(wp_location)
            
            # Prepare request parameters
            params = {
                'origin': origin,
                'destination': destination,
                'mode': request.travel_mode.value,
                'alternatives': request.alternatives,
                'avoid': self._build_avoid_list(request),
                'language': request.language,
                'region': request.region,
                'units': request.units.value
            }
            
            # Add waypoints if present
            if waypoints:
                params['waypoints'] = waypoints
                params['optimize_waypoints'] = request.optimization_mode in [
                    OptimizationMode.FASTEST, OptimizationMode.SHORTEST
                ]
            
            # Add traffic model for driving mode
            if request.travel_mode == TravelMode.DRIVING:
                if request.departure_time:
                    params['departure_time'] = request.departure_time
                elif request.arrival_time:
                    params['arrival_time'] = request.arrival_time
                else:
                    params['departure_time'] = datetime.now()
                
                if settings.enable_traffic_model:
                    params['traffic_model'] = request.traffic_model.value
            
            # Execute directions request
            result = await self._execute_sync_operation(
                self.client.directions,
                **params
            )
            
            logger.info(f"Calculated directions: {len(result)} route(s) found")
            return result
            
        except Exception as e:
            logger.error(f"Directions calculation failed: {str(e)}")
            raise
    
    def _build_avoid_list(self, request: RouteRequest) -> List[str]:
        """Build avoid list for directions API"""
        avoid = []
        if request.avoid_highways:
            avoid.append('highways')
        if request.avoid_tolls:
            avoid.append('tolls')
        if request.avoid_ferries:
            avoid.append('ferries')
        return avoid
    
    async def calculate_distance_matrix(
        self,
        origins: List[LocationInput],
        destinations: List[LocationInput],
        mode: TravelMode = TravelMode.DRIVING,
        traffic_model: Optional[TrafficModel] = None,
        departure_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate distance matrix between multiple origins and destinations
        
        Args:
            origins: List of origin locations
            destinations: List of destination locations
            mode: Travel mode
            traffic_model: Traffic model for predictions
            departure_time: Departure time for traffic-aware calculations
            
        Returns:
            Distance Matrix API response
        """
        try:
            # Resolve locations
            origin_locations = [self._resolve_location_input(loc) for loc in origins]
            dest_locations = [self._resolve_location_input(loc) for loc in destinations]
            
            # Check matrix size limits
            if len(origin_locations) * len(dest_locations) > settings.max_matrix_elements:
                raise ValueError(f"Matrix too large: maximum {settings.max_matrix_elements} elements allowed")
            
            # Prepare parameters
            params = {
                'origins': origin_locations,
                'destinations': dest_locations,
                'mode': mode.value,
                'units': settings.matrix_units,
                'language': settings.maps_language,
                'region': settings.maps_region
            }
            
            # Add traffic parameters for driving mode
            if mode == TravelMode.DRIVING:
                if departure_time:
                    params['departure_time'] = departure_time
                else:
                    params['departure_time'] = datetime.now()
                
                if traffic_model and settings.enable_traffic_model:
                    params['traffic_model'] = traffic_model.value
                    
                # Add avoid parameters
                avoid = []
                if settings.avoid_tolls:
                    avoid.append('tolls')
                if settings.avoid_highways:
                    avoid.append('highways')
                if avoid:
                    params['avoid'] = avoid
            
            # Execute distance matrix request
            result = await self._execute_sync_operation(
                self.client.distance_matrix,
                **params
            )
            
            logger.info(f"Calculated distance matrix: {len(origins)} origins × {len(destinations)} destinations")
            return result
            
        except Exception as e:
            logger.error(f"Distance matrix calculation failed: {str(e)}")
            raise
    
    async def get_place_details(self, place_id: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get detailed information about a place
        
        Args:
            place_id: Google Places ID
            fields: List of fields to retrieve
            
        Returns:
            Place details response
        """
        try:
            default_fields = [
                'place_id', 'name', 'formatted_address', 'geometry',
                'types', 'business_status', 'opening_hours'
            ]
            
            result = await self._execute_sync_operation(
                self.client.place,
                place_id=place_id,
                fields=fields or default_fields,
                language=settings.maps_language,
                region=settings.maps_region
            )
            
            logger.info(f"Retrieved place details for: {place_id}")
            return result
            
        except Exception as e:
            logger.error(f"Place details retrieval failed for {place_id}: {str(e)}")
            raise
    
    async def search_nearby_places(
        self,
        location: Location,
        radius: int = 1000,
        place_type: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for nearby places
        
        Args:
            location: Center location for search
            radius: Search radius in meters
            place_type: Type of place to search for
            keyword: Keyword to search for
            
        Returns:
            Nearby search results
        """
        try:
            params = {
                'location': (location.lat, location.lng),
                'radius': radius,
                'language': settings.maps_language,
                'region': settings.maps_region
            }
            
            if place_type:
                params['type'] = place_type
            if keyword:
                params['keyword'] = keyword
            
            result = await self._execute_sync_operation(
                self.client.places_nearby,
                **params
            )
            
            logger.info(f"Found {len(result.get('results', []))} nearby places")
            return result
            
        except Exception as e:
            logger.error(f"Nearby places search failed: {str(e)}")
            raise
    
    def calculate_emissions(self, route_data: Dict[str, Any], travel_mode: TravelMode) -> EmissionsData:
        """
        Calculate emissions data for a route
        
        Args:
            route_data: Route data from Directions API
            travel_mode: Travel mode used
            
        Returns:
            Emissions calculation results
        """
        try:
            # Extract total distance (in meters)
            total_distance = 0
            for leg in route_data.get('legs', []):
                total_distance += leg['distance']['value']
            
            distance_km = total_distance / 1000
            
            # Calculate based on travel mode
            if travel_mode == TravelMode.DRIVING:
                fuel_liters = distance_km / settings.fuel_efficiency_km_per_liter
                co2_kg = fuel_liters * settings.co2_per_liter_petrol
                energy_kwh = None
            elif travel_mode == TravelMode.BICYCLING or travel_mode == TravelMode.WALKING:
                fuel_liters = None
                co2_kg = 0.0  # Zero emissions
                energy_kwh = None
            elif travel_mode == TravelMode.TRANSIT:
                # Assume average public transport emissions
                co2_kg = distance_km * 0.05  # 50g CO2 per km
                fuel_liters = None
                energy_kwh = None
            else:
                fuel_liters = None
                co2_kg = distance_km * 0.1  # Default estimate
                energy_kwh = None
            
            # Calculate eco score (0-10, higher is better)
            if co2_kg == 0:
                eco_score = 10.0
            elif co2_kg < 1:
                eco_score = 9.0
            elif co2_kg < 3:
                eco_score = 7.0
            elif co2_kg < 5:
                eco_score = 5.0
            elif co2_kg < 10:
                eco_score = 3.0
            else:
                eco_score = 1.0
            
            return EmissionsData(
                co2_emissions_kg=round(co2_kg, 2),
                fuel_consumption_liters=round(fuel_liters, 2) if fuel_liters else None,
                energy_consumption_kwh=round(energy_kwh, 2) if energy_kwh else None,
                eco_score=eco_score,
                comparison_savings={}
            )
            
        except Exception as e:
            logger.error(f"Emissions calculation failed: {str(e)}")
            # Return default emissions data
            return EmissionsData(
                co2_emissions_kg=0.0,
                fuel_consumption_liters=None,
                energy_consumption_kwh=None,
                eco_score=5.0,
                comparison_savings={}
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Google Maps service
        
        Returns:
            Health status information
        """
        try:
            # Simple geocoding test
            start_time = time.time()
            result = await self.geocode_address("New Delhi, India")
            response_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                "status": "healthy",
                "service": "google_maps",
                "response_time_ms": response_time,
                "requests_count": self.request_count,
                "daily_requests": self.daily_requests,
                "rate_limit_remaining": max(0, settings.rate_limit_per_minute - len(self.request_times)),
                "test_result": "OK" if result else "FAILED"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "google_maps",
                "error": str(e),
                "requests_count": self.request_count,
                "daily_requests": self.daily_requests
            }


# Global service instance
_google_maps_service: Optional[GoogleMapsService] = None


def get_google_maps_service() -> GoogleMapsService:
    """Get or create Google Maps service instance"""
    global _google_maps_service
    if _google_maps_service is None:
        _google_maps_service = GoogleMapsService()
    return _google_maps_service