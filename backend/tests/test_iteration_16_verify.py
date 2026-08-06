"""Iteration 16 — email verification & biometric-related backend regression."""
import os
import time
import uuid
import pytest
import requests
from pymongo import MongoClient

BASE = os.environ.get("EXPO_BACKEND_URL", "").rstrip("/")
assert BASE, "EXPO_BACKEND_URL must be set"
API = f"{BASE}/api"

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")


@pytest.fixture(scope="module")
def db():
    return MongoClient(MONGO_URL)[DB_NAME]


@pytest.fixture(scope="module")
def fresh_user():
    email = f"TEST_verify_{uuid.uuid4().hex[:10]}@example.com"
    r = requests.post(f"{API}/auth/signup", json={
        "email": email, "password": "Abc123!xyz", "name": "Verify Tester", "lang": "en"
    })
    assert r.status_code == 200, r.text
    data = r.json()
    return {"token": data["token"], "user": data["user"], "email": email}


@pytest.fixture(scope="module")
def demo_user():
    r = requests.post(f"{API}/auth/login", json={
        "email": "demo@tradequest.app", "password": "demo123"
    })
    if r.status_code != 200:
        pytest.skip(f"demo login not available: {r.text}")
    return {"token": r.json()["token"], "user": r.json()["user"]}


# --- Signup returns email_verified=false ---
class TestSignupVerification:
    def test_signup_response_has_email_verified_false(self, fresh_user):
        assert fresh_user["user"]["email_verified"] is False
        assert fresh_user["user"]["email"] == fresh_user["email"].lower()

    def test_me_returns_email_verified_false(self, fresh_user):
        r = requests.get(f"{API}/auth/me",
                         headers={"Authorization": f"Bearer {fresh_user['token']}"})
        assert r.status_code == 200
        assert r.json()["user"]["email_verified"] is False

    def test_email_event_recorded(self, fresh_user, db):
        # send_and_log runs as background task; give it a moment
        time.sleep(2.5)
        uid = fresh_user["user"]["user_id"]
        ev = db.email_events.find_one(
            {"user_ref": uid, "template": "email_verification"})
        assert ev is not None, "no email_verification event logged"
        assert ev["status"] in ("sent", "failed"), ev.get("status")
        # even on provider failure the event must be recorded
        # verify a code hash record exists in email_verifications
        rec = db.email_verifications.find_one({"user_id": uid})
        assert rec is not None
        assert "code_hash" in rec and "expires_at" in rec


# --- verify-email negative path ---
class TestVerifyEmail:
    def test_wrong_code_returns_400_localized(self, fresh_user):
        r = requests.post(
            f"{API}/auth/verify-email",
            json={"code": "000000", "lang": "en"},
            headers={"Authorization": f"Bearer {fresh_user['token']}",
                     "Accept-Language": "en"},
        )
        # 000000 has vanishingly small chance to match the real code (1e-6),
        # accept 400; if by cosmic accident it matched, skip.
        if r.status_code == 200:
            pytest.skip("random 000000 happened to match the real code")
        assert r.status_code == 400
        detail = r.json().get("detail", "")
        assert "invalid" in detail.lower() or "expired" in detail.lower()

    def test_wrong_code_de_localized(self, fresh_user):
        r = requests.post(
            f"{API}/auth/verify-email",
            json={"code": "111111", "lang": "de"},
            headers={"Authorization": f"Bearer {fresh_user['token']}",
                     "Accept-Language": "de"},
        )
        if r.status_code == 200:
            pytest.skip("random code matched")
        assert r.status_code == 400
        detail = r.json().get("detail", "")
        # German verify_invalid message
        assert "ungültig" in detail.lower() or "abgelaufen" in detail.lower()

    def test_verify_requires_auth(self):
        r = requests.post(f"{API}/auth/verify-email",
                          json={"code": "123456", "lang": "en"})
        assert r.status_code == 401


# --- resend-verification ---
class TestResendVerification:
    def test_resend_ok(self, fresh_user):
        r = requests.post(
            f"{API}/auth/resend-verification",
            json={"lang": "en"},
            headers={"Authorization": f"Bearer {fresh_user['token']}"},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("ok") is True

    def test_resend_rate_limit(self, fresh_user):
        # Already called once above => quota is 3/15min. Two more should still be OK,
        # 4th should be 429.
        headers = {"Authorization": f"Bearer {fresh_user['token']}"}
        # 2nd and 3rd
        for _ in range(2):
            r = requests.post(f"{API}/auth/resend-verification",
                              json={"lang": "en"}, headers=headers)
            assert r.status_code == 200, r.text
        # 4th -> 429
        r = requests.post(f"{API}/auth/resend-verification",
                          json={"lang": "en"}, headers=headers)
        assert r.status_code == 429, r.text

    def test_resend_verified_user_is_ok(self, demo_user):
        # demo user is treated as verified (email_verified default True)
        r = requests.post(
            f"{API}/auth/resend-verification",
            json={"lang": "en"},
            headers={"Authorization": f"Bearer {demo_user['token']}"},
        )
        assert r.status_code == 200
        assert r.json().get("ok") is True


# --- Regression on unrelated endpoints ---
class TestRegression:
    def test_demo_login_and_me(self, demo_user):
        assert demo_user["user"]["email_verified"] is True
        r = requests.get(f"{API}/auth/me",
                         headers={"Authorization": f"Bearer {demo_user['token']}"})
        assert r.status_code == 200
        assert r.json()["user"]["email_verified"] is True

    def test_google_invalid_session(self):
        r = requests.post(f"{API}/auth/google",
                          json={"session_id": "invalid-session-xyz"})
        assert r.status_code == 401

    def test_apple_invalid_token(self):
        r = requests.post(f"{API}/auth/apple",
                          json={"identity_token": "not-a-real-jwt"})
        assert r.status_code == 401
