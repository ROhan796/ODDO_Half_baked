"""Unit tests for input validators."""
import pytest
from app.utils.validators import (
    validate_phone,
    validate_aadhaar,
    validate_pan,
    validate_gst,
    validate_pincode,
    validate_ifsc,
    validate_email_format,
)


class TestValidatePhone:
    def test_valid_phones(self):
        assert validate_phone("9876543210") is True
        assert validate_phone("6000000000") is True
        assert validate_phone("8888888888") is True
        assert validate_phone("7000000000") is True

    def test_invalid_phones(self):
        assert validate_phone("1234567890") is False  # starts with 1
        assert validate_phone("5678901234") is False  # starts with 5
        assert validate_phone("987654321") is False   # 9 digits
        assert validate_phone("98765432100") is False # 11 digits
        assert validate_phone("abcdefghij") is False   # letters
        assert validate_phone("") is False              # empty
        assert validate_phone("98765-43210") is False  # contains dash


class TestValidateAadhaar:
    def test_valid_aadhaar(self):
        assert validate_aadhaar("123456789012") is True
        assert validate_aadhaar("000000000000") is True
        assert validate_aadhaar("999999999999") is True

    def test_invalid_aadhaar(self):
        assert validate_aadhaar("12345678901") is False   # 11 digits
        assert validate_aadhaar("1234567890123") is False # 13 digits
        assert validate_aadhaar("1234567890a") is False   # contains letter
        assert validate_aadhaar("") is False               # empty
        assert validate_aadhaar("1234-5678-9012") is False # contains dash


class TestValidatePAN:
    def test_valid_pan(self):
        assert validate_pan("ABCDE1234F") is True
        assert validate_pan("AAAAA0000A") is True
        assert validate_pan("abcde1234f") is True  # case insensitive

    def test_invalid_pan(self):
        assert validate_pan("ABCDEF1234") is False  # 6th char must be digit
        assert validate_pan("ABCD12345F") is False   # first 5 must be letters
        assert validate_pan("ABCDE12345") is False   # last char must be letter
        assert validate_pan("ABCD1234") is False      # too short
        assert validate_pan("ABCDE12345F") is False  # too long
        assert validate_pan("12345ABCDE") is False    # starts with digits


class TestValidateGST:
    def test_valid_gst(self):
        assert validate_gst("27AAPFU0939F1ZV") is True
        assert validate_gst("07AAACG0846C1Z2") is True

    def test_invalid_gst(self):
        assert validate_gst("27AAPFU0939F1Z") is False   # too short
        assert validate_gst("27AAPFU0939F1ZVK") is False # too long
        assert validate_gst("12345678901234") is False    # all digits
        assert validate_gst("") is False                   # empty
        assert validate_gst("27AAPFU093F1ZV") is False   # wrong format


class TestValidatePincode:
    def test_valid_pincode(self):
        assert validate_pincode("110001") is True
        assert validate_pincode("400001") is True
        assert validate_pincode("000000") is True

    def test_invalid_pincode(self):
        assert validate_pincode("12345") is False   # 5 digits
        assert validate_pincode("1234567") is False # 7 digits
        assert validate_pincode("12345a") is False  # contains letter


class TestValidateIFSC:
    def test_valid_ifsc(self):
        assert validate_ifsc("SBIN0001234") is True
        assert validate_ifsc("HDFC0001234") is True
        assert validate_ifsc("sbin0001234") is True  # case insensitive

    def test_invalid_ifsc(self):
        assert validate_ifsc("SBIN1234") is False     # too short
        assert validate_ifsc("SBIN00012345") is False # too long
        assert validate_ifsc("12340001234") is False   # starts with digit


class TestValidateEmail:
    def test_valid_email(self):
        assert validate_email_format("user@example.com") is True
        assert validate_email_format("test.user@domain.co.in") is True
        assert validate_email_format("a+b@c.com") is True

    def test_invalid_email(self):
        assert validate_email_format("userexample.com") is False  # no @
        assert validate_email_format("@example.com") is False     # no local part
        assert validate_email_format("user@") is False            # no domain
        assert validate_email_format("") is False                 # empty
        assert validate_email_format("user@.com") is False        # dot at start of domain
