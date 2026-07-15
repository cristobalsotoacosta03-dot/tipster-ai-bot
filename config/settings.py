"""
Configuration management using Pydantic Settings.
Loads environment variables and provides typed configuration.
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ===========================================
    # TELEGRAM CONFIGURATION
    # ===========================================
    telegram_bot_token: str
    telegram_admin_id: int
    telegram_vip_group_id: int
    
    # ===========================================
    # ANTHROPIC API (Claude)
    # ===========================================
    anthropic_api_key: str
    
    # ===========================================
    # STRIPE PAYMENTS
    # ===========================================
    stripe_api_key: str
    stripe_webhook_secret: str
    stripe_price_id_monthly: str
    stripe_price_id_yearly: str
    
    # ===========================================
    # FOOTBALL DATA API
    # ===========================================
    api_football_key: Optional[str] = None
    
    # ===========================================
    # REDIS CACHE (Upstash)
    # ===========================================
    upstash_redis_rest_url: Optional[str] = None
    upstash_redis_rest_token: Optional[str] = None
    
    # ===========================================
    # APPLICATION SETTINGS
    # ===========================================
    environment: str = "development"
    log_level: str = "INFO"
    cache_ttl_hours: int = 6
    max_analysis_per_day: int = 50
    free_tips_per_day: int = 2
    
    # ===========================================
    # MONETIZATION
    # ===========================================
    vip_monthly_price_eur: float = 29.99
    vip_yearly_price_eur: float = 299.00
    currency: str = "EUR"
    
    # ===========================================
    # COMPUTED PROPERTIES
    # ===========================================
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def cache_ttl_seconds(self) -> int:
        """Convert cache TTL from hours to seconds."""
        return self.cache_ttl_hours * 3600


# Global settings instance
settings = Settings()