"""
Configuration management for Google Maps Backend API
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Google Maps Platform Configuration
    google_maps_api_key: str = Field(..., env="GOOGLE_MAPS_API_KEY")
    google_cloud_project_id: Optional[str] = Field(None, env="GOOGLE_CLOUD_PROJECT_ID")
    
    # API Server Configuration
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8001, env="API_PORT")
    debug_mode: bool = Field(False, env="DEBUG_MODE")
    api_prefix: str = Field("/api/v1", env="API_PREFIX")
    
    # CORS Configuration
    allowed_origins: List[str] = Field(
        ["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    allowed_methods: List[str] = Field(
        ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        env="ALLOWED_METHODS"
    )
    allowed_headers: List[str] = Field(["*"], env="ALLOWED_HEADERS")
    
    # Cache Configuration
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    cache_ttl_seconds: int = Field(3600, env="CACHE_TTL_SECONDS")
    cache_prefix: str = Field("gmaps_backend", env="CACHE_PREFIX")
    
    # Rate Limiting Configuration
    rate_limit_per_minute: int = Field(100, env="RATE_LIMIT_PER_MINUTE")
    daily_quota_limit: int = Field(10000, env="DAILY_QUOTA_LIMIT")
    burst_limit: int = Field(20, env="BURST_LIMIT")
    
    # Database Configuration (Optional)
    database_url: Optional[str] = Field(None, env="DATABASE_URL")
    db_pool_size: int = Field(20, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(30, env="DB_MAX_OVERFLOW")
    
    # Logging Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_format: str = Field("json", env="LOG_FORMAT")
    enable_access_logs: bool = Field(True, env="ENABLE_ACCESS_LOGS")
    
    # Google Maps API Specific Settings
    maps_region: str = Field("IN", env="MAPS_REGION")
    maps_language: str = Field("en", env="MAPS_LANGUAGE")
    default_travel_mode: str = Field("driving", env="DEFAULT_TRAVEL_MODE")
    
    # Route Optimization Settings
    max_waypoints: int = Field(25, env="MAX_WAYPOINTS")
    max_alternatives: int = Field(3, env="MAX_ALTERNATIVES")
    enable_traffic_model: bool = Field(True, env="ENABLE_TRAFFIC_MODEL")
    traffic_model: str = Field("best_guess", env="TRAFFIC_MODEL")
    
    # Geocoding Settings
    geocoding_region: str = Field("IN", env="GEOCODING_REGION")
    geocoding_bounds: str = Field("6.4627,68.1097|35.5127,97.3955", env="GEOCODING_BOUNDS")
    max_geocoding_results: int = Field(5, env="MAX_GEOCODING_RESULTS")
    
    # Distance Matrix Settings
    max_matrix_elements: int = Field(100, env="MAX_MATRIX_ELEMENTS")
    matrix_units: str = Field("metric", env="MATRIX_UNITS")
    avoid_tolls: bool = Field(False, env="AVOID_TOLLS")
    avoid_highways: bool = Field(False, env="AVOID_HIGHWAYS")
    
    # Emissions Calculation
    fuel_efficiency_km_per_liter: float = Field(15.0, env="FUEL_EFFICIENCY_KM_PER_LITER")
    co2_per_liter_petrol: float = Field(2.31, env="CO2_PER_LITER_PETROL")
    co2_per_liter_diesel: float = Field(2.68, env="CO2_PER_LITER_DIESEL")
    electric_vehicle_efficiency: float = Field(0.2, env="ELECTRIC_VEHICLE_EFFICIENCY")
    
    # Monitoring and Metrics
    enable_prometheus_metrics: bool = Field(True, env="ENABLE_PROMETHEUS_METRICS")
    metrics_port: int = Field(9090, env="METRICS_PORT")
    health_check_interval: int = Field(30, env="HEALTH_CHECK_INTERVAL")
    
    # Security Settings
    secret_key: str = Field("your-secret-key-change-this", env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # External Service Timeouts (seconds)
    http_timeout: int = Field(30, env="HTTP_TIMEOUT")
    geocoding_timeout: int = Field(10, env="GEOCODING_TIMEOUT")
    routes_timeout: int = Field(15, env="ROUTES_TIMEOUT")
    distance_matrix_timeout: int = Field(20, env="DISTANCE_MATRIX_TIMEOUT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Parse comma-separated list fields
        if isinstance(self.allowed_origins, str):
            self.allowed_origins = [origin.strip() for origin in self.allowed_origins.split(",")]
        if isinstance(self.allowed_methods, str):
            self.allowed_methods = [method.strip() for method in self.allowed_methods.split(",")]
        if isinstance(self.allowed_headers, str):
            self.allowed_headers = [header.strip() for header in self.allowed_headers.split(",")]


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance"""
    return settings


# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings"""
    debug_mode: bool = True
    log_level: str = "DEBUG"
    enable_access_logs: bool = True


class ProductionSettings(Settings):
    """Production environment settings"""
    debug_mode: bool = False
    log_level: str = "INFO" 
    enable_access_logs: bool = False


class TestingSettings(Settings):
    """Testing environment settings"""
    debug_mode: bool = True
    log_level: str = "DEBUG"
    database_url: str = "sqlite:///./test.db"
    cache_ttl_seconds: int = 60  # Shorter cache for tests


def get_environment_settings() -> Settings:
    """Get environment-specific settings"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Application metadata
class AppInfo:
    """Application information and metadata"""
    
    title: str = "Google Maps Routes API Backend"
    description: str = """
    Advanced route optimization backend service integrating with Google Maps Platform APIs.
    
    ## Features
    - Real-time route optimization with Google Maps Routes API
    - Multi-modal transportation support (driving, walking, transit, cycling)
    - Sustainable route recommendations with emissions tracking
    - Geocoding and reverse geocoding services
    - Distance matrix calculations for multi-destination planning
    - Traffic-aware routing with real-time conditions
    - Waypoint optimization and route comparison
    - Comprehensive caching and rate limiting
    
    ## API Documentation
    - **Interactive Docs**: Available at `/docs`
    - **ReDoc**: Available at `/redoc`
    - **OpenAPI Spec**: Available at `/openapi.json`
    """
    version: str = "1.0.0"
    contact: dict = {
        "name": "PragatiDhara Team",
        "email": "support@pragatidhara.com",
        "url": "https://pragatidhara.com"
    }
    license_info: dict = {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
    tags_metadata: list = [
        {
            "name": "routes",
            "description": "Route optimization and navigation endpoints",
        },
        {
            "name": "geocoding", 
            "description": "Address and coordinate conversion services",
        },
        {
            "name": "distance",
            "description": "Distance matrix and travel time calculations",
        },
        {
            "name": "maps",
            "description": "Google Maps integration and utilities",
        },
        {
            "name": "health",
            "description": "Health checks and system monitoring",
        }
    ]


app_info = AppInfo()