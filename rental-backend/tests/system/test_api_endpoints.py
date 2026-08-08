"""System tests for API endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, db_session):
    payload = {
        "name": "New User",
        "email": "newuser@example.com",
        "phone": "9876543211",
        "password": "StrongPass123!",
        "user_type": "personal",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


@pytest.mark.asyncio
async def test_register_duplicate_user(client: AsyncClient, db_session, seed_user):
    payload = {
        "name": "Duplicate User",
        "email": "test@example.com",
        "phone": "9876543210",
        "password": "StrongPass123!",
        "user_type": "personal",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient, db_session, seed_user):
    payload = {
        "identifier": "test@example.com",
        "password": "Test@1234",
        "device_fingerprint": "test-device-001",
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, db_session, seed_user):
    payload = {
        "identifier": "test@example.com",
        "password": "WrongPassword",
        "device_fingerprint": "test-device-002",
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient, db_session):
    payload = {
        "identifier": "nobody@example.com",
        "password": "whatever123",
        "device_fingerprint": "test-device-003",
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
