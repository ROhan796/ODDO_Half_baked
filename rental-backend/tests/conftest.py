"""Shared test fixtures."""
import asyncio
import json
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import String, Text, TypeDecorator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles

# Make sqlite3 accept Python list/dict/tuple by auto-serializing to JSON
sqlite3.register_adapter(list, json.dumps)
sqlite3.register_adapter(dict, json.dumps)
sqlite3.register_adapter(tuple, json.dumps)


class UUIDType(TypeDecorator):
    """SQLite-compatible UUID type that converts to/from uuid.UUID objects."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(value)
        except (ValueError, AttributeError):
            return value


class SQLiteArrayType(TypeDecorator):
    """SQLite-compatible ARRAY type that stores JSON strings."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, (list, tuple)):
            return json.dumps(list(value))
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value


class SQLiteJSONType(TypeDecorator):
    """SQLite-compatible JSONB type that stores JSON strings."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value


def _patch_pg_types_for_sqlite():
    """Replace PostgreSQL-specific column types with SQLite-compatible TypeDecorators."""
    from app.utils.database import Base
    from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY, JSONB, INET, UUID as PG_UUID

    for table in Base.metadata.tables.values():
        for column in table.columns:
            type_name = type(column.type).__name__
            if type_name in ("UUID",):
                column.type = UUIDType()
            elif type_name in ("ARRAY",):
                column.type = SQLiteArrayType()
            elif type_name == "JSONB":
                column.type = SQLiteJSONType()
            elif type_name == "INET":
                column.type = Text()


from app.main import app
from app.utils.database import Base
from app.core.auth import create_access_token, hash_password
from app.models.user import User, UserRole, UserType

_patch_pg_types_for_sqlite()

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db():
        yield db_session

    async def _override_get_read_db():
        yield db_session

    app.dependency_overrides[app] = None
    from app.utils.database import get_db, get_read_db

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_read_db] = _override_get_read_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def seed_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid.uuid4(),
        name="Test User",
        email="test@example.com",
        phone="9876543210",
        password_hash=hash_password("Test@1234"),
        role=UserRole.PORTAL_USER,
        user_type=UserType.PERSONAL,
        kyc_status="verified",
        trust_score=50,
        trust_tier="silver",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def seed_admin(db_session: AsyncSession) -> User:
    admin = User(
        id=uuid.uuid4(),
        name="Test Admin",
        email="admin@example.com",
        phone="9999999999",
        password_hash=hash_password("Admin@1234"),
        role=UserRole.SUPER_ADMIN,
        user_type=UserType.PERSONAL,
        kyc_status="verified",
        trust_score=100,
        trust_tier="platinum",
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def auth_headers(seed_user: User) -> dict:
    token = create_access_token(
        str(seed_user.id),
        seed_user.role.value,
        seed_user.user_type.value,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_auth_headers(seed_admin: User) -> dict:
    token = create_access_token(
        str(seed_admin.id),
        seed_admin.role.value,
        seed_admin.user_type.value,
    )
    return {"Authorization": f"Bearer {token}"}
