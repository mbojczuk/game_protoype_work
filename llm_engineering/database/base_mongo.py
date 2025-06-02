import uuid
from abc import ABC
from typing import Generic, Type, TypeVar
from loguru import logger
from pydantic import UUID4, BaseModel, Field
from pymongo import errors

from llm_engineering.database.mongo_connection import connection
from llm_engineering.model.settings import settings

# set up initial database connection
try:
   _database = connection.get_database(settings.MONGO_DATABASE_NAME)
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise e # raise an exception if the connection fails

""" 
Leverage TypeVar for generic type hinting, this allows us to specify that T is a subclass of NoSQLBaseDocument
When we implement the class, we can use T to refer to the specific type of NoSQLBaseDocument being used.
Such as where T can be replace with ArticleDocument, UserDocument, etc.
https://realpython.com/python-type-checking/
https://realpython.com/python312-typing/
"""

T = TypeVar("T", bound="NoSQLBaseDocument")

class NoSQLBaseDocument(BaseModel, Generic[T], ABC):
    var = 1