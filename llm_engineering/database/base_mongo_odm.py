import uuid
from abc import ABC
from typing import Generic, Type, TypeVar
from loguru import logger
from pydantic import UUID4, BaseModel, Field
from pymongo import errors
from time import time

from llm_engineering.database.mongo_connection import connection
from llm_engineering.settings import settings

# Set up the initial database connection
try:
    _database = connection.get_database(settings.DATABASE_NAME)
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise e  # Raise an exception if the connection fails

"""
### Object-Document Mapper (ODM) Overview
This class defines a **MongoDB-compatible ODM**, similar to ORM but designed for NoSQL databases.
It allows defining a **base document class** that can be extended for different MongoDB collections.

We leverage **TypeVar (T)** for generic typing, ensuring that subclasses maintain the correct type hinting.

TypeVar Reference:
- https://realpython.com/python-type-checking/
- https://realpython.com/python312-typing/
"""

# Define a **TypeVar** with a bound, restricting it to subclasses of `NoSQLBaseDocument`
T = TypeVar("T", bound="NoSQLBaseDocument")


class NoSQLBaseDocument(BaseModel, Generic[T], ABC):
    """Base class for MongoDB documents using Pydantic and UUIDs."""
    
    # **Auto-generating a UUID4-based unique identifier for MongoDB documents**
    id: UUID4 = Field(default_factory=uuid.uuid4)

    # Implementing comparison and hashing methods for better usage in dictionaries and sets
    def __eq__(self, value: object) -> bool:
        """Enables comparison between instances using their unique `id`."""
        logger.debug(f"Comparing {self.__class__.__name__} with {value.__class__.__name__}")
        if not isinstance(value, self.__class__):
            return False
        return self.id == value.id

    def __hash__(self) -> int:
        """Allows instances to be used as dictionary keys or in sets."""
        return hash(self.id)

    @classmethod
    def from_mongo(cls: Type[T], data: dict) -> T:
        """
        Converts a MongoDB document into a class instance.
        
        - MongoDB stores `_id` as a string; this method **converts it into a UUID**.
        """
        if not data:
            raise ValueError("Data is empty.")
        
        # Extract the MongoDB `_id` and convert it to a UUID object
        id = uuid.UUID(data.pop("_id"))
        
        return cls(**dict(data, id=id))

    def to_mongo(self: T, **kwargs) -> dict:
        """
        Converts the class instance into a MongoDB-compatible dictionary.
        
        - MongoDB expects `_id` as a **string**, so this method ensures proper conversion.
        - Uses Pydantic's `model_dump()` to serialize fields.
        """
        exclude_unset = kwargs.pop("exclude_unset", False) #unpacked from kwargs pop the exclude_unset flag
        by_alias = kwargs.pop("by_alias", True) #unpacked from kwargs pop the by_alias flag

        # Serialize the model instance into a dictionary
        # dumps all fields from kwargs, excluding unset fields if specified
        # and using aliases if specified
        parsed = self.model_dump(exclude_unset=exclude_unset, by_alias=by_alias, **kwargs)

        # Ensure `_id` is correctly set as a string before inserting into MongoDB
        if "_id" not in parsed and "id" in parsed:
            parsed["_id"] = str(parsed.pop("id"))

        # Convert any remaining UUID fields into strings
        for key, value in parsed.items():
            if isinstance(value, uuid.UUID):
                parsed[key] = str(value)

        return parsed

    def save(self: T, **kwargs) -> T | None:
        """
        Saves the document to the MongoDB collection.
        
        - Converts the class instance into MongoDB format using `to_mongo()`.
        """
        collection = _database[self.get_collection_name()]
        try:
            # Insert the document into the MongoDB collection
            logger.debug(f"Inserting document into collection: {self.get_collection_name()}")
            collection.insert_one(self.to_mongo(**kwargs))
            return self
        except errors.WriteError:
            logger.exception("Failed to insert document.")
            return None

    @classmethod
    def get_or_create(cls: Type[T], **filter_options) -> T:
        """
        Retrieves an existing document or **creates** a new one if it doesn't exist.
        
        - Attempts to find a matching document in MongoDB using `filter_options`.
        - If found, it converts the result using `from_mongo()`.
        - Otherwise, it **creates a new instance** and inserts it.
        """
        collection = _database[cls.get_collection_name()]
        start_time = time()  # Start timing the operation
        try:
            instance = collection.find_one(filter_options)
            if instance:
                logger.info(f"Document found in {time() - start_time:.2f} seconds")
                return cls.from_mongo(instance)

            # Create and save a new document if no match is found
            new_instance = cls(**filter_options)
            new_instance = new_instance.save()

            logger.success(f"New document inserted in {time() - start_time:.3f}s")
            return new_instance
        except errors.OperationFailure:
            logger.exception(f"MongoDB Failed to retrieve document with filter options: {filter_options}")
            raise

    @classmethod
    def bulk_insert(cls: Type[T], documents: list[T], **kwargs) -> bool:
        """
        Inserts multiple documents into the MongoDB collection.
        
        - Converts each instance using `to_mongo()` before insertion.
        """
        collection = _database[cls.get_collection_name()]
        try:
            collection.insert_many(doc.to_mongo(**kwargs) for doc in documents)
            return True
        except (errors.WriteError, errors.BulkWriteError):
            logger.error(f"Failed to insert documents of type {cls.__name__}")
            return False

    @classmethod
    def find(cls: Type[T], **filter_options) -> T | None:
        """
        Finds a **single** document in MongoDB.
        
        - Uses the provided filter options.
        """
        collection = _database[cls.get_collection_name()]
        try:
            instance = collection.find_one(filter_options)
            return cls.from_mongo(instance) if instance else None
        except errors.OperationFailure:
            logger.error("Failed to retrieve document")
            return None

    @classmethod
    def bulk_find(cls: Type[T], **filter_options) -> list[T]:
        """
        Finds **multiple** documents matching filter criteria.
        """
        collection = _database[cls.get_collection_name()]
        try:
            instances = collection.find(filter_options)
            return [document for instance in instances if (document := cls.from_mongo(instance)) is not None]
        except errors.OperationFailure:
            logger.error("Failed to retrieve documents")
            return []

    @classmethod
    def get_collection_name(cls: Type[T]) -> str:
        """Retrieves the collection name from the Settings configuration class."""
        try:
            print(f"Using collection name: {cls.Settings.name}")
            if not hasattr(cls, 'Settings'):
                raise ValueError("Settings class is not defined in the document class.")
            return cls.Settings.name
        except AttributeError:
            raise ValueError("Missing 'name' attribute in the Settings configuration class.")