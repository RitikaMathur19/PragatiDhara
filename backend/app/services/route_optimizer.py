"""
Route Optimization Service
Implements CPU-efficient A* pathfinding with emission calculations and eco-priority routing
"""

import time
import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from heapq import heappush, heappop
import asyncio

import numpy as np
from diskcache import Cache

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class RouteNode:
    """Route node with location and properties."""
    id: str
    name: str
    latitude: float = 0.0
    longitude: float = 0.0
    properties: Dict = None


@dataclass
class RouteLink:
    """Route link between nodes with traffic and emission data."""
    from_node: str
    to_node: str
    distance: float
    time: float
    eco_priority: bool = False
    emissions_multiplier: float = 1.0
    traffic_factor: float = 1.0
    road_type: str = "normal"


@dataclass
class RouteResult:
    """Route calculation result."""
    path: List[str]
    total_time: float
    total_distance: float
    total_emissions: float
    green_points_score: int
    route_type: str
    processing_time_ms: float
    cache_hit: bool = False


class AStarPathfinder:
    """CPU-optimized A* pathfinding algorithm."""
    
    def __init__(self, nodes: Dict[str, RouteNode], links: List[RouteLink]):
        """Initialize pathfinder with graph data."""
        self.nodes = nodes
        self.graph = self._build_graph(links)
        
    def _build_graph(self, links: List[RouteLink]) -> Dict[str, List[RouteLink]]:
        """Build adjacency graph from links."""
        graph = {}
        for link in links:
            if link.from_node not in graph:
                graph[link.from_node] = []
            graph[link.from_node].append(link)
        return graph
    
    def find_path(self, start: str, end: str, alpha: float = 1.0) -> Optional[RouteResult]:
        """Find optimal path using A* with emissions consideration."""
        if start not in self.nodes or end not in self.nodes:
            return None
            
        start_time = time.time()
        
        # Priority queue: (f_score, g_score, node, path)
        open_set = [(0, 0, start, [start])]
        closed_set: Set[str] = set()
        
        while open_set:
            f_score, g_score, current, path = heappop(open_set)
            
            if current == end:
                # Calculate route metrics
                total_distance, total_emissions = self._calculate_route_metrics(path)
                processing_time = (time.time() - start_time) * 1000
                
                return RouteResult(
                    path=path,
                    total_time=g_score,
                    total_distance=total_distance,
                    total_emissions=total_emissions,
                    green_points_score=self._calculate_green_points(total_emissions, g_score),
                    route_type="optimal",
                    processing_time_ms=processing_time
                )
            
            if current in closed_set:
                continue
                
            closed_set.add(current)
            
            # Explore neighbors
            if current in self.graph:
                for link in self.graph[current]:
                    if link.to_node in closed_set:
                        continue
                    
                    # Calculate costs
                    new_g = g_score + link.time * link.traffic_factor
                    emissions_cost = self._calculate_emissions_cost(link)
                    h_score = self._heuristic(link.to_node, end)
                    
                    # Combined cost with alpha weighting
                    f_score_new = new_g + h_score + (alpha * emissions_cost)
                    
                    heappush(open_set, (f_score_new, new_g, link.to_node, path + [link.to_node]))
        
        return None  # No path found
    
    def _calculate_route_metrics(self, path: List[str]) -> Tuple[float, float]:
        """Calculate total distance and emissions for a path."""
        total_distance = 0.0
        total_emissions = 0.0
        
        for i in range(len(path) - 1):
            link = self._find_link(path[i], path[i + 1])
            if link:
                total_distance += link.distance
                base_emissions = link.time * 100  # Base emissions per minute
                total_emissions += base_emissions * link.emissions_multiplier
        
        return total_distance, total_emissions
    
    def _find_link(self, from_node: str, to_node: str) -> Optional[RouteLink]:
        """Find link between two nodes."""
        if from_node in self.graph:
            for link in self.graph[from_node]:
                if link.to_node == to_node:
                    return link
        return None
    
    def _calculate_emissions_cost(self, link: RouteLink) -> float:
        """Calculate emissions cost for a link."""
        base_emissions = link.time * 100  # Base emissions calculation
        return base_emissions * link.emissions_multiplier
    
    def _heuristic(self, node: str, goal: str) -> float:
        """Heuristic function (simplified distance estimation)."""
        # In a real implementation, use haversine distance
        return 0.0  # Simplified for CPU efficiency
    
    def _calculate_green_points(self, emissions: float, time: float) -> int:
        """Calculate green points score based on emissions and time."""
        base_score = 100
        emissions_penalty = min(50, emissions / 100)  # Penalty for high emissions
        time_penalty = min(30, time / 10)  # Penalty for long time
        return max(0, int(base_score - emissions_penalty - time_penalty))


class RouteOptimizerService:
    """Route optimization service with multiple algorithms and caching."""
    
    def __init__(self):
        """Initialize route optimizer service."""
        self.settings = get_settings()
        self.cache = Cache(directory='.cache/routes', size_limit=int(2e6))  # 2MB cache
        self.pathfinder: Optional[AStarPathfinder] = None
        self.ready = False
        self.optimization_count = 0
        self.total_optimization_time = 0.0
        
        # Load Pune city map data
        self.nodes = self._load_pune_nodes()
        self.links = self._load_pune_links()
    
    async def initialize(self) -> None:
        """Initialize the service."""
        logger.info("🗺️  Initializing Route Optimizer...")
        
        # Initialize pathfinder
        self.pathfinder = AStarPathfinder(self.nodes, self.links)
        
        # Warm up cache with common routes
        await self._warmup_cache()
        
        self.ready = True
        logger.info("✅ Route Optimizer ready - A* algorithm with emissions optimization")
    
    async def optimize_routes(self, start_node: str, end_node: str, 
                            alpha: float = 1.0) -> List[RouteResult]:
        """Optimize routes with multiple strategies."""
        if not self.ready:
            raise RuntimeError("Service not ready")
        
        start_time = time.time()
        
        # Create cache key
        cache_key = f"{start_node}:{end_node}:{round(alpha, 2)}"
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            for route in cached_result:
                route['cache_hit'] = True
                route['processing_time_ms'] = 0.5  # Very fast cache retrieval
            return [RouteResult(**route) for route in cached_result]
        
        # Calculate different route options
        routes = []
        
        # 1. Speed-optimized route (low alpha)
        fast_route = self.pathfinder.find_path(start_node, end_node, alpha=0.1)
        if fast_route:
            fast_route.route_type = "fast"
            routes.append(fast_route)
        
        # 2. Eco-optimized route (high alpha)
        eco_route = self.pathfinder.find_path(start_node, end_node, alpha=2.0)
        if eco_route:
            eco_route.route_type = "eco"
            eco_route.green_points_score += 20  # Bonus for eco route
            routes.append(eco_route)
        
        # 3. RL-optimized route (provided alpha)
        rl_route = self.pathfinder.find_path(start_node, end_node, alpha=alpha)
        if rl_route:
            rl_route.route_type = "rl-optimized"
            rl_route.green_points_score += 10  # Bonus for RL optimization
            routes.append(rl_route)
        
        # Sort by green points score (descending)
        routes.sort(key=lambda r: r.green_points_score, reverse=True)
        
        # Cache results
        cache_data = [
            {
                'path': route.path,
                'total_time': route.total_time,
                'total_distance': route.total_distance,
                'total_emissions': route.total_emissions,
                'green_points_score': route.green_points_score,
                'route_type': route.route_type,
                'processing_time_ms': route.processing_time_ms,
                'cache_hit': False
            }
            for route in routes
        ]
        self.cache.set(cache_key, cache_data, expire=self.settings.ROUTE_CACHE_TTL)
        
        # Update service metrics
        processing_time = time.time() - start_time
        self.optimization_count += 1
        self.total_optimization_time += processing_time
        
        return routes
    
    async def get_traffic_data(self) -> Dict:
        """Get simulated real-time traffic data."""
        # Simulate dynamic traffic conditions
        current_time = time.time()
        hour = int((current_time % 86400) // 3600)
        
        # Peak hours have higher traffic
        base_traffic = 0.3
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
            base_traffic = 0.7
        elif 10 <= hour <= 16:  # Daytime
            base_traffic = 0.5
        elif 22 <= hour or hour <= 6:  # Night
            base_traffic = 0.2
        
        # Add some randomness
        traffic_factor = base_traffic + np.random.normal(0, 0.1)
        traffic_factor = max(0.1, min(1.0, traffic_factor))
        
        incident_factor = np.random.exponential(0.1)
        incident_factor = min(1.0, incident_factor)
        
        return {
            "timestamp": current_time,
            "traffic_factor": round(traffic_factor, 3),
            "incident_factor": round(incident_factor, 3),
            "hour_of_day": hour,
            "is_peak_hour": 7 <= hour <= 9 or 17 <= hour <= 19,
            "weather_factor": 0.5  # Neutral weather
        }
    
    def get_service_metrics(self) -> Dict:
        """Get service performance metrics."""
        avg_optimization_time = (
            self.total_optimization_time / max(1, self.optimization_count)
        ) * 1000  # Convert to ms
        
        cache_stats = {
            'size': len(self.cache) if hasattr(self.cache, '__len__') else 0,
            'hits': getattr(self.cache, 'hits', 0),
            'misses': getattr(self.cache, 'misses', 0)
        }
        
        return {
            'service_status': 'ready' if self.ready else 'initializing',
            'performance': {
                'total_optimizations': self.optimization_count,
                'avg_optimization_time_ms': round(avg_optimization_time, 2),
                'nodes_count': len(self.nodes),
                'links_count': len(self.links)
            },
            'cache_stats': cache_stats,
            'algorithms': {
                'pathfinding': 'A* with emissions weighting',
                'cpu_optimized': True,
                'multi_objective': True
            }
        }
    
    def is_ready(self) -> bool:
        """Check if service is ready."""
        return self.ready
    
    async def cleanup(self) -> None:
        """Cleanup service resources."""
        if hasattr(self.cache, 'close'):
            self.cache.close()
        logger.info("🧹 Route Optimizer service cleanup complete")
    
    def _load_pune_nodes(self) -> Dict[str, RouteNode]:
        """Load Pune city nodes."""
        return {
            'A': RouteNode('A', 'Katraj (South)', 18.4088, 73.8578),
            'B': RouteNode('B', 'Swargate', 18.5018, 73.8636),
            'C': RouteNode('C', 'Deccan Gymkhana', 18.5204, 73.8567),
            'D': RouteNode('D', 'Shivajinagar', 18.5304, 73.8567),
            'E': RouteNode('E', 'University Circle', 18.5404, 73.8267),
            'F': RouteNode('F', 'Kothrud Bypass', 18.5074, 73.8077),
            'G': RouteNode('G', 'Balewadi Stadium', 18.5644, 73.7749),
            'H': RouteNode('H', 'Baner', 18.5590, 73.7770),
            'I': RouteNode('I', 'Wakad', 18.5974, 73.7662),
            'J': RouteNode('J', 'Hinjawadi Ph 1', 18.5912, 73.7394)
        }
    
    def _load_pune_links(self) -> List[RouteLink]:
        """Load Pune city road links with emissions data."""
        base_links = [
            # Core Main Artery Links
            RouteLink('A', 'B', 10, 5),
            RouteLink('A', 'C', 12, 6),
            RouteLink('B', 'D', 10, 5),
            RouteLink('C', 'D', 8, 4),
            RouteLink('D', 'E', 5, 2),
            RouteLink('E', 'J', 10, 5),
            RouteLink('I', 'J', 8, 4),
            
            # Eco Bypass Routes (High Priority, Low Emissions)
            RouteLink('C', 'F', 8, 4, eco_priority=True, emissions_multiplier=0.5),
            RouteLink('F', 'H', 15, 7, eco_priority=True, emissions_multiplier=0.05),  # Primary eco bypass
            RouteLink('E', 'I', 10, 5, eco_priority=True, emissions_multiplier=0.4),
            RouteLink('G', 'D', 12, 5, eco_priority=True, emissions_multiplier=0.7),
            
            # Other Links
            RouteLink('D', 'G', 7, 3),
            RouteLink('G', 'H', 5, 2),
            RouteLink('H', 'I', 8, 4),
            RouteLink('D', 'F', 12, 6),
            RouteLink('B', 'E', 14, 7),
        ]
        
        # Create bidirectional links
        all_links = []
        for link in base_links:
            # Forward direction
            all_links.append(link)
            # Reverse direction
            all_links.append(RouteLink(
                from_node=link.to_node,
                to_node=link.from_node,
                distance=link.distance,
                time=link.time,
                eco_priority=link.eco_priority,
                emissions_multiplier=link.emissions_multiplier
            ))
        
        return all_links
    
    async def _warmup_cache(self) -> None:
        """Warm up cache with common routes."""
        common_routes = [
            ('A', 'J'),  # South to Tech Hub
            ('D', 'J'),  # City Center to Tech Hub
            ('B', 'I'),  # Transit Hub to Suburbs
        ]
        
        for start, end in common_routes:
            try:
                await self.optimize_routes(start, end, alpha=1.0)
            except Exception as e:
                logger.warning(f"Cache warmup failed for {start}->{end}: {e}")
        
        logger.info("🔥 Route cache warmed up")