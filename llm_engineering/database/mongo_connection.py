from pymongo import MongoClient
from loguru import logger
from pymongo.errors import ConnectionFailure

from llm_engineering.model.settings import settings

class MongoDatabaseConnector:
    """
    Singleton class to manage MongoDB connection using pymongo.
    Ensures only one instance of MongoClient is created.
    """

    _instance: MongoClient | None = None  # Stores the single instance of MongoClient

    def __new__(cls, *args, **kwargs) -> MongoClient:
        """
        Overrides the __new__ method to implement a singleton pattern.
        If an instance doesn't exist, it creates one; otherwise, returns the existing instance.
        """
        if cls._instance is None:
            try:
                logger.info("Attempting to connect to MongoDB...")  # Log connection attempt
                
                # Establish a connection to MongoDB using settings configuration
                cls._instance = MongoClient(
                    host=settings.MONGO_HOST,  # MongoDB host address
                    port=settings.MONGO_PORT,  # MongoDB port number
                    username=settings.MONGO_USER,  # MongoDB authentication username
                    password=settings.MONGO_PASSWORD  # MongoDB authentication password
                )

                logger.success("Successfully connected to MongoDB")  # Log success
            except ConnectionFailure as e:
                logger.error(f"Failed to connect to MongoDB: {e!s}")  # Log failure
                raise ConnectionError(f"Couldn't connect to the database: {e!s}")

        return cls._instance  # Return the singleton instance of MongoClient

# Instantiate the database connection (ensures a single connection)
connection = MongoDatabaseConnector()