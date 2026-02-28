"""Application configuration with security best practices."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation."""

    # OpenRouter API Configuration
    openrouter_api_key: str = Field(
        ..., 
        min_length=1, 
        description="OpenRouter API key for LLM access"
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenRouter API base URL"
    )
    model_name: str = Field(
        default="mistralai/mistral-7b-instruct:free",
        description="LLM model name"
    )

    # Application Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    critic_threshold: float = Field(
        default=7.0,
        ge=0.0,
        le=10.0,
        description="Quality threshold for critic agent"
    )
    max_retries: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts"
    )
    request_timeout: int = Field(
        default=300,
        ge=30,
        le=1800,
        description="Request timeout in seconds"
    )

    # Security (optional for API key auth)
    api_key_header: str = Field(
        default="X-API-Key",
        description="API key header name"
    )

    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=60,
        ge=1,
        le=1000,
        description="Rate limit per minute"
    )

    # Environment
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )

    @validator("openrouter_api_key")
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format."""
        if not v or v == "your_openrouter_api_key_here":
            raise ValueError("OpenRouter API key must be set")
        return v



    class Config:
        """Pydantic config."""
        
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields like removed secret_key


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()