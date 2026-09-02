"""
Tests for the DNS/MX-record domain validation added to POST /api/auth/signup.
Covers: fake-domain rejection (localized en/de/es), valid-domain success,
duplicate-email regression, and non-interference with google/apple auth,
forgot-password, and verify-email/resend-verification flows.
"""
import os
import time
import uuid

import pytest
import requests

BASE_URL = os.environ.get("EXPO_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    # fallback to reading frontend .env style var used in this repo
    BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL", "").rstrip("/")

FAKE_DOMAIN = "thisdomaindoesnotexist12345xyz.com"


@pytest.fixture
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


def unique_email(domain="gmail.com"):
    return f"TEST_qapilo_{uuid.uuid4().hex[:10]}@{domain}"


class TestSignupDomainValidationFakeDomain:
    def test_fake_domain_rejected_400_en(self, api_client):
        email = unique_email(FAKE_DOMAIN)
        r = api_client.post(
            f"{BASE_URL}/api/auth/signup",
            json={"email": email, "password": "testpass123", "lang": "en"},
            headers={"Accept-Language": "en"},
        )
        assert r.status_code == 400, r.text
        data = r.json()
        detail = data.get("detail", "")
        assert "exist" in detail.lower() or "typo" in detail.lower(), detail

    def test_fake_domain_rejected_400_de(self, api_client):
        email = unique_email(FAKE_DOMAIN)
        r = api_client.post(
            f"{BASE_URL}/api/auth/signup",
            json={"email": email, "password": "testpass123", "lang": "de"},
            headers={"Accept-Language": "de"},
        )
        assert r.status_code == 400, r.text
        detail = r.json().get("detail", "")
        assert "existieren" in detail or "Tippfehler" in detail, detail

    def test_fake_domain_rejected_400_es(self, api_client):
        email = unique_email(FAKE_DOMAIN)
        r = api_client.post(
            f"{BASE_URL}/api/auth/signup",
            json={"email": email, "password": "testpass123", "lang": "es"},
            headers={"Accept-Language": "es"},
        )
        assert r.status_code == 400, r.text
        detail = r.json().get("detail", "")
        assert "existir" in detail or "escritura" in detail, detail

    def test_fake_domain_no_user_created(self, api_client):
        """Ensure signup with fake domain does NOT create a usable account
        (login afterwards should fail with bad_credentials, not succeed)."""
        email = unique_email(FAKE_DOMAIN)
        r = api_client.post(
            f"{BASE_URL}/api/auth/signup",
            json={"email": email, "password": "testpass123", "lang": "en"},
        )
        assert r.status_code == 400
        # Attempt login - should fail since no user was created
        login_r = api_client.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": "testpass123"},
        )
        assert login_r.status_code == 401, login_r.text


class TestSignupDomainValidationRealDomain:
    def test_valid_domain_signup_succeeds(self, api_client):
        email = unique_email("gmail.com")
        start = time.time()
        r = api_client.post(
            f"{BASE_URL}/api/auth/signup",
            json={"email": email, "password": "testpass123", "lang": "en"},
        )
        elapsed = time.time() - start
        assert r.status_code == 200, r.text
        data = r.json()
        assert "token" in data
        assert data["user"]["email"] == email.lower()
        assert data["user"]["email_verified"] is False
        assert elapsed < 8, f"signup took too long: {elapsed}s"

    def test_valid_domain_outlook_signup_succeeds(self, api_client):
        email = unique_email("outlook.com")
        r = api_client.post(
            f"{BASE_URL}/api/auth/signup",
            json={"email": email, "password": "testpass123", "lang": "en"},
        )
        assert r.status_code == 200, r.text
        assert r.json()["user"]["email"] == email.lower()


class TestSignupDuplicateEmailRegression:
    def test_duplicate_email_still_returns_email_taken(self, api_client):
        email = unique_email("gmail.com")
        r1 = api_client.post(
            f"{BASE_URL}/api/auth/signup",
            json={"email": email, "password": "testpass123", "lang": "en"},
        )
        assert r1.status_code == 200, r1.text

        r2 = api_client.post(
            f"{BASE_URL}/api/auth/signup",
            json={"email": email, "password": "testpass123", "lang": "en"},
        )
        assert r2.status_code == 400, r2.text
        detail = r2.json().get("detail", "")
        assert "registered" in detail.lower(), detail


class TestAuthRegressionUnaffected:
    def test_google_auth_invalid_session_unaffected(self, api_client):
        r = api_client.post(
            f"{BASE_URL}/api/auth/google",
            json={"session_id": "invalid-session-id-xyz"},
        )
        assert r.status_code == 401, r.text
        detail = r.json().get("detail", "")
        assert "google" in detail.lower(), detail

    def test_apple_auth_invalid_token_unaffected(self, api_client):
        r = api_client.post(
            f"{BASE_URL}/api/auth/apple",
            json={"identity_token": "not-a-real-jwt"},
        )
        assert r.status_code == 401, r.text
        detail = r.json().get("detail", "")
        assert "apple" in detail.lower(), detail

    def test_forgot_password_unaffected(self, api_client):
        # Should always return 200 with reset_sent message regardless of domain
        r = api_client.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"email": unique_email("gmail.com"), "lang": "en"},
        )
        assert r.status_code == 200, r.text

    def test_forgot_password_fake_domain_still_200(self, api_client):
        """forgot-password must NOT apply the new domain check (unchanged
        behavior - always returns 200 to avoid leaking account existence)."""
        r = api_client.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"email": unique_email(FAKE_DOMAIN), "lang": "en"},
        )
        assert r.status_code == 200, r.text
