"""
Configuration Management
Environment-based configuration for the enhanced MCP server
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Server configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Database configuration
    database_url: str = Field(..., env="DATABASE_URL")
    db_min_connections: int = Field(default=5, env="DB_MIN_CONNECTIONS")
    db_max_connections: int = Field(default=20, env="DB_MAX_CONNECTIONS")
    
    # Security configuration
    cors_origins: str = Field(default="*", env="CORS_ORIGINS")
    rate_limit_per_minute: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    
    # Performance configuration
    query_timeout_seconds: int = Field(default=30, env="QUERY_TIMEOUT_SECONDS")
    max_preview_rows: int = Field(default=10, env="MAX_PREVIEW_ROWS")
    
    # Monitoring configuration
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def get_settings() -> Settings:
    """Get application settings (cached)"""
    return Settings()

# Global settings instance
settings = get_settings()