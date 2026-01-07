"""
Test configuration and fixtures
"""
import pytest
import os
import tempfile
import shutil
from pathlib import Path


@pytest.fixture(scope="session")
def test_db():
    """Create a temporary test database"""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_prometheus.db")
    
    # Set environment variable for test database
    os.environ["DATABASE_PATH"] = db_path
    
    yield db_path
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def test_config():
    """Set test configuration"""
    original_values = {}
    
    # Save original values
    test_vars = {
        "DEBUG": "true",
        "SECRET_KEY": "test-secret-key-for-testing-only",
        "REDIS_ENABLED": "false",
        "RATE_LIMIT_ENABLED": "false",
        "LOG_LEVEL": "DEBUG"
    }
    
    for key, value in test_vars.items():
        original_values[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield test_vars
    
    # Restore original values
    for key, value in original_values.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest.fixture(autouse=True)
def reset_database(test_db):
    """Reset database before each test"""
    # Import here to avoid circular imports
    import database as db
    
    # Reinitialize database
    db.init_db()
    
    yield
    
    # Could add cleanup here if needed


@pytest.fixture
def sample_query():
    """Sample RAG query for testing"""
    return "What are the top fintech startups in Bangalore?"


@pytest.fixture
def sample_response():
    """Sample RAG response for testing"""
    return """
    Based on the funding data, here are the top fintech startups in Bangalore:
    
    1. Startup A - $10M Series A funding
    2. Startup B - $5M Seed funding
    3. Startup C - $3M Angel funding
    """
