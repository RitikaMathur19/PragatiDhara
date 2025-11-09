"""
Configuration management for sustainable AI backend
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with sustainability focus."""
    
    # Application settings
    APP_NAME: str = "PragatiDhara Sustainable Backend"
    DEBUG: bool = False
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]
    
    # OpenAI settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"  # More energy efficient than GPT-4
    OPENAI_MAX_TOKENS: int = 500  # Limit tokens for sustainability
    OPENAI_TEMPERATURE: float = 0.7
    
    # RL Agent settings (CPU-optimized)
    RL_MODEL_PATH: str = "models/rl_agent_cpu.onnx"
    RL_QUANTIZATION: str = "INT8"  # Quantized for efficiency
    RL_BATCH_SIZE: int = 1  # Single inference for real-time
    RL_CACHE_SIZE: int = 100  # Cache recent predictions
    
    # Route optimization settings
    ROUTE_CACHE_TTL: int = 300  # 5 minutes cache
    MAX_PATH_LENGTH: int = 20  # Limit search complexity
    ENABLE_ECO_PRIORITY: bool = True
    
    # Energy monitoring settings
    ENERGY_MONITORING: bool = True
    CPU_THRESHOLD: float = 80.0  # Alert threshold
    MEMORY_THRESHOLD: float = 85.0  # Alert threshold
    
    # Caching settings for sustainability
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 600  # 10 minutes default TTL
    ENABLE_DISK_CACHE: bool = True
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    STRUCTURED_LOGGING: bool = True
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()