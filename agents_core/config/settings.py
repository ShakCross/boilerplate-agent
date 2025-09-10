"""Application settings and configuration."""

import os
from typing import Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables from .env file silently
load_dotenv(verbose=False)


class Settings(BaseSettings):
    """Main application settings."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(default="", description="OpenAI API key")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis URL")
    
    # Langfuse Configuration
    langfuse_host: str = Field(default="https://cloud.langfuse.com", description="Langfuse host")
    langfuse_public_key: str = Field(default="", description="Langfuse public key")
    langfuse_secret_key: str = Field(default="", description="Langfuse secret key")
    
    # LLM Configuration
    llm_model: str = Field(default="gpt-4o-mini", description="LLM model to use")
    max_tokens: int = Field(default=500, description="Maximum tokens for responses")
    temperature: float = Field(default=0.2, description="Temperature for LLM responses")
    
    # Application Configuration
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Log level")
    
    # Environment Detection
    environment: str = Field(default="local", description="Environment: local, docker, production")
    
    # Celery Configuration
    celery_broker_url: str = Field(default="redis://localhost:6379/0", description="Celery broker URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", description="Celery result backend")
    
    def get_redis_url_for_celery(self) -> str:
        """Get Redis URL optimized for Celery connections."""
        # Check if we have workers running in Docker (common dev setup)
        celery_broker = os.getenv("CELERY_BROKER_URL")
        if celery_broker:
            return celery_broker
            
        # If running in Docker, use internal Docker networking
        if self.environment == "docker":
            return "redis://redis:6379/0"
        
        # For local development connecting to Docker Redis, use localhost
        # but ensure we use the same broker URL as workers
        return "redis://localhost:6379/0"
    
    def get_redis_url_for_memory(self) -> str:
        """Get Redis URL optimized for memory/cache connections."""
        # Always use localhost for API connections when running locally
        if self.environment == "local":
            return "redis://localhost:6379/0"
        
        # In Docker, use internal networking
        return self.redis_url
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class TenantConfig:
    """Configuration for individual tenants."""
    
    def __init__(
        self,
        tenant_id: str,
        tone: str = "professional",
        disclaimers: list[str] | None = None,
        enabled_tools: list[str] | None = None,
        custom_instructions: str = "",
        language: str = "en"
    ):
        self.tenant_id = tenant_id
        self.tone = tone
        self.disclaimers = disclaimers or []
        self.enabled_tools = enabled_tools or []
        self.custom_instructions = custom_instructions
        self.language = language
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "tenant_id": self.tenant_id,
            "tone": self.tone,
            "disclaimers": self.disclaimers,
            "enabled_tools": self.enabled_tools,
            "custom_instructions": self.custom_instructions,
            "language": self.language
        }


# Global settings instance
settings = Settings()


def get_tenant_config(tenant_id: str) -> TenantConfig:
    """Get tenant configuration by ID."""
    # In a real implementation, this would fetch from a database or config store
    # For now, return default configuration
    return TenantConfig(
        tenant_id=tenant_id,
        tone="professional",
        disclaimers=["This is an AI assistant."],
        enabled_tools=["schedule_visit", "get_business_hours"],
        custom_instructions="Be helpful and concise.",
        language="en"
    )
