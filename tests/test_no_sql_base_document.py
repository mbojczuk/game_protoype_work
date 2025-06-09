import pytest
import uuid
from pymongo.errors import WriteError
from tqdm import tqdm

from llm_engineering.database.mongo_connection import MongoDatabaseConnector
from llm_engineering.database.base_mongo_odm import NoSQLBaseDocument

# If no work run this command in the terminal
# $env:PYTHONPATH="C:\projects\game_protoype_work" 

# Mock Document Class for Testing
@pytest.mark.usefixtures("mongo_connector")
class ExampleDocument(NoSQLBaseDocument):
    """Example subclass of NoSQLBaseDocument."""
    name: str

    class Settings:
        name = "test_collection"

@pytest.fixture(scope="module")
def mongo_connector():
    """Fixture to provide a database connection."""
    return MongoDatabaseConnector()

@pytest.fixture
def sample_document():
    """Fixture to generate a sample document."""
    return ExampleDocument(name="Test Entry")

def test_uuid_generation(sample_document):
    """Ensure UUID4 is automatically generated."""
    tqdm.write("🔍 Checking UUID generation...")
    assert isinstance(sample_document.id, uuid.UUID), "UUID generation failed!"

def test_to_mongo_conversion(sample_document):
    """Validate MongoDB serialization."""
    tqdm.write("🔄 Testing MongoDB serialization...")
    mongo_data = sample_document.to_mongo()

    assert "_id" in mongo_data, "_id missing from MongoDB representation!"
    assert mongo_data["_id"] == str(sample_document.id), "UUID conversion incorrect!"
    tqdm.write("✅ MongoDB serialization works.")

def test_save_document(sample_document, mongo_connector):
    """Test saving a document to MongoDB."""
    tqdm.write("💾 Inserting document...")
    saved_doc = sample_document.save()

    assert saved_doc is not None, "❌ Document saving failed!"
    tqdm.write("✅ Document saved successfully.")

def test_find_document(sample_document):
    """Ensure a saved document can be retrieved."""
    tqdm.write("🔍 Searching for document...")
    found_doc = ExampleDocument.find(name="Test Entry")

    assert found_doc is not None, "❌ Failed to retrieve document!"
    assert found_doc.name == sample_document.name, "❌ Retrieved document mismatch!"
    tqdm.write("✅ Document retrieval verified.")

def test_bulk_insert():
    """Test inserting multiple documents."""
    tqdm.write("💾 Bulk inserting...")
    docs = [ExampleDocument(name=f"Entry {i}") for i in range(5)]
    success = ExampleDocument.bulk_insert(docs)

    assert success, "❌ Bulk insert failed!"
    tqdm.write("✅ Bulk insertion successful.")

def test_bulk_find():
    """Ensure multiple documents can be found."""
    tqdm.write("🔍 Bulk searching...")
    results = ExampleDocument.bulk_find(name={"$regex": "Entry"})

    assert len(results) >= 5, "❌ Bulk retrieval failed!"
    tqdm.write(f"✅ Retrieved {len(results)} documents.")