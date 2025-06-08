from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class AppSettings(BaseSettings):
    """Configuration class for application settings using Pydantic."""

    # MongoDB connection details (constants)
    MONGO_HOST: str = "localhost"  # Default MongoDB host
    MONGO_PORT: int = 27017  # Default MongoDB port
    MONGO_USER: str = "llm"  # MongoDB username
    MONGO_PASSWORD: str = "llm"  # MongoDB password
    DATABASE_NAME: str = "llm_game"  # Target database name

    model_config = ConfigDict(env_prefix="APP_", env_file=".env")


# Instantiate settings
settings = AppSettings()

# Example usage: Accessing settings
# print(f"Connecting to MongoDB at {settings.MONGO_HOST}:{settings.MONGO_PORT}")