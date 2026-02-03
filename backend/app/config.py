from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"  # MongoDB connection string
    mongodb_db_name: str = "sems_db"  # Database name

    # JWT Configuration
    jwt_secret_key: str = "your-secret-key-change-in-production"  # Secret key for JWT
    jwt_algorithm: str = "HS256"  # Algorithm used for JWT
    jwt_access_token_expire_minutes: int = 5000  # Token expiration time in minutes

    # Backend Configuration
    backend_host: str = "0.0.0.0"  # Host for the backend server
    backend_port: int = 8000  # Port for the backend server

    # AI Service Configuration
    ai_service_url: str = "http://localhost:8001"  # URL for the AI service

    # Device status timings (seconds)
    device_timeout_seconds: int = 120  # Timeout for marking devices as inactive
    device_status_interval_seconds: int = 30  # Interval for checking device status

    # Pydantic model configuration
    model_config = SettingsConfigDict(
        env_file=".env",  # Load environment variables from .env file
        case_sensitive=False,  # Environment variables are case-insensitive
        extra="ignore"  # Ignore extra fields in the .env file
    )


# Initialize settings instance
settings = Settings()
