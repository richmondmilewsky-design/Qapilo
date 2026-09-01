"""
Iteration 34: Tests for compute_pro() self-heal fix for missing/corrupt trial_ends_at,
and FREE_LEVEL_LIMIT change from 40 -> 60.

Covers:
- Self-heal backfills trial_started_at/trial_ends_at (in DB) when trial_ends_at missing/corrupt,
  no sub history, pro_active=false -> trial_status='active', is_pro=true, trial_end_reason=None.
- Genuinely expired trial (past trial_ends_at) is NOT self-healed -> trial_status='ended', reason='time'.
- User with subscription history + missing trial_ends_at is NOT self-healed -> stays 'ended'.
- FREE_LEVEL_LIMIT == 60: level 55 active user is_pro=true; level 61 user trial_end_reason='level', is_pro=false.
- free_level_limit field in response == 60.
- Regression: normal signup gets trial fields immediately; pro/subscribed user shows 'premium'.
"""
import os
import time
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


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def signup(api, level_xp=0, password="TestPass123!"):
    """Sign up a new user via normal endpoint, return (token, user_id, email)."""
    email = f"TEST_trial_{uuid.uuid4().hex[:10]}@example.com"
    created_test_emails.append(email)
    resp = api.post(f"{BASE_URL}/api/auth/signup", json={
        "email": email, "password": password, "name": "Trial Test User"
    })
    assert resp.status_code in (200, 201), f"signup failed: {resp.status_code} {resp.text}"
    data = resp.json()
    token = data["token"] if "token" in data else data.get("access_token")
    user = data.get("user") or data.get("public_user") or {}
    user_id = user.get("user_id")
    if level_xp:
        db.users.update_one({"user_id": user_id}, {"$set": {"xp": level_xp}})
    return token, user_id, email


def get_me(api, token):
    r = api.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    return r


def me_body(resp):
    """/api/auth/me wraps public_user() under 'user' key."""
    data = resp.json()
    return data.get("user", data)


class TestSelfHealMissingTrialEndsAt:
    """Scenario 1+2: missing/corrupt trial_ends_at, no sub history -> self-heal."""

    @pytest.mark.parametrize("corrupt_value", [None, "invalid", "__UNSET__"])
    def test_selfheal_active_and_persisted(self, api, corrupt_value):
        token, user_id, email = signup(api, level_xp=100)  # low level, well below 60
        # Corrupt/remove trial_ends_at directly in DB
        if corrupt_value == "__UNSET__":
            db.users.update_one({"user_id": user_id}, {"$unset": {"trial_ends_at": "", "trial_started_at": ""}})
        else:
            db.users.update_one({"user_id": user_id}, {"$set": {"trial_ends_at": corrupt_value}})
        # sanity: confirm corruption applied
        doc = db.users.find_one({"user_id": user_id})
        assert doc.get("trial_ends_at") == (None if corrupt_value in (None, "__UNSET__") else corrupt_value)

        resp = get_me(api, token)
        assert resp.status_code == 200, resp.text
        body = me_body(resp)
        assert body["trial_status"] == "active", f"Expected active, got {body}"
        assert body["is_pro"] is True
        assert body["trial_end_reason"] is None
        assert 28 <= body["trial_days_left"] <= 31, body["trial_days_left"]

        # Confirm persisted in Mongo (self-heal write)
        doc2 = db.users.find_one({"user_id": user_id})
        assert doc2.get("trial_ends_at") is not None
        assert doc2.get("trial_started_at") is not None
        parsed_end = datetime.fromisoformat(doc2["trial_ends_at"])
        assert parsed_end > datetime.now(timezone.utc)

        # Second call: should survive/stay active with persisted values (no reheal drift)
        resp2 = get_me(api, token)
        body2 = me_body(resp2)
        assert body2["trial_status"] == "active"
        assert body2["trial_ends_at"] == doc2["trial_ends_at"], "trial_ends_at should not change/re-heal on 2nd call"


class TestGenuinelyExpiredTrialNotHealed:
    """Scenario 3: genuinely expired trial_ends_at must stay ended (not self-healed)."""

    def test_expired_trial_stays_ended(self, api):
        token, user_id, email = signup(api, level_xp=100)
        now = datetime.now(timezone.utc)
        db.users.update_one({"user_id": user_id}, {"$set": {
            "trial_started_at": (now - timedelta(days=70)).isoformat(),
            "trial_ends_at": (now - timedelta(days=40)).isoformat(),
        }})
        resp = get_me(api, token)
        assert resp.status_code == 200
        body = me_body(resp)
        assert body["trial_status"] == "ended", body
        assert body["trial_end_reason"] == "time", body
        assert body["is_pro"] is False


class TestSubHistoryExcludedFromSelfHeal:
    """Scenario 4: missing trial_ends_at but has subscription history -> no self-heal."""

    def test_sub_history_stays_ended_not_healed(self, api):
        token, user_id, email = signup(api, level_xp=100)
        db.users.update_one({"user_id": user_id}, {"$unset": {"trial_ends_at": "", "trial_started_at": ""},
                                                     "$set": {"subscription_status": "CANCELLED", "pro_active": False}})
        resp = get_me(api, token)
        assert resp.status_code == 200
        body = me_body(resp)
        assert body["trial_status"] == "ended", f"Expected ended (no self-heal for sub history), got {body}"
        assert body["is_pro"] is False

        # Confirm DB was NOT backfilled with a new trial window
        doc = db.users.find_one({"user_id": user_id})
        assert doc.get("trial_ends_at") is None, "self-heal must not apply to users with subscription history"


class TestFreeLevelLimit60:
    """Scenario 5: FREE_LEVEL_LIMIT is 60 now (was 40)."""

    def test_level_55_active_previously_blocked_at_40(self, api):
        # level 55 -> xp in [5400,5499]
        token, user_id, email = signup(api, level_xp=5450)
        resp = get_me(api, token)
        body = me_body(resp)
        assert body["current_level"] == 55, body
        assert body["trial_status"] == "active", f"level 55 should be active under new limit 60: {body}"
        assert body["is_pro"] is True
        assert body["free_level_limit"] == 60

    def test_level_61_blocked_by_level_reason(self, api):
        # level 61 -> xp in [6000,6099]
        token, user_id, email = signup(api, level_xp=6050)
        resp = get_me(api, token)
        body = me_body(resp)
        assert body["current_level"] == 61, body
        assert body["trial_end_reason"] == "level", body
        assert body["is_pro"] is False
        assert body["free_level_limit"] == 60


class TestRegressionNewSignup:
    """Scenario 6: brand-new signup gets trial fields set immediately, no self-heal path needed."""

    def test_new_signup_gets_trial_immediately(self, api):
        token, user_id, email = signup(api)
        doc = db.users.find_one({"user_id": user_id})
        assert doc.get("trial_ends_at") is not None
        assert doc.get("trial_started_at") is not None
        resp = get_me(api, token)
        body = me_body(resp)
        assert body["trial_status"] == "active"
        assert body["is_pro"] is True
        assert body["pro_source"] == "trial"


class TestRegressionProSubscribed:
    """Scenario 7: pro_active=true user shows 'premium' regardless of trial fields."""

    def test_pro_active_user_shows_premium(self, api):
        token, user_id, email = signup(api, level_xp=100)
        db.users.update_one({"user_id": user_id}, {"$set": {"pro_active": True, "subscription_status": "ACTIVE"}})
        resp = get_me(api, token)
        body = me_body(resp)
        assert body["trial_status"] == "premium", body
        assert body["is_pro"] is True
        assert body["pro_source"] == "subscription"


class TestRegressionOtherEndpoints:
    """Scenario 8: /api/practice and /api/progress still work and are consistent with /auth/me."""

    def test_practice_and_progress_consistent(self, api):
        token, user_id, email = signup(api, level_xp=100)
        headers = {"Authorization": f"Bearer {token}"}
        me = me_body(api.get(f"{BASE_URL}/api/auth/me", headers=headers))

        r_practice = api.get(f"{BASE_URL}/api/practice", headers=headers)
        assert r_practice.status_code == 200, r_practice.text

        r_progress = api.get(f"{BASE_URL}/api/progress", headers=headers)
        if r_progress.status_code == 200:
            prog = r_progress.json()
            if "is_pro" in prog:
                assert prog["is_pro"] == me["is_pro"]
            if "free_level_limit" in prog:
                assert prog["free_level_limit"] == 60


@pytest.fixture(scope="module", autouse=True)
def cleanup_test_users():
    yield
    if created_test_emails:
        result = db.users.delete_many({"email": {"$in": created_test_emails}})
        print(f"Cleaned up {result.deleted_count} test users")
