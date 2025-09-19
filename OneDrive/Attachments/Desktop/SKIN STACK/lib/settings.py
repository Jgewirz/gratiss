"""
Settings module - Pydantic env configuration
Following STEP 0 rules: minimal, < 50 LOC
"""
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Database (from env)
    database_url: PostgresDsn

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # App
    app_name: str = "SkinStack"
    debug: bool = False
    environment: str = "development"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Domain
    base_url: str = "http://localhost:8000"
    short_domain: str = "http://localhost:8000"

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Platform
    platform_fee_rate: float = 0.20
    min_payout_amount: float = 50.00
    default_cookie_window_days: int = 7

    # CORS Settings
    cors_origins: str = "*"  # Comma-separated list or "*" for all

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


settings = Settings()