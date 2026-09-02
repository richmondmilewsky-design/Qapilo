"""
Iteration 40: Endless Practice Premium gating.

Covers:
- Non-Premium (trial ended, no sub) user -> GET /api/practice and
  POST /api/practice/complete return 403 with localized 'practice_pro' detail
  (en/de/es via Accept-Language).
- Premium user (active trial) -> both endpoints work (200) unchanged.
- Regression: /api/duels create/join still free for non-Premium users.
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

PRACTICE_PRO_MSG = {
    "en": "Endless Practice is a Premium feature.",
    "de": "Endloses Üben ist eine Premium-Funktion.",
    "es": "La práctica ilimitada es una función Premium.",
}


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def signup(api, email, password="TestPass123"):
    r = api.post(f"{BASE_URL}/api/auth/signup", json={"email": email, "password": password, "name": "Test User"})
    assert r.status_code == 200, r.text
    created_test_emails.append(email)
    data = r.json()
    return data["token"], data["user"]["user_id"]


def expire_trial(user_id):
    past = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
    started = (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
    db.users.update_one(
        {"user_id": user_id},
        {"$set": {"trial_ends_at": past, "trial_started_at": started, "pro_active": False}},
    )


@pytest.fixture(scope="module", autouse=True)
def cleanup():
    yield
    if created_test_emails:
        db.users.delete_many({"email": {"$in": created_test_emails}})


class TestPracticeGateNonPremium:
    def test_practice_get_403_after_trial_expired(self, api):
        email = f"TEST_free_{uuid.uuid4().hex[:8]}@example.com"
        token, uid = signup(api, email)
        expire_trial(uid)
        headers = {"Authorization": f"Bearer {token}"}

        me = api.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert me.status_code == 200
        assert me.json()["user"].get("is_pro") is False, f"expected is_pro False, got {me.json()}"

        r = api.get(f"{BASE_URL}/api/practice", headers=headers)
        assert r.status_code == 403, r.text
        assert r.json()["detail"] == PRACTICE_PRO_MSG["en"]

    def test_practice_complete_403_after_trial_expired(self, api):
        email = f"TEST_free2_{uuid.uuid4().hex[:8]}@example.com"
        token, uid = signup(api, email)
        expire_trial(uid)
        headers = {"Authorization": f"Bearer {token}"}

        body = {"correct": 1, "total": 1, "tier": 1}
        r = api.post(f"{BASE_URL}/api/practice/complete", headers=headers, json=body)
        assert r.status_code == 403, r.text
        assert r.json()["detail"] == PRACTICE_PRO_MSG["en"]

    @pytest.mark.parametrize("lang,expected_key", [("de", "de"), ("es", "es"), ("en", "en")])
    def test_practice_403_localized(self, api, lang, expected_key):
        email = f"TEST_free_lang_{lang}_{uuid.uuid4().hex[:8]}@example.com"
        token, uid = signup(api, email)
        expire_trial(uid)
        headers = {"Authorization": f"Bearer {token}", "Accept-Language": lang}
        r = api.get(f"{BASE_URL}/api/practice", headers=headers)
        assert r.status_code == 403
        assert r.json()["detail"] == PRACTICE_PRO_MSG[expected_key], r.json()

    def test_duels_still_free_for_non_premium(self, api):
        """Regression: duels must remain unaffected by the practice gate."""
        email = f"TEST_free_duel_{uuid.uuid4().hex[:8]}@example.com"
        token, uid = signup(api, email)
        expire_trial(uid)
        headers = {"Authorization": f"Bearer {token}"}
        r = api.post(f"{BASE_URL}/api/duels", headers=headers, json={})
        assert r.status_code == 200, r.text


class TestPracticeGatePremium:
    def test_practice_get_200_within_trial(self, api):
        email = f"TEST_pro_{uuid.uuid4().hex[:8]}@example.com"
        token, uid = signup(api, email)
        headers = {"Authorization": f"Bearer {token}"}

        me = api.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert me.status_code == 200
        assert me.json()["user"].get("is_pro") is True, f"expected fresh signup is_pro True (trial), got {me.json()}"

        r = api.get(f"{BASE_URL}/api/practice", headers=headers)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "questions" in data or "practice_level" in data, data

    def test_practice_complete_200_within_trial(self, api):
        email = f"TEST_pro2_{uuid.uuid4().hex[:8]}@example.com"
        token, uid = signup(api, email)
        headers = {"Authorization": f"Bearer {token}"}

        session = api.get(f"{BASE_URL}/api/practice", headers=headers)
        assert session.status_code == 200
        body = {"correct": 1, "total": 1, "tier": 1}
        r = api.post(f"{BASE_URL}/api/practice/complete", headers=headers, json=body)
        assert r.status_code == 200, r.text
