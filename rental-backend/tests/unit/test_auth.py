"""Unit tests for authentication utilities."""
import pytest
from app.core.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
    generate_otp,
    create_refresh_token,
    hash_token,
)


class TestPasswordHashing:
    def test_hash_password_returns_string(self):
        result = hash_password("mypassword")
        assert isinstance(result, str)

    def test_hash_password_is_different_each_time(self):
        h1 = hash_password("mypassword")
        h2 = hash_password("mypassword")
        assert h1 != h2

    def test_verify_password_correct(self):
        password = "securepass123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        hashed = hash_password("correctpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_verify_password_empty_string(self):
        hashed = hash_password("password")
        assert verify_password("", hashed) is False


class TestAccessToken:
    def test_create_access_token_returns_string(self):
        token = create_access_token("user-123", "super_admin", "personal")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_valid_token(self):
        user_id = "user-456"
        role = "ops_admin"
        user_type = "enterprise"
        token = create_access_token(user_id, role, user_type)
        payload = verify_access_token(token)
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["role"] == role
        assert payload["user_type"] == user_type

    def test_verify_invalid_token(self):
        payload = verify_access_token("invalid.token.here")
        assert payload is None

    def test_verify_tampered_token(self):
        token = create_access_token("user-789", "field_agent", "personal")
        tampered = token[:-5] + "XXXXX"
        payload = verify_access_token(tampered)
        assert payload is None

    def test_token_contains_jti(self):
        token = create_access_token("user-000", "super_admin", "personal")
        payload = verify_access_token(token)
        assert "jti" in payload
        assert len(payload["jti"]) > 0

    def test_token_contains_expiry(self):
        token = create_access_token("user-000", "super_admin", "personal")
        payload = verify_access_token(token)
        assert "exp" in payload
        assert "iat" in payload


class TestOTP:
    def test_generate_otp_returns_6_digits(self):
        otp = generate_otp()
        assert len(otp) == 6
        assert otp.isdigit()

    def test_generate_otp_is_random(self):
        otps = {generate_otp() for _ in range(100)}
        assert len(otps) > 1

    def test_generate_otp_within_range(self):
        for _ in range(50):
            otp = generate_otp()
            assert 0 <= int(otp) <= 999999


class TestRefreshToken:
    def test_create_refresh_token_returns_hex_string(self):
        token = create_refresh_token()
        assert isinstance(token, str)
        int(token, 16)  # Should not raise

    def test_refresh_tokens_are_unique(self):
        t1 = create_refresh_token()
        t2 = create_refresh_token()
        assert t1 != t2

    def test_hash_token_deterministic(self):
        token = "abc123"
        h1 = hash_token(token)
        h2 = hash_token(token)
        assert h1 == h2

    def test_hash_token_different_inputs(self):
        h1 = hash_token("token1")
        h2 = hash_token("token2")
        assert h1 != h2
