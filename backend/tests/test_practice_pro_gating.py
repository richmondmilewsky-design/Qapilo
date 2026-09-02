"""
Tests for stricter Endless Practice gating (iteration): GET /api/practice and
POST /api/practice/complete now require pro_active=true OR founder-override,
NOT just an active trial (compute_pro().is_pro). Premium lesson (PRO_UNITS)
gating is UNCHANGED and must remain trial-accessible.
"""
import os
import time
import uuid

import pytest
import requests
from pymongo import MongoClient

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL", os.environ.get("EXPO_BACKEND_URL")).rstrip("/")
MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")

FOUNDER_EMAILS = [
    e.strip().lower()
    for e in os.environ.get("FOUNDER_EMAILS", "").split(",")
    if e.strip()
]


@pytest.fixture(scope="module")
def mongo_db():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    yield db
    client.close()


@pytest.fixture
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


def signup_new_user(api_client, email_prefix="TEST_practice"):
    email = f"{email_prefix}_{uuid.uuid4().hex[:10]}@gmail.com".lower()
    password = "TestPass123"
    resp = api_client.post(
        f"{BASE_URL}/api/auth/signup",
        json={"email": email, "password": password, "name": "Practice Tester"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    token = data["token"]
    api_client.headers.update({"Authorization": f"Bearer {token}"})
    return email, password, token, data["user"]


class TestTrialUserBlockedFromPractice:
    """A fresh trial user (pro_active=false, not founder) is_pro=true via trial
    must now get 403 from practice endpoints (regression from prior behavior)."""

    def test_trial_user_get_practice_403(self, api_client, mongo_db):
        email, _, token, user = signup_new_user(api_client)
        # sanity: user is on trial and NOT pro_active
        db_user = mongo_db.users.find_one({"email": email})
        assert db_user is not None
        assert db_user.get("pro_active", False) is False
        assert email.lower() not in FOUNDER_EMAILS

        # verify via /auth/me that is_pro is true (trial) - general gate unaffected
        me = api_client.get(f"{BASE_URL}/api/auth/me")
        assert me.status_code == 200
        me_data = me.json()
        assert me_data["user"]["is_pro"] is True
        assert me_data["user"]["pro_source"] == "trial"

        resp = api_client.get(f"{BASE_URL}/api/practice")
        assert resp.status_code == 403, resp.text
        body = resp.json()
        assert "detail" in body

        # cleanup
        mongo_db.users.delete_one({"email": email})

    def test_trial_user_post_practice_complete_403(self, api_client, mongo_db):
        email, _, token, user = signup_new_user(api_client)
        resp = api_client.post(
            f"{BASE_URL}/api/practice/complete",
            json={"correct": 4, "total": 5, "tier": 1, "lang": "en"},
        )
        assert resp.status_code == 403, resp.text
        mongo_db.users.delete_one({"email": email})


class TestSubscribedUserAllowedPractice:
    """pro_active=true (real subscription) must return 200 regardless of trial status."""

    def test_pro_active_user_get_practice_200(self, api_client, mongo_db):
        email, _, token, user = signup_new_user(api_client, "TEST_practice_sub")
        mongo_db.users.update_one({"email": email}, {"$set": {"pro_active": True}})

        resp = api_client.get(f"{BASE_URL}/api/practice")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "questions" in data
        assert isinstance(data["questions"], list)
        assert len(data["questions"]) > 0
        assert "reward_xp" in data

        mongo_db.users.delete_one({"email": email})

    def test_pro_active_user_post_practice_complete_200(self, api_client, mongo_db):
        email, _, token, user = signup_new_user(api_client, "TEST_practice_sub2")
        mongo_db.users.update_one({"email": email}, {"$set": {"pro_active": True}})

        resp = api_client.post(
            f"{BASE_URL}/api/practice/complete",
            json={"correct": 4, "total": 5, "tier": 1, "lang": "en"},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "earned_xp" in data
        assert data["earned_xp"] > 0
        assert "user" in data

        mongo_db.users.delete_one({"email": email})


@pytest.mark.skipif(not FOUNDER_EMAILS, reason="No FOUNDER_EMAILS configured in backend/.env")
class TestFounderOverride:
    """Founder-email users must get 200 from practice endpoints even with pro_active=false."""

    def test_founder_practice_access(self, api_client, mongo_db):
        founder_email = FOUNDER_EMAILS[0]
        password = "FounderTestPass123"
        # Try signup; if already exists, log in instead.
        resp = api_client.post(
            f"{BASE_URL}/api/auth/signup",
            json={"email": founder_email, "password": password, "name": "Founder"},
        )
        if resp.status_code == 200:
            token = resp.json()["token"]
        else:
            login_resp = api_client.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": founder_email, "password": password},
            )
            if login_resp.status_code != 200:
                pytest.skip(f"Cannot obtain auth for founder email {founder_email}: {login_resp.text}")
            token = login_resp.json()["token"]

        api_client.headers.update({"Authorization": f"Bearer {token}"})

        db_user = mongo_db.users.find_one({"email": founder_email})
        assert db_user is not None
        # Force pro_active false to specifically test the founder bypass path
        mongo_db.users.update_one({"email": founder_email}, {"$set": {"pro_active": False}})

        resp = api_client.get(f"{BASE_URL}/api/practice")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "questions" in data
        assert len(data["questions"]) > 0


class TestPremiumLessonRegressionTrialAccess:
    """PRO_UNITS/lesson_pro gating must be UNCHANGED - trial users still get lessons."""

    def test_trial_user_can_access_pro_unit_lesson(self, api_client, mongo_db):
        email, _, token, user = signup_new_user(api_client, "TEST_lesson_trial")
        db_user = mongo_db.users.find_one({"email": email})
        assert db_user.get("pro_active", False) is False

        # fetch curriculum to find a PRO_UNITS (u21+) lesson id
        curr_resp = api_client.get(f"{BASE_URL}/api/curriculum")
        assert curr_resp.status_code == 200, curr_resp.text
        curriculum = curr_resp.json()
        pro_lesson_id = None
        for unit in curriculum.get("units", []):
            if unit.get("pro") and unit.get("lessons"):
                pro_lesson_id = unit["lessons"][0]["id"]
                assert unit["lessons"][0]["pro_locked"] is False, (
                    "curriculum should mark pro unit lessons as NOT locked for trial user "
                    "(pro_locked based on compute_pro().is_pro, unchanged)"
                )
                break
        if pro_lesson_id is None:
            pytest.skip("No PRO_UNITS lesson found in /api/curriculum response to test with")

        resp = api_client.get(f"{BASE_URL}/api/lessons/{pro_lesson_id}")
        assert resp.status_code == 200, (
            f"Trial user should still access PRO_UNITS lesson {pro_lesson_id}, got {resp.status_code}: {resp.text}"
        )

        mongo_db.users.delete_one({"email": email})


class TestGeneralAuthMeUnaffected:
    """auth/me is_pro/pro_source values for trial users must remain unaffected."""

    def test_trial_user_auth_me_is_pro_true(self, api_client, mongo_db):
        email, _, token, user = signup_new_user(api_client, "TEST_authme")
        me = api_client.get(f"{BASE_URL}/api/auth/me")
        assert me.status_code == 200
        data = me.json()["user"]
        assert data["is_pro"] is True
        assert data["pro_source"] == "trial"
        mongo_db.users.delete_one({"email": email})
