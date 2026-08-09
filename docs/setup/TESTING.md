# Testing Guide

## Overview

Reprico uses **pytest** with three test tiers: unit, integration, and system tests. Tests run against SQLite for isolation and speed.

## Quick Start

```bash
cd rental-backend

# Install dev dependencies
pip install -r requirements.txt
pip install aiosqlite  # SQLite driver for tests

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific tier
pytest -m unit
pytest -m integration
pytest -m system
```

## Test Structure

```
tests/
├── conftest.py              # Fixtures, DB setup, auth helpers
├── unit/
│   ├── test_auth.py         # Password hashing, JWT, OTP (18 tests)
│   ├── test_permissions.py  # RBAC permission matrix (11 tests)
│   └── test_validators.py   # Input validation
├── integration/
│   └── test_rentals.py      # Rental lifecycle (3 tests)
└── system/
    └── test_api_endpoints.py # Full API flow (6 tests)
```

## Test Configuration

### `pyproject.toml`

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "system: System tests",
]
```

### `conftest.py` - Key Fixtures

```python
# SQLite-compatible type adapters
class UUIDType(TypeDecorator): ...      # UUID ↔ TEXT
class SQLiteArrayType(TypeDecorator): ... # ARRAY ↔ JSON
class SQLiteJSONType(TypeDecorator): ...  # JSONB ↔ JSON

# Test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
test_engine = create_async_engine(TEST_DATABASE_URL)

# Key fixtures:
# - db_session: Isolated session with rollback
# - client: AsyncClient with dependency overrides
# - seed_user: Pre-seeded test user
# - seed_admin: Pre-seeded admin user
# - auth_headers: JWT headers for regular user
# - admin_auth_headers: JWT headers for admin
```

## Writing Tests

### Unit Test Example

```python
# tests/unit/test_auth.py
import pytest
from app.core.auth import (
    hash_password, verify_password,
    create_access_token, verify_token,
    generate_otp, hash_token,
)


class TestPasswordHashing:
    def test_hash_password(self):
        hashed = hash_password("Test@1234")
        assert hashed != "Test@1234"
        assert len(hashed) > 50

    def test_verify_password(self):
        hashed = hash_password("Test@1234")
        assert verify_password("Test@1234", hashed) is True
        assert verify_password("WrongPass", hashed) is False


class TestAccessToken:
    def test_create_access_token(self):
        token = create_access_token("user-id", "portal_user", "personal")
        assert isinstance(token, str)
        assert len(token) > 50

    def test_verify_valid_token(self):
        token = create_access_token("user-id", "portal_user", "personal")
        payload = verify_token(token)
        assert payload["sub"] == "user-id"
        assert payload["role"] == "portal_user"
```

### Integration Test Example

```python
# tests/integration/test_rentals.py
import pytest
from httpx import AsyncClient


class TestRentalFlow:
    async def test_create_rental(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/v1/rentals/",
            headers=auth_headers,
            json={
                "product_id": "test-product-id",
                "start_date": "2025-02-01",
                "end_date": "2025-02-07",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"
        assert "id" in data

    async def test_list_rentals(self, client: AsyncClient, auth_headers: dict):
        response = await client.get(
            "/api/v1/rentals/",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
```

### System Test Example

```python
# tests/system/test_api_endpoints.py
import pytest
from httpx import AsyncClient


class TestAPIEndpoints:
    async def test_health_check(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    async def test_register_user(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "name": "New User",
                "email": "new@example.com",
                "phone": "9876543210",
                "password": "StrongPass@123",
                "user_type": "personal",
            },
        )
        assert response.status_code == 201

    async def test_login_wrong_password(self, client: AsyncClient, seed_user):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword",
            },
        )
        assert response.status_code == 401
```

## Test Markers

```python
@pytest.mark.unit
def test_password_hash(): ...

@pytest.mark.integration
async def test_rental_flow(): ...

@pytest.mark.system
async def test_full_api(): ...

# Skip tests
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature(): ...

# Conditional skip
@pytest.mark.skipif(
    not settings.SENTRY_DSN,
    reason="Sentry not configured"
)
def test_sentry_integration(): ...
```

## Running Tests

```bash
# All tests
pytest

# By marker
pytest -m unit
pytest -m integration
pytest -m system

# By file
pytest tests/unit/test_auth.py

# With verbose output
pytest -v

# Stop on first failure
pytest -x

# Show print output
pytest -s

# Run specific test
pytest tests/unit/test_auth.py::TestPasswordHashing::test_hash_password

# Coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pip install aiosqlite
      - run: pytest -v --cov=app
      - uses: codecov/codecov-action@v4
```

## Best Practices

1. **Isolation**: Each test gets a fresh database (via `setup_database` fixture)
2. **Naming**: `test_<action>_<condition>` (e.g., `test_login_wrong_password`)
3. **One assertion per concept**: Don't mix unrelated assertions
4. **Use fixtures**: Don't create test data inline
5. **Async**: All API tests use `async def` with `AsyncClient`
6. **Mock externals**: Don't call real Razorpay/Resend in tests

## Test Data Management

```python
# Creating test data
@pytest.fixture
async def sample_product(db_session):
    product = Product(
        id=uuid.uuid4(),
        name="Test Product",
        slug="test-product",
        category_id=sample_category.id,
        status=ProductStatus.AVAILABLE,
        purchase_price=10000,
    )
    db_session.add(product)
    await db_session.commit()
    return product

# Using test data
async def test_get_product(client, auth_headers, sample_product):
    response = await client.get(
        f"/api/v1/products/{sample_product.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
```

## Coverage Targets

| Tier | Target |
|------|--------|
| Unit tests | 90%+ |
| Integration | 80%+ |
| System | 70%+ |
| Overall | 85%+ |

## Debugging Tests

```bash
# Debug mode with pdb
pytest --pdb

# Show local variables on failure
pytest --tb=long

# Trace through test execution
pytest --setup-show

# Run last failed tests only
pytest --lf
```
