# app/utils/database.py
import ssl
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.config import settings


class Base(DeclarativeBase):
    pass


def _get_ssl_context():
    """Create SSL context for NeonDB connections."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _is_cloud_db(url: str) -> bool:
    """Check if DATABASE_URL points to a cloud database (NeonDB, etc.)."""
    return any(host in url for host in ["neon.tech", "amazonaws.com", "azure.com", "google.com"])


# Primary engine (writes)
primary_connect_args = {"statement_cache_size": 0}
if _is_cloud_db(settings.DATABASE_URL):
    primary_connect_args["ssl"] = _get_ssl_context()

primary_engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_pre_ping=True,
    echo=settings.DEBUG,
    connect_args=primary_connect_args,
)

# Read replica engine (reads)
read_url = settings.DATABASE_READ_URL or settings.DATABASE_URL
read_connect_args = {"statement_cache_size": 0}
if _is_cloud_db(read_url):
    read_connect_args["ssl"] = _get_ssl_context()

read_engine = create_async_engine(
    read_url,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=False,
    connect_args=read_connect_args,
)

# Session factories
PrimarySessionLocal = async_sessionmaker(
    bind=primary_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

ReadSessionLocal = async_sessionmaker(
    bind=read_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Dependency injection
async def get_db():
    """Write operations -> Primary"""
    async with PrimarySessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_read_db():
    """Read operations -> Replica"""
    async with ReadSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
