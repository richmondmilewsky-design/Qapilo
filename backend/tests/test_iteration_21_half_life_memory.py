"""
Iteration 21: Heuristic half-life memory model for /practice prioritization.
Covers:
 - POST /api/lessons/{lesson_id}/complete writes lesson_memory doc (half_life_days, last_seen_at)
 - half_life doubles on accuracy>=0.6 (capped 60.0), halves on accuracy<0.6 (floored 0.5)
 - response shape unchanged (earned_xp, first_time, perfect, new_badges, user)
 - GET /api/practice prioritizes 'due' lessons (simulated stale last_seen_at)
 - GET /api/practice works for brand-new user (no lesson_memory / completed_lessons)
 - GET /api/practice gracefully skips stale/malformed lesson_memory (lesson_id not in LESSON_MAP)
 - POST /api/practice/complete regression (untouched)
"""
import os
import time
import uuid
import pytest
import requests
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL").rstrip("/")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")


@pytest.fixture(scope="module")
def mongo_db():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    yield db
    client.close()


@pytest.fixture(scope="module")
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


def _signup_and_get_token(api_client, email_prefix="TEST_hlm"):
    email = f"{email_prefix}_{uuid.uuid4().hex[:10]}@example.com"
    resp = api_client.post(f"{BASE_URL}/api/auth/signup", json={
        "email": email, "password": "testpass123", "name": "Half Life Tester"
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    token = data["token"]
    user_id = data["user"]["user_id"]
    api_client.headers.update({"Authorization": f"Bearer {token}"})
    return email, user_id


def _first_lesson_id(api_client):
    resp = api_client.get(f"{BASE_URL}/api/curriculum")
    assert resp.status_code == 200
    data = resp.json()
    for unit in data["units"]:
        if unit["lessons"]:
            return unit["lessons"][0]["id"]
    return None


class TestCompleteLessonHalfLife:
    """POST /api/lessons/{lesson_id}/complete -> lesson_memory doc lifecycle"""

    @pytest.fixture(scope="class")
    def user_ctx(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        email, user_id = _signup_and_get_token(session)
        lesson_id = _first_lesson_id(session)
        assert lesson_id, "No lesson found to test with"
        yield session, user_id, lesson_id

    def test_first_completion_sets_half_life_1(self, user_ctx, mongo_db):
        session, user_id, lesson_id = user_ctx
        resp = session.post(f"{BASE_URL}/api/lessons/{lesson_id}/complete",
                             json={"correct": 5, "total": 5})
        assert resp.status_code == 200, resp.text
        body = resp.json()
        # response shape unchanged
        assert set(["earned_xp", "first_time", "perfect", "new_badges", "user"]).issubset(body.keys())
        assert body["first_time"] is True
        assert body["perfect"] is True

        mem = mongo_db.lesson_memory.find_one({"user_id": user_id, "lesson_id": lesson_id})
        assert mem is not None, "lesson_memory doc not created"
        assert mem["half_life_days"] == 1.0
        assert mem["last_seen_at"] is not None

    def test_second_completion_high_accuracy_doubles(self, user_ctx, mongo_db):
        session, user_id, lesson_id = user_ctx
        prev = mongo_db.lesson_memory.find_one({"user_id": user_id, "lesson_id": lesson_id})
        prev_hl = prev["half_life_days"]

        resp = session.post(f"{BASE_URL}/api/lessons/{lesson_id}/complete",
                             json={"correct": 5, "total": 5})
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["first_time"] is False  # already completed

        mem = mongo_db.lesson_memory.find_one({"user_id": user_id, "lesson_id": lesson_id})
        assert mem["half_life_days"] == min(60.0, prev_hl * 2)

    def test_third_completion_low_accuracy_halves(self, user_ctx, mongo_db):
        session, user_id, lesson_id = user_ctx
        prev = mongo_db.lesson_memory.find_one({"user_id": user_id, "lesson_id": lesson_id})
        prev_hl = prev["half_life_days"]

        resp = session.post(f"{BASE_URL}/api/lessons/{lesson_id}/complete",
                             json={"correct": 1, "total": 5})
        assert resp.status_code == 200, resp.text

        mem = mongo_db.lesson_memory.find_one({"user_id": user_id, "lesson_id": lesson_id})
        assert mem["half_life_days"] == max(0.5, prev_hl / 2)

    def test_cap_at_60_and_floor_at_half(self, user_ctx, mongo_db):
        """Repeatedly complete with high accuracy to check cap at 60.0"""
        session, user_id, lesson_id = user_ctx
        for _ in range(12):
            resp = session.post(f"{BASE_URL}/api/lessons/{lesson_id}/complete",
                                 json={"correct": 5, "total": 5})
            assert resp.status_code == 200
        mem = mongo_db.lesson_memory.find_one({"user_id": user_id, "lesson_id": lesson_id})
        assert mem["half_life_days"] == 60.0, f"Expected cap at 60.0, got {mem['half_life_days']}"

        for _ in range(10):
            resp = session.post(f"{BASE_URL}/api/lessons/{lesson_id}/complete",
                                 json={"correct": 1, "total": 5})
            assert resp.status_code == 200
        mem = mongo_db.lesson_memory.find_one({"user_id": user_id, "lesson_id": lesson_id})
        assert mem["half_life_days"] == 0.5, f"Expected floor at 0.5, got {mem['half_life_days']}"

    @classmethod
    def teardown_class(cls):
        pass  # cleanup happens in module-level fixture below


class TestPracticeDueLessons:
    """GET /api/practice prioritization + edge cases"""

    def test_new_user_practice_unchanged(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        _signup_and_get_token(session, "TEST_hlm_newuser")
        resp = session.get(f"{BASE_URL}/api/practice")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "questions" in data and 0 < len(data["questions"]) <= 5
        for q in data["questions"]:
            assert set(["q", "options", "answer", "explain", "tier"]).issubset(q.keys())
        for key in ["reward_xp", "tier", "max_tier", "practice_level"]:
            assert key in data

    def test_due_lesson_prioritized(self, mongo_db):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        email, user_id = _signup_and_get_token(session, "TEST_hlm_due")
        lesson_id = _first_lesson_id(session)

        # complete the lesson first (creates completed_lessons + lesson_memory)
        resp = session.post(f"{BASE_URL}/api/lessons/{lesson_id}/complete",
                             json={"correct": 5, "total": 5})
        assert resp.status_code == 200

        # force half_life_days=1.0, last_seen_at=10 days ago -> p = 2^(-10/1) ~ 0.001 <0.7 (due)
        ten_days_ago = datetime.now(timezone.utc) - timedelta(days=10)
        mongo_db.lesson_memory.update_one(
            {"user_id": user_id, "lesson_id": lesson_id},
            {"$set": {"half_life_days": 1.0, "last_seen_at": ten_days_ago}},
        )

        resp = session.get(f"{BASE_URL}/api/practice")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert 0 < len(data["questions"]) <= 5
        for q in data["questions"]:
            assert set(["q", "options", "answer", "explain", "tier"]).issubset(q.keys())

        # Verify due lesson_id's questions appear ahead: fetch lesson question set for lesson_id
        lesson_resp = session.get(f"{BASE_URL}/api/lessons/{lesson_id}")
        assert lesson_resp.status_code == 200
        lesson_questions = {q["q"] for q in lesson_resp.json()["questions"]}
        first_q = data["questions"][0]["q"]
        assert first_q in lesson_questions, (
            "Expected the due lesson's question to be prioritized first in /practice results"
        )

        mongo_db.lesson_memory.delete_one({"user_id": user_id, "lesson_id": lesson_id})

    def test_malformed_lesson_memory_skipped_gracefully(self, mongo_db):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        email, user_id = _signup_and_get_token(session, "TEST_hlm_malformed")
        lesson_id = _first_lesson_id(session)
        resp = session.post(f"{BASE_URL}/api/lessons/{lesson_id}/complete",
                             json={"correct": 5, "total": 5})
        assert resp.status_code == 200

        # Insert a lesson_memory doc referencing a bogus lesson_id not in LESSON_MAP
        bogus_lesson_id = "TEST_nonexistent_lesson_xyz"
        # also mark it as completed to be included in query, and stale
        mongo_db.users.update_one(
            {"user_id": user_id},
            {"$push": {"completed_lessons": bogus_lesson_id}},
        )
        mongo_db.lesson_memory.insert_one({
            "user_id": user_id, "lesson_id": bogus_lesson_id,
            "half_life_days": 1.0,
            "last_seen_at": datetime.now(timezone.utc) - timedelta(days=30),
        })

        resp = session.get(f"{BASE_URL}/api/practice")
        assert resp.status_code == 200, f"Practice endpoint crashed with malformed lesson_memory: {resp.text}"
        data = resp.json()
        assert 0 < len(data["questions"]) <= 5

        # cleanup
        mongo_db.lesson_memory.delete_one({"user_id": user_id, "lesson_id": bogus_lesson_id})
        mongo_db.users.update_one(
            {"user_id": user_id},
            {"$pull": {"completed_lessons": bogus_lesson_id}},
        )


class TestPracticeCompleteRegression:
    """POST /api/practice/complete unrelated endpoint - unaffected regression check"""

    def test_practice_complete_unchanged(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        _signup_and_get_token(session, "TEST_hlm_practice_complete")
        resp = session.post(f"{BASE_URL}/api/practice/complete",
                             json={"correct": 4, "total": 5, "tier": 1, "lang": "en"})
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert set(["earned_xp", "perfect", "new_badges", "user"]).issubset(body.keys())
        assert body["perfect"] is False
        assert body["earned_xp"] > 0
