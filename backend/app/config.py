# from pydantic_settings import BaseSettings
# from typing import Optional


# class Settings(BaseSettings):
#     # MongoDB Configuration
#     mongodb_url: str = "mongodb://localhost:27017"
#     mongodb_db_name: str = "sems_db"
    
#     # JWT Configuration
#     jwt_secret_key: str = "your-secret-key-change-in-production"
#     jwt_algorithm: str = "HS256"
#     jwt_access_token_expire_minutes: int = 30
    
#     # Backend Configuration
#     backend_host: str = "0.0.0.0"
#     backend_port: int = 8000
    
#     # AI Service Configuration
#     ai_service_url: str = "http://localhost:8001"
    
#     class Config:
#         env_file = ".env"
#         case_sensitive = False


# settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "sems_db"

    # JWT Configuration
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # Backend Configuration
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # AI Service Configuration
    ai_service_url: str = "http://localhost:8001"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"   # 👈 دي أهم سطر
    )


settings = Settings()
