"""Integration tests for rental endpoints."""
import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_rental(client: AsyncClient, db_session, seed_user, seed_admin, admin_auth_headers):
    from app.models.product import Category, Product, ProductStatus
    from decimal import Decimal

    cat = Category(name="Test Cat", slug="test-cat-integration", is_active=True)
    db_session.add(cat)
    await db_session.flush()

    product = Product(
        name="Test Product",
        slug="test-product-integration",
        category_id=cat.id,
        status=ProductStatus.AVAILABLE,
        purchase_price=Decimal("50000.00"),
        deposit_percentage=Decimal("20.00"),
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    payload = {
        "customer_id": str(seed_user.id),
        "product_id": str(product.id),
        "start_date": "2026-09-01",
        "end_date": "2026-09-05",
        "rental_type": "daily",
    }

    response = await client.post("/api/v1/rentals/", json=payload, headers=admin_auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["customer_id"] == str(seed_user.id)
    assert data["product_id"] == str(product.id)
    assert "id" in data


@pytest.mark.asyncio
async def test_list_rentals(client: AsyncClient, admin_auth_headers):
    response = await client.get("/api/v1/rentals/", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "limit" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_get_rental(client: AsyncClient, db_session, seed_user, seed_admin, admin_auth_headers):
    from app.models.product import Category, Product, ProductStatus
    from app.models.rental import Rental, RentalStatus, RentalType
    from decimal import Decimal
    from datetime import date

    cat = Category(name="Test Cat Get", slug="test-cat-get", is_active=True)
    db_session.add(cat)
    await db_session.flush()

    product = Product(
        name="Test Product Get",
        slug="test-product-get",
        category_id=cat.id,
        status=ProductStatus.RENTED,
        purchase_price=Decimal("50000.00"),
        deposit_percentage=Decimal("20.00"),
    )
    db_session.add(product)
    await db_session.flush()

    rental = Rental(
        customer_id=seed_user.id,
        product_id=product.id,
        status=RentalStatus.ACTIVE,
        rental_type=RentalType.DAILY,
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 5),
        daily_rate=Decimal("500.00"),
        total_amount=Decimal("2000.00"),
        deposit_amount=Decimal("400.00"),
    )
    db_session.add(rental)
    await db_session.commit()
    await db_session.refresh(rental)

    response = await client.get(f"/api/v1/rentals/{rental.id}", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(rental.id)
    assert data["status"] == "active"
