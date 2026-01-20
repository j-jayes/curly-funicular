"""Configuration utilities."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # GCP settings
    gcp_project_id: str = "swedish-labor-market"
    gcs_bucket_name: str = "labor-market-data"
    
    # SCB settings
    scb_api_key: Optional[str] = None
    
    # Data settings
    data_raw_path: str = "data/raw"
    data_processed_path: str = "data/processed"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Get application settings.
    
    Returns:
        Settings instance
    """
    return Settings()
