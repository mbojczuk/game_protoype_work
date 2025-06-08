from llm_engineering.database.base_mongo_odm import NoSQLBaseDocument
from llm_engineering.database.mongo_connection import connection
from llm_engineering.settings import settings


class ExampleDocument(NoSQLBaseDocument):
    name: str
    document: str
    # Define the Settings class to specify the MongoDB collection name
    class Settings:
        name = "tester"  # MongoDB collection name


if __name__ == "__main__":
    # connect to the database
    try:
        _database = connection.get_database(settings.DATABASE_NAME)
        print(f"Connected to database: {settings.DATABASE_NAME}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise e  # Raise an exception if the connection fails
    
    # Example usage of ExampleDocument
    example_doc = ExampleDocument(name="Test Document", document="This is a sample document testing the connection.")
    print(f"Created ExampleDocument: {example_doc}")

    # Insert the document into the collection
    example_doc.save()
    print(f"Document saved with ID: {example_doc.id}")

    # get or create the collection, since we are using a singleton pattern we should get the required here
    docs = example_doc.get_or_create()
    print(f"Retrieved document: {docs}")

    # Create a list of ExampleDocument instances for bulk insertion
    temp_doc_list = [ExampleDocument(name=f"Test Document {i}", document=f"This is a sample document testing the connection {i}.") for i in range(5)]
    
    # Insert multiple documents into the collection
    inserted = ExampleDocument.bulk_insert(temp_doc_list)
    print(f"Bulk insert successful: {inserted}")

    # Find a bulk of documents based on a filter since we passed a bunch of documents under name 0 then we should find a bunch
    found_docs = ExampleDocument.bulk_find(name="Test Document 0")
    print(f"Found documents: {found_docs}")