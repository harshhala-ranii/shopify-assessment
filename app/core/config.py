"""
Configuration management for the Shopify Insights application.
Handles environment variables, settings, and configuration validation.
"""

import os
from typing import Optional
from pydantic import BaseSettings, validator, HttpUrl


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    app_name: str = "Shopify Store Insights Extractor"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API settings
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]
    
    # HTTP settings
    request_timeout: int = 30
    max_retries: int = 3
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # LLM settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 2000
    openai_temperature: float = 0.1
    
    # Database settings (optional)
    database_url: Optional[str] = None
    database_enabled: bool = False
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @validator("openai_api_key")
    def validate_openai_key(cls, v):
        """Validate OpenAI API key if provided."""
        if v is not None and len(v.strip()) == 0:
            return None
        return v
    
    @validator("database_url")
    def validate_database_url(cls, v):
        """Validate database URL if provided."""
        if v is not None and len(v.strip()) == 0:
            return None
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance."""
    return settings
