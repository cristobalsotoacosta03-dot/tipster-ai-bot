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
    # Optional on purpose: you can launch the bot (free tips, VIP
    # checkout, channel) before paying for Claude API credits. Analysis
    # simply stays unavailable until this is set.
    anthropic_api_key: Optional[str] = None
    
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

    # Optional free fallback data sources, used only when API-Football can't
    # find one of the two teams. See src/data/providers/.
    football_data_org_key: Optional[str] = None
    thesportsdb_api_key: Optional[str] = None

    # Optional: real bookmaker odds (The Odds API, free tier: 500 req/month,
    # no card required) to compare the model's confidence against the
    # market's implied probability. See src/data/odds_provider.py.
    odds_api_key: Optional[str] = None

    # Optional: Telegram "consensus" reader - reads public channels from a
    # separate user account (not the bot) to detect tipster agreement on a
    # match. Get api_id/api_hash from https://my.telegram.org, then run
    # scripts/telegram_consensus_login.py once to obtain the session string.
    telegram_consensus_api_id: Optional[str] = None
    telegram_consensus_api_hash: Optional[str] = None
    telegram_consensus_session: Optional[str] = None
    # Comma-separated public channel usernames to monitor for consensus
    # (e.g. "tipster_juan,picks_maria"). Empty/unset means the feature has
    # no channels configured yet - see src/consensus/.
    telegram_consensus_channels: Optional[str] = None
    
    # ===========================================
    # REDIS CACHE (Upstash)
    # ===========================================
    upstash_redis_rest_url: Optional[str] = None
    upstash_redis_rest_token: Optional[str] = None

    # ===========================================
    # DATABASE (optional Postgres)
    # ===========================================
    # Optional on purpose: when unset, DatabaseManager keeps using its
    # existing SQLite file (data/tipster_bot.db) exactly as before. Render's
    # Free plan has no persistent disk, so that SQLite file is wiped on every
    # redeploy/restart — losing users, VIP status, and payment history. To
    # fix this for real, create a free Postgres project (Supabase or Neon,
    # no card required) and set this to its connection string in Render's
    # dashboard env vars. See MANUAL_OPERATIVO.md for the exact steps.
    database_url: Optional[str] = None
    
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

    @property
    def consensus_channel_list(self) -> list[str]:
        """Parsed list of channel usernames from telegram_consensus_channels."""
        if not self.telegram_consensus_channels:
            return []
        return [c.strip() for c in self.telegram_consensus_channels.split(",") if c.strip()]


# Global settings instance
settings = Settings()