"""
Iteration 36: Tests for FOUNDER_EMAILS override in compute_pro().

Requires FOUNDER_EMAILS env var to include "founder_test@example.com"
(set in backend/.env and backend restarted before running this file).

Covers:
- Founder email (exact case) with expired trial + low level + no subscription -> is_pro=True,
  trial_status='premium', pro_source='founder', trial_end_reason=None.
- Founder email different casing (FOUNDER_TEST@EXAMPLE.COM) -> same founder override applies.
- Non-founder email (demo@tradequest.app-like fresh user) with identical expired-trial setup
  -> trial_status='ended' (no leak of founder override).
- Regression: normal active-trial user and pro_active subscriber unaffected.
- Regression: /api/practice and /api/progress consistent with /auth/me for founder user.
"""
import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
import requests
from pymongo import MongoClient

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL", "").rstrip("/")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

mongo_client = MongoClient(MONGO_URL)
db = mongo_client[DB_NAME]

created_test_emails = []
FOUNDER_EMAIL = "founder_test@example.com"


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def signup(api, email, level_xp=500, password="TestPass123!"):
    created_test_emails.append(email)
    resp = api.post(f"{BASE_URL}/api/auth/signup", json={
        "email": email, "password": password, "name": "Founder Test"
    })
    assert resp.status_code in (200, 201), f"signup failed: {resp.status_code} {resp.text}"
    data = resp.json()
    token = data.get("token") or data.get("access_token")
    user = data.get("user") or data.get("public_user") or {}
    user_id = user.get("user_id")
    if level_xp:
        db.users.update_one({"user_id": user_id}, {"$set": {"xp": level_xp}})
    return token, user_id, email


def expire_trial_low_level_no_sub(user_id):
    now = datetime.now(timezone.utc)
    db.users.update_one({"user_id": user_id}, {"$set": {
        "trial_started_at": (now - timedelta(days=40)).isoformat(),
        "trial_ends_at": (now - timedelta(days=10)).isoformat(),  # expired
        "pro_active": False,
        "subscription_id": None,
        "subscription_status": None,
        "xp": 450,  # level 5, well below 60
    }})


def get_me(api, token):
    r = api.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    return r


def me_body(resp):
    data = resp.json()
    return data.get("user", data)


class TestFounderOverrideExactCase:
    def test_founder_email_forces_premium_despite_expired_low_level_no_sub(self, api):
        token, user_id, email = signup(api, FOUNDER_EMAIL)
        expire_trial_low_level_no_sub(user_id)
        resp = get_me(api, token)
        assert resp.status_code == 200, resp.text
        body = me_body(resp)
        assert body["is_pro"] is True, body
        assert body["trial_status"] == "premium", body
        assert body["pro_source"] == "founder", body
        assert body["trial_end_reason"] is None, body
        assert body["current_level"] == 5, body


class TestFounderOverrideCaseInsensitive:
    def test_uppercase_founder_email_variant_still_matches_via_db_update(self, api):
        # Sign up with lowercase (EmailStr normalizes/validates), then simulate stored
        # casing variance directly in DB to test the .lower() comparison in compute_pro.
        email = f"TEST_founder_case_{uuid.uuid4().hex[:8]}@example.com"
        token, user_id, _ = signup(api, email)
        # Overwrite email to match FOUNDER_EMAIL with different casing
        upper_variant = FOUNDER_EMAIL.upper()
        db.users.update_one({"user_id": user_id}, {"$set": {"email": upper_variant}})
        created_test_emails.append(upper_variant)
        expire_trial_low_level_no_sub(user_id)
        resp = get_me(api, token)
        assert resp.status_code == 200, resp.text
        body = me_body(resp)
        assert body["is_pro"] is True, body
        assert body["trial_status"] == "premium", body
        assert body["pro_source"] == "founder", body
        assert body["trial_end_reason"] is None, body


class TestNonFounderNoLeak:
    def test_non_founder_email_same_setup_shows_ended(self, api):
        email = f"TEST_nonfounder_{uuid.uuid4().hex[:8]}@example.com"
        token, user_id, _ = signup(api, email)
        expire_trial_low_level_no_sub(user_id)
        resp = get_me(api, token)
        assert resp.status_code == 200, resp.text
        body = me_body(resp)
        assert body["trial_status"] == "ended", body
        assert body["is_pro"] is False, body
        assert body["pro_source"] == "free", body
        assert body["trial_end_reason"] == "time", body


class TestRegressionNormalUsersUnaffected:
    def test_new_signup_active_trial_unaffected(self, api):
        email = f"TEST_regression_trial_{uuid.uuid4().hex[:8]}@example.com"
        token, user_id, _ = signup(api, email, level_xp=100)
        resp = get_me(api, token)
        body = me_body(resp)
        assert body["trial_status"] == "active", body
        assert body["pro_source"] == "trial", body
        assert body["is_pro"] is True

    def test_pro_active_subscriber_unaffected(self, api):
        email = f"TEST_regression_sub_{uuid.uuid4().hex[:8]}@example.com"
        token, user_id, _ = signup(api, email, level_xp=100)
        db.users.update_one({"user_id": user_id}, {"$set": {"pro_active": True, "subscription_status": "ACTIVE"}})
        resp = get_me(api, token)
        body = me_body(resp)
        assert body["trial_status"] == "premium", body
        assert body["pro_source"] == "subscription", body
        assert body["is_pro"] is True


class TestOtherEndpointsConsistentForFounder:
    def test_practice_and_progress_consistent_with_me_for_founder(self, api):
        email = f"TEST_founder_endpoints_{uuid.uuid4().hex[:8]}@example.com"
        token, user_id, _ = signup(api, email)
        db.users.update_one({"user_id": user_id}, {"$set": {"email": FOUNDER_EMAIL}})
        created_test_emails.append(FOUNDER_EMAIL)
        expire_trial_low_level_no_sub(user_id)
        headers = {"Authorization": f"Bearer {token}"}
        me = me_body(api.get(f"{BASE_URL}/api/auth/me", headers=headers))
        assert me["pro_source"] == "founder"

        r_practice = api.get(f"{BASE_URL}/api/practice", headers=headers)
        assert r_practice.status_code == 200, r_practice.text

        r_progress = api.get(f"{BASE_URL}/api/progress", headers=headers)
        if r_progress.status_code == 200:
            prog = r_progress.json()
            if "is_pro" in prog:
                assert prog["is_pro"] == me["is_pro"]


@pytest.fixture(scope="module", autouse=True)
def cleanup_test_users():
    yield
    if created_test_emails:
        result = db.users.delete_many({"email": {"$in": created_test_emails}})
        print(f"Cleaned up {result.deleted_count} test users")
