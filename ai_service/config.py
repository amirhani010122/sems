# from pydantic_settings import BaseSettings


# class Settings(BaseSettings):
#     # AI Service Configuration
#     ai_service_host: str = "0.0.0.0"
#     ai_service_port: int = 8001
#     env_file = ".env"
#     extra = "ignore"
    
#     # Backend API URL
#     backend_api_url: str = "http://localhost:8000"
    
#     class Config:
#         env_file = ".env"
#         extra = "ignore"
#         case_sensitive = False


# settings = Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # AI Service Configuration
    ai_service_host: str = "0.0.0.0"
    ai_service_port: int = 8001
    
    # Backend API URL
    backend_api_url: str = "http://localhost:8000"

    # الإعدادات في V2 بتتحط في متغير اسمه model_config
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False
    )

settings = Settings()