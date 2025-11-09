"""
Pydantic models for API data validation and serialization
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


# Request Models
class TrafficStateRequest(BaseModel):
    """Traffic state data for RL predictions."""
    traffic_factor: float = Field(ge=0.0, le=1.0, description="Traffic congestion level (0-1)")
    incident_factor: float = Field(ge=0.0, le=1.0, description="Incident density (0-1)")
    time_of_day: float = Field(ge=0.0, lt=24.0, description="Hour of day (0-24)")
    day_of_week: int = Field(ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    weather_factor: float = Field(default=0.5, ge=0.0, le=1.0, description="Weather impact (0-1)")
    road_capacity: float = Field(default=1.0, ge=0.1, le=2.0, description="Road capacity multiplier")


class RouteOptimizationRequest(BaseModel):
    """Route optimization request."""
    start_node: str = Field(description="Starting location node ID")
    end_node: str = Field(description="Destination location node ID")
    alpha: Optional[float] = Field(default=1.0, ge=0.1, le=2.0, description="Emissions weighting factor")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User preferences")
    
    @validator('start_node', 'end_node')
    def validate_nodes(cls, v):
        valid_nodes = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'}
        if v not in valid_nodes:
            raise ValueError(f"Node must be one of {valid_nodes}")
        return v
    
    @validator('end_node')
    def validate_different_nodes(cls, v, values):
        if 'start_node' in values and v == values['start_node']:
            raise ValueError("Start and end nodes must be different")
        return v


class ModelUpdateRequest(BaseModel):
    """RL model update request."""
    traffic_state: TrafficStateRequest
    alpha_used: float = Field(ge=0.1, le=2.0)
    actual_performance: Dict[str, float] = Field(description="Actual performance metrics")


class OpenAIRequest(BaseModel):
    """OpenAI service request."""
    prompt: str = Field(min_length=1, max_length=2000, description="Input prompt")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    max_tokens: Optional[int] = Field(default=200, ge=10, le=500, description="Maximum tokens")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="Response creativity")


# Response Models
class RLPredictionResponse(BaseModel):
    """RL agent prediction response."""
    alpha: float = Field(description="Predicted optimal alpha value")
    confidence: float = Field(ge=0.0, le=1.0, description="Prediction confidence")
    processing_time_ms: float = Field(description="Processing time in milliseconds")
    energy_cost: float = Field(description="Estimated energy cost")
    cache_hit: bool = Field(description="Whether result was cached")
    model_version: str = Field(default="cpu-optimized-v1", description="Model version used")


class RouteResponse(BaseModel):
    """Individual route response."""
    path: List[str] = Field(description="Route path as node sequence")
    total_time: float = Field(ge=0, description="Total travel time in minutes")
    total_distance: float = Field(ge=0, description="Total distance in kilometers")
    total_emissions: float = Field(ge=0, description="Total CO2 emissions in grams")
    green_points_score: int = Field(ge=0, le=150, description="Environmental score (0-150)")
    route_type: str = Field(description="Route optimization type")
    processing_time_ms: float = Field(description="Processing time in milliseconds")
    cache_hit: bool = Field(default=False, description="Whether result was cached")


class RouteOptimizationResponse(BaseModel):
    """Route optimization response with multiple options."""
    routes: List[RouteResponse] = Field(description="Optimized route options")
    recommendation: str = Field(description="Recommended route type")
    total_processing_time_ms: float = Field(description="Total processing time")
    sustainability_score: int = Field(ge=0, le=100, description="Overall sustainability score")


class TrafficDataResponse(BaseModel):
    """Real-time traffic data response."""
    timestamp: float = Field(description="Unix timestamp")
    traffic_factor: float = Field(ge=0.0, le=1.0, description="Current traffic level")
    incident_factor: float = Field(ge=0.0, le=1.0, description="Current incident density")
    hour_of_day: int = Field(ge=0, le=23, description="Current hour")
    is_peak_hour: bool = Field(description="Whether it's peak traffic hour")
    weather_factor: float = Field(ge=0.0, le=1.0, description="Weather impact factor")
    recommendations: List[str] = Field(description="Traffic-based recommendations")


class OpenAIResponse(BaseModel):
    """OpenAI service response."""
    content: str = Field(description="Generated content")
    tokens_used: int = Field(ge=0, description="Tokens consumed")
    processing_time_ms: float = Field(description="Processing time in milliseconds")
    energy_cost: float = Field(description="Estimated energy cost")
    cache_hit: bool = Field(description="Whether result was cached")
    model_used: str = Field(description="AI model used")


class ServiceMetricsResponse(BaseModel):
    """Service performance metrics."""
    service_name: str = Field(description="Name of the service")
    status: str = Field(description="Service status")
    performance_metrics: Dict[str, Any] = Field(description="Performance statistics")
    sustainability_metrics: Dict[str, Any] = Field(description="Sustainability metrics")
    cache_metrics: Optional[Dict[str, Any]] = Field(description="Cache performance")


class EnergyMetricsResponse(BaseModel):
    """Energy and system metrics."""
    timestamp: float = Field(description="Measurement timestamp")
    cpu_usage_percent: float = Field(ge=0.0, le=100.0, description="CPU usage percentage")
    memory_usage_percent: float = Field(ge=0.0, le=100.0, description="Memory usage percentage")
    energy_efficiency_score: float = Field(ge=0.0, le=100.0, description="Energy efficiency score")
    sustainability_grade: str = Field(description="Sustainability grade (A+ to D)")
    recommendations: List[str] = Field(description="Efficiency recommendations")
    system_info: Dict[str, Any] = Field(description="System information")


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(description="Overall system status")
    timestamp: float = Field(description="Check timestamp")
    services: Dict[str, bool] = Field(description="Individual service status")
    system_metrics: Dict[str, float] = Field(description="System performance metrics")
    energy_efficient: bool = Field(description="Whether system is energy efficient")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    timestamp: float = Field(description="Error timestamp")
    request_id: Optional[str] = Field(description="Request ID for tracking")


# Audit and Logging Models
class AuditLogEntry(BaseModel):
    """Audit log entry for sustainability tracking."""
    timestamp: datetime = Field(default_factory=datetime.now)
    user_session: Optional[str] = Field(description="User session ID")
    action: str = Field(description="Action performed")
    route_request: Optional[RouteOptimizationRequest] = Field(description="Route request data")
    carbon_saved: float = Field(default=0.0, description="Carbon saved in grams")
    processing_time_ms: float = Field(description="Processing time")
    energy_cost: float = Field(description="Energy cost estimate")


class SustainabilityReport(BaseModel):
    """Sustainability impact report."""
    period_start: datetime = Field(description="Report period start")
    period_end: datetime = Field(description="Report period end")
    total_requests: int = Field(description="Total optimization requests")
    total_carbon_saved_kg: float = Field(description="Total carbon saved in kg")
    total_energy_saved_kwh: float = Field(description="Total energy saved in kWh")
    avg_processing_time_ms: float = Field(description="Average processing time")
    efficiency_score: float = Field(ge=0.0, le=100.0, description="Overall efficiency score")
    recommendations: List[str] = Field(description="Sustainability recommendations")


# Configuration Models
class NodeInfo(BaseModel):
    """Location node information."""
    id: str = Field(description="Node identifier")
    name: str = Field(description="Location name")
    latitude: float = Field(ge=-90.0, le=90.0, description="Latitude coordinate")
    longitude: float = Field(ge=-180.0, le=180.0, description="Longitude coordinate")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties")


class SystemConfigResponse(BaseModel):
    """System configuration response."""
    version: str = Field(description="Application version")
    environment: str = Field(description="Environment (dev/prod)")
    features_enabled: Dict[str, bool] = Field(description="Feature flags")
    sustainability_mode: bool = Field(description="Sustainability mode enabled")
    available_nodes: Dict[str, NodeInfo] = Field(description="Available location nodes")
    model_info: Dict[str, Any] = Field(description="AI model information")