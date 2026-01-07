# Testing Guide for Prometheus

## Quick Start

### Install Test Dependencies

```bash
cd prometheus-ui/backend
pip install -r requirements-test.txt
```

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html --cov-report=term
```

View HTML coverage report:
```bash
# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_validators.py       # Pydantic model validation tests
├── test_utils.py           # Utility function tests
└── test_integration.py     # API endpoint integration tests
```

## Running Specific Tests

### Run Single File

```bash
pytest tests/test_validators.py
```

### Run Specific Test Class

```bash
pytest tests/test_validators.py::TestRagRequestValidator
```

### Run Specific Test

```bash
pytest tests/test_validators.py::TestRagRequestValidator::test_valid_query
```

### Run Tests Matching Pattern

```bash
pytest -k "test_valid"
```

## Test Fixtures

Available fixtures from `conftest.py`:

### `test_db`
Temporary test database, auto-cleaned after tests.

```python
def test_something(test_db):
    # test_db contains path to temporary database
    pass
```

### `test_config`
Test environment configuration.

```python
def test_with_config(test_config):
    # Configuration is set for testing
    assert test_config["DEBUG"] == "true"
```

### `sample_query`
Sample RAG query for testing.

```python
def test_query_processing(sample_query):
    result = process_query(sample_query)
    assert result is not None
```

### `sample_response`
Sample RAG response for testing.

```python
def test_save_chat(sample_query, sample_response):
    save_chat(sample_query, sample_response)
```

## Writing New Tests

### Test Validators

```python
import pytest
from pydantic import ValidationError
from validators import RagRequestValidated

def test_your_validation():
    """Test description"""
    # Valid case
    request = RagRequestValidated(query="Test query")
    assert request.query == "Test query"
    
    # Invalid case
    with pytest.raises(ValidationError):
        RagRequestValidated(query="")
```

### Test Utilities

```python
from utils.amount_utils import parse_amount

def test_your_utility():
    """Test description"""
    result = parse_amount("$1,000")
    assert result == 1000
```

### Test API Endpoints

```python
from fastapi.testclient import TestClient
from main import app

def test_your_endpoint():
    """Test description"""
    client = TestClient(app)
    response = client.get("/your-endpoint")
    
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
```

## Test Coverage Goals

Target coverage levels:
- **Critical Modules**: 90%+ (validators, auth, database)
- **Service Layer**: 80%+ (RAG service, cache service)
- **Utilities**: 85%+ (amount utils, transliteration)
- **Overall**: 75%+

Check coverage:
```bash
pytest --cov=. --cov-report=term-missing
```

## Common Test Patterns

### Testing Exceptions

```python
import pytest

def test_raises_exception():
    with pytest.raises(ValueError, match="specific error message"):
        dangerous_function()
```

### Testing Async Functions

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

### Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    ("$1000", 1000),
    ("₹5000", 5000),
    ("€2000", 2000),
])
def test_parse_amounts(input, expected):
    assert parse_amount(input) == expected
```

### Mocking External Services

```python
from unittest.mock import Mock, patch

def test_with_mock():
    with patch('ollama.generate') as mock_generate:
        mock_generate.return_value = {"response": "mocked"}
        result = call_ollama("test")
        assert result["response"] == "mocked"
```

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Best Practices

1. **Isolate Tests**: Each test should be independent
2. **Use Fixtures**: Reuse common setup code
3. **Clear Names**: Use descriptive test names
4. **Test Edge Cases**: Not just happy paths
5. **Fast Tests**: Keep tests quick (mock slow operations)
6. **Clean Up**: Use fixtures for cleanup
7. **Readable Assertions**: One assertion concept per test

## Debugging Tests

### Run with Verbose Output

```bash
pytest -v
```

### Stop at First Failure

```bash
pytest -x
```

### Run Last Failed Tests

```bash
pytest --lf
```

### Show Print Statements

```bash
pytest -s
```

### Drop into Debugger on Failure

```bash
pytest --pdb
```

### Run Specific Tests with Debug Output

```bash
pytest -vvs tests/test_validators.py::test_specific
```

## Performance Testing

### Measure Test Duration

```bash
pytest --durations=10
```

### Profile Tests

```bash
pytest --profile
```

## Test Database

Tests use a temporary SQLite database that is:
- Created before each test session
- Reset before each test
- Cleaned up after session ends

Location: Temporary directory (auto-managed)

## Troubleshooting

### Tests Fail with Import Errors

```bash
# Ensure you're in the backend directory
cd prometheus-ui/backend

# Reinstall dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Tests Fail with Database Errors

```bash
# Set test environment
export SKIP_CONFIG_VALIDATION=true

# Run tests
pytest
```

### Tests are Slow

```bash
# Run in parallel (install pytest-xdist)
pip install pytest-xdist
pytest -n auto
```

## Advanced Testing

### Integration Testing with Docker

```bash
# Start services
docker-compose -f docker-compose.test.yml up -d

# Run tests
pytest tests/test_integration.py

# Cleanup
docker-compose -f docker-compose.test.yml down
```

### Load Testing

```bash
# Install locust
pip install locust

# Create locustfile.py
# Run load tests
locust -f locustfile.py --host=http://localhost:8000
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pydantic Testing](https://docs.pydantic.dev/latest/usage/validation_errors/)
- [Coverage.py](https://coverage.readthedocs.io/)

## Support

For testing issues:
1. Check test output carefully
2. Review this guide
3. Check `conftest.py` for available fixtures
4. Open GitHub issue with test output
