"""Seeding utility functions."""
import random
import string
from datetime import datetime, timedelta, timezone


def random_phone() -> str:
    """Generate realistic 10-digit Indian phone number with +91 country code."""
    prefix = random.choice(["98", "97", "99", "96", "95", "91", "88", "87"])
    digits = "".join(random.choices(string.digits, k=8))
    return f"+91{prefix}{digits}"


def slugify(name: str) -> str:
    """Convert string to url-friendly slug."""
    clean = "".join(c.lower() if c.isalnum() or c == " " else "" for c in name)
    return "-".join(clean.split())


def random_date_range(status: str) -> tuple[datetime, datetime]:
    """Generate realistic start and end dates based on rental status."""
    now = datetime.now(timezone.utc)
    duration_days = random.choice([2, 3, 5, 7, 10, 14, 30])

    if status == "active":
        start_date = now - timedelta(days=random.randint(1, duration_days - 1))
        end_date = start_date + timedelta(days=duration_days)
    elif status == "overdue":
        end_date = now - timedelta(days=random.randint(1, 10))
        start_date = end_date - timedelta(days=duration_days)
    elif status in ["returned", "completed"]:
        days_ago = random.randint(15, 90)
        start_date = now - timedelta(days=days_ago)
        end_date = start_date + timedelta(days=duration_days)
    elif status in ["pending", "draft"]:
        start_date = now + timedelta(days=random.randint(1, 10))
        end_date = start_date + timedelta(days=duration_days)
    else:
        start_date = now - timedelta(days=random.randint(5, 20))
        end_date = start_date + timedelta(days=duration_days)

    return start_date, end_date


def generate_ref_no(prefix: str, index: int) -> str:
    """Generate structured reference strings e.g. INV-2026-00101."""
    return f"{prefix.upper()}-2026-{index:05d}"
