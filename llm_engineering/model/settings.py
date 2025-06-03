from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    """Configuration class for application settings using Pydantic."""

    # MongoDB connection details (constants)
    MONGO_HOST: str = "localhost"  # Default MongoDB host
    MONGO_PORT: int = 27017  # Default MongoDB port
    MONGO_USER: str = "llm"  # MongoDB username
    MONGO_PASSWORD: str = "llm"  # MongoDB password
    DATABASE_NAME: str = "llm_game"  # Target database name

    class Config:
        """Pydantic configuration settings."""
        
        ENV_PREFIX = "APP_"  # Prefix for environment variables (e.g., APP_MONGO_HOST)
        ENV_FILE = ".env"  # Load settings from a .env file

# Instantiate settings
settings = AppSettings()

# Example usage: Accessing settings
# print(f"Connecting to MongoDB at {settings.MONGO_HOST}:{settings.MONGO_PORT}")