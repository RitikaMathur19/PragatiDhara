"""
OpenAI Integration Service
Sustainable AI service with CPU optimization and energy-efficient API usage
"""

import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio
import json

import httpx
from openai import AsyncOpenAI
from diskcache import Cache

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class OpenAIRequest:
    """OpenAI API request data."""
    prompt: str
    max_tokens: int = 500
    temperature: float = 0.7
    model: str = "gpt-3.5-turbo"
    system_message: str = ""


@dataclass
class OpenAIResponse:
    """OpenAI API response data."""
    content: str
    tokens_used: int
    processing_time_ms: float
    energy_cost: float
    cache_hit: bool = False
    model_used: str = ""


class SustainableOpenAIService:
    """OpenAI service with energy optimization and intelligent caching."""
    
    def __init__(self):
        """Initialize OpenAI service."""
        self.settings = get_settings()
        self.client: Optional[AsyncOpenAI] = None
        self.cache = Cache(directory='.cache/openai', size_limit=int(5e6))  # 5MB cache
        self.ready = False
        self.request_count = 0
        self.total_tokens_used = 0
        self.total_api_time = 0.0
        
        # Sustainable AI configuration
        self.max_requests_per_minute = 10  # Rate limiting for sustainability
        self.request_timestamps = []
        
    async def initialize(self) -> None:
        """Initialize OpenAI service."""
        if not self.settings.OPENAI_API_KEY:
            logger.warning("🔑 No OpenAI API key provided - service will run in mock mode")
            self.ready = True
            return
        
        logger.info("🤖 Initializing OpenAI service...")
        
        try:
            self.client = AsyncOpenAI(
                api_key=self.settings.OPENAI_API_KEY,
                timeout=30.0,  # Reasonable timeout for energy efficiency
                max_retries=2   # Limited retries to save energy
            )
            
            # Test API connection
            await self._test_connection()
            
            self.ready = True
            logger.info("✅ OpenAI service ready - sustainable mode enabled")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI service: {e}")
            self.ready = False
    
    async def generate_route_insights(self, route_data: Dict) -> OpenAIResponse:
        """Generate sustainable route insights using OpenAI."""
        system_message = """You are a sustainable transportation AI assistant. 
        Provide concise, actionable insights about route optimization focusing on:
        1. Environmental impact
        2. Energy efficiency
        3. Time optimization
        4. Sustainable transportation tips
        Keep responses under 150 words and focus on practical advice."""
        
        prompt = f"""
        Route Analysis:
        - Path: {' → '.join(route_data.get('path', []))}
        - Total Time: {route_data.get('total_time', 0)} minutes
        - Emissions: {route_data.get('total_emissions', 0)}g CO₂
        - Green Score: {route_data.get('green_points_score', 0)}
        
        Provide sustainable transportation insights and recommendations.
        """
        
        request = OpenAIRequest(
            prompt=prompt,
            system_message=system_message,
            max_tokens=200,  # Limit for sustainability
            temperature=0.3,  # Lower temperature for consistent, efficient responses
            model=self.settings.OPENAI_MODEL
        )
        
        return await self.complete_chat(request)
    
    async def analyze_traffic_patterns(self, traffic_data: Dict) -> OpenAIResponse:
        """Analyze traffic patterns with AI insights."""
        system_message = """You are a traffic analysis AI. Provide brief insights about 
        traffic patterns and sustainable mobility recommendations. Focus on actionable advice."""
        
        prompt = f"""
        Traffic Analysis:
        - Traffic Level: {traffic_data.get('traffic_factor', 0) * 100:.0f}%
        - Incidents: {traffic_data.get('incident_factor', 0) * 100:.0f}%
        - Time: Hour {traffic_data.get('hour_of_day', 12)}
        - Peak Hour: {traffic_data.get('is_peak_hour', False)}
        
        Provide traffic insights and eco-friendly travel suggestions.
        """
        
        request = OpenAIRequest(
            prompt=prompt,
            system_message=system_message,
            max_tokens=150,
            temperature=0.4,
            model=self.settings.OPENAI_MODEL
        )
        
        return await self.complete_chat(request)
    
    async def complete_chat(self, request: OpenAIRequest) -> OpenAIResponse:
        """Complete chat request with sustainability optimizations."""
        if not self.ready:
            return self._mock_response("Service not ready", request)
        
        # Rate limiting check
        if not await self._check_rate_limit():
            return self._mock_response("Rate limit exceeded - practicing sustainable AI", request)
        
        # Check cache first
        cache_key = self._create_cache_key(request)
        cached_response = self.cache.get(cache_key)
        if cached_response:
            return OpenAIResponse(
                content=cached_response['content'],
                tokens_used=cached_response['tokens_used'],
                processing_time_ms=1.0,  # Cache is very fast
                energy_cost=0.001,  # Minimal energy for cache
                cache_hit=True,
                model_used=cached_response['model_used']
            )
        
        start_time = time.time()
        
        try:
            if self.client is None:
                return self._mock_response("No API key configured", request)
            
            # Make API request
            messages = []
            if request.system_message:
                messages.append({"role": "system", "content": request.system_message})
            messages.append({"role": "user", "content": request.prompt})
            
            response = await self.client.chat.completions.create(
                model=request.model,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=False  # No streaming for simplicity and energy efficiency
            )
            
            # Extract response data
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            processing_time = (time.time() - start_time) * 1000
            energy_cost = self._calculate_energy_cost(tokens_used, processing_time)
            
            # Cache response for sustainability
            cache_data = {
                'content': content,
                'tokens_used': tokens_used,
                'model_used': request.model,
                'timestamp': time.time()
            }
            self.cache.set(cache_key, cache_data, expire=3600)  # Cache for 1 hour
            
            # Update service metrics
            self.request_count += 1
            self.total_tokens_used += tokens_used
            self.total_api_time += (time.time() - start_time)
            
            return OpenAIResponse(
                content=content,
                tokens_used=tokens_used,
                processing_time_ms=processing_time,
                energy_cost=energy_cost,
                cache_hit=False,
                model_used=request.model
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._mock_response(f"API Error: {str(e)}", request)
    
    async def get_sustainability_tips(self, context: Dict) -> OpenAIResponse:
        """Get personalized sustainability tips."""
        system_message = """You are a green transportation advisor. Provide 3 practical, 
        actionable sustainability tips based on user context. Be concise and specific."""
        
        prompt = f"""
        User Context:
        - Recent trips: {context.get('trip_count', 0)}
        - CO₂ saved: {context.get('carbon_saved', 0)}g
        - Preferred route types: {context.get('preferred_routes', 'mixed')}
        
        Provide 3 personalized green transportation tips.
        """
        
        request = OpenAIRequest(
            prompt=prompt,
            system_message=system_message,
            max_tokens=200,
            temperature=0.5,
            model=self.settings.OPENAI_MODEL
        )
        
        return await self.complete_chat(request)
    
    def get_service_metrics(self) -> Dict:
        """Get OpenAI service metrics."""
        avg_tokens_per_request = (
            self.total_tokens_used / max(1, self.request_count)
        )
        
        avg_api_time = (
            self.total_api_time / max(1, self.request_count)
        ) * 1000  # Convert to ms
        
        cache_stats = {
            'size': len(self.cache) if hasattr(self.cache, '__len__') else 0,
            'hits': getattr(self.cache, 'hits', 0),
            'misses': getattr(self.cache, 'misses', 0)
        }
        
        cache_hit_rate = (
            cache_stats['hits'] / max(1, cache_stats['hits'] + cache_stats['misses'])
        ) * 100
        
        return {
            'service_status': 'ready' if self.ready else 'initializing',
            'api_status': 'connected' if self.client else 'disconnected',
            'performance': {
                'total_requests': self.request_count,
                'total_tokens_used': self.total_tokens_used,
                'avg_tokens_per_request': round(avg_tokens_per_request, 1),
                'avg_api_time_ms': round(avg_api_time, 2),
                'cache_hit_rate': round(cache_hit_rate, 2)
            },
            'sustainability': {
                'rate_limited': True,
                'caching_enabled': True,
                'efficient_model': self.settings.OPENAI_MODEL == "gpt-3.5-turbo",
                'token_optimized': True
            },
            'cache_stats': cache_stats
        }
    
    def is_ready(self) -> bool:
        """Check if service is ready."""
        return self.ready
    
    async def cleanup(self) -> None:
        """Cleanup service resources."""
        if self.client:
            await self.client.close()
        if hasattr(self.cache, 'close'):
            self.cache.close()
        logger.info("🧹 OpenAI service cleanup complete")
    
    async def _test_connection(self) -> None:
        """Test OpenAI API connection."""
        if not self.client:
            return
            
        try:
            # Simple test request
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            logger.info("🔗 OpenAI API connection verified")
        except Exception as e:
            raise RuntimeError(f"OpenAI API connection failed: {e}")
    
    async def _check_rate_limit(self) -> bool:
        """Check if request is within rate limits."""
        current_time = time.time()
        
        # Remove old timestamps (older than 1 minute)
        self.request_timestamps = [
            ts for ts in self.request_timestamps 
            if current_time - ts < 60
        ]
        
        # Check if under limit
        if len(self.request_timestamps) >= self.max_requests_per_minute:
            return False
        
        # Add current timestamp
        self.request_timestamps.append(current_time)
        return True
    
    def _create_cache_key(self, request: OpenAIRequest) -> str:
        """Create cache key for request."""
        # Create hash-like key from request parameters
        key_data = {
            'prompt': request.prompt[:100],  # First 100 chars for efficiency
            'model': request.model,
            'max_tokens': request.max_tokens,
            'temperature': round(request.temperature, 1),
            'system': request.system_message[:50] if request.system_message else ""
        }
        return json.dumps(key_data, sort_keys=True)
    
    def _calculate_energy_cost(self, tokens_used: int, processing_time_ms: float) -> float:
        """Calculate estimated energy cost for request."""
        # Simplified energy cost calculation
        token_cost = tokens_used * 0.001  # Cost per token
        time_cost = processing_time_ms * 0.0001  # Cost per ms
        return token_cost + time_cost
    
    def _mock_response(self, message: str, request: OpenAIRequest) -> OpenAIResponse:
        """Create mock response when API is unavailable."""
        mock_responses = {
            "Service not ready": "🌱 PragatiDhara is optimizing for sustainable transportation. Please try again in a moment.",
            "No API key configured": "🔧 AI insights are currently in eco-mode. Basic route optimization is still available!",
            "Rate limit exceeded - practicing sustainable AI": "⚡ Practicing sustainable AI - please wait a moment before the next request."
        }
        
        content = mock_responses.get(message, f"🤖 AI Service: {message}")
        
        return OpenAIResponse(
            content=content,
            tokens_used=0,
            processing_time_ms=1.0,
            energy_cost=0.0,
            cache_hit=False,
            model_used="mock"
        )