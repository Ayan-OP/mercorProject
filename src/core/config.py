from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # MongoDB Settings
    MONGO_URI: str
    DATABASE_NAME: str

    # JWT Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Token expires in 60 minutes
    
    # Email Settings
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: EmailStr
    
    # Admin 
    ADMIN_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env")

# Create a single, importable instance of the settings
settings = Settings()
