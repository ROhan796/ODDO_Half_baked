# app/utils/validators.py
import re
from typing import Optional


def validate_phone(phone: str) -> bool:
    """Validate Indian phone number."""
    pattern = r"^[6-9]\d{9}$"
    return bool(re.match(pattern, phone))


def validate_aadhaar(aadhaar: str) -> bool:
    """Validate Aadhaar number (12 digits)."""
    pattern = r"^\d{12}$"
    return bool(re.match(pattern, aadhaar))


def validate_pan(pan: str) -> bool:
    """Validate PAN number."""
    pattern = r"^[A-Z]{5}\d{4}[A-Z]$"
    return bool(re.match(pattern, pan.upper()))


def validate_gst(gst: str) -> bool:
    """Validate GST number."""
    pattern = r"^\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z][A-Z\d]$"
    return bool(re.match(pattern, gst.upper()))


def validate_pincode(pincode: str) -> bool:
    """Validate Indian pincode (6 digits)."""
    pattern = r"^\d{6}$"
    return bool(re.match(pattern, pincode))


def validate_ifsc(ifsc: str) -> bool:
    """Validate IFSC code."""
    pattern = r"^[A-Z]{4}0[A-Z0-9]{6}$"
    return bool(re.match(pattern, ifsc.upper()))


def sanitize_string(value: str) -> str:
    """Sanitize string input."""
    return value.strip()


def validate_email_format(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))
