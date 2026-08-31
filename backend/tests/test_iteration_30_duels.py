"""
Iteration 30: Async quiz duel feature ("Freund herausfordern")
Tests: POST /api/duels, GET /api/duels/{duel_id}, POST /api/duels/{duel_id}/complete
Plus regression sanity for /api/practice, /api/practice/complete, and XP/streak isolation.
"""
import os
import uuid
import pytest
import requests
from pathlib import Path

def _load_backend_url():
    val = os.environ.get("EXPO_BACKEND_URL") or os.environ.get("EXPO_PUBLIC_BACKEND_URL")
    if val:
        return val.rstrip("/")
    env_path = Path("/app/frontend/.env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("EXPO_PUBLIC_BACKEND_URL="):
                return line.split("=", 1)[1].strip().strip('"').rstrip("/")
    return ""

BASE_URL = _load_backend_url()


@pytest.fixture(scope="module")
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def user_a_token(api_client):
    r = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": "demo@tradequest.app", "password": "demo123"
    })
    if r.status_code != 200:
        pytest.skip(f"Could not login as demo user A: {r.status_code} {r.text}")
    return r.json()["token"]


def _fresh_user(api_client, tag):
    email = f"TEST_duel_{tag}_{uuid.uuid4().hex[:8]}@example.com"
    r = api_client.post(f"{BASE_URL}/api/auth/signup", json={
        "email": email, "password": "testpass123", "name": f"Duel {tag}"
    })
    assert r.status_code == 200, r.text
    return r.json()["token"]


@pytest.fixture(scope="module")
def user_b_token(api_client):
    return _fresh_user(api_client, "B")


@pytest.fixture(scope="module")
def user_c_token(api_client):
    return _fresh_user(api_client, "C")


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


class TestDuelCreationAndFetch:
    duel_id = None
    original_questions = None

    def test_create_duel(self, api_client, user_a_token):
        r = api_client.post(f"{BASE_URL}/api/duels?lang=en", headers=auth_headers(user_a_token))
        assert r.status_code == 200, r.text
        data = r.json()
        assert "duel_id" in data and isinstance(data["duel_id"], str) and len(data["duel_id"]) > 0
        assert "questions" in data
        assert len(data["questions"]) == 5
        for q in data["questions"]:
            assert set(["q", "options", "answer", "explain", "tier"]).issubset(q.keys())
        TestDuelCreationAndFetch.duel_id = data["duel_id"]
        TestDuelCreationAndFetch.original_questions = data["questions"]

    def test_get_duel_en_matches_creation(self, api_client, user_a_token):
        duel_id = TestDuelCreationAndFetch.duel_id
        r = api_client.get(f"{BASE_URL}/api/duels/{duel_id}?lang=en", headers=auth_headers(user_a_token))
        assert r.status_code == 200, r.text
        data = r.json()
        assert len(data["questions"]) == 5
        orig_qs = [q["q"] for q in TestDuelCreationAndFetch.original_questions]
        fetched_qs = [q["q"] for q in data["questions"]]
        assert orig_qs == fetched_qs, "Questions/order mismatch between create and GET"
        assert data["creator_result"] is None
        assert data["opponent_result"] is None
        assert "creator_user_id" in data

    def test_get_duel_de_localized(self, api_client, user_a_token):
        duel_id = TestDuelCreationAndFetch.duel_id
        r = api_client.get(f"{BASE_URL}/api/duels/{duel_id}?lang=de", headers=auth_headers(user_a_token))
        assert r.status_code == 200, r.text
        data = r.json()
        assert len(data["questions"]) == 5
        orig_tiers = [q["tier"] for q in TestDuelCreationAndFetch.original_questions]
        de_tiers = [q["tier"] for q in data["questions"]]
        assert orig_tiers == de_tiers, "Tiers should match between languages"
        orig_qs = [q["q"] for q in TestDuelCreationAndFetch.original_questions]
        de_qs = [q["q"] for q in data["questions"]]
        assert orig_qs != de_qs, "DE text should differ from EN text (localization)"

    def test_get_duel_es_localized(self, api_client, user_a_token):
        duel_id = TestDuelCreationAndFetch.duel_id
        r = api_client.get(f"{BASE_URL}/api/duels/{duel_id}?lang=es", headers=auth_headers(user_a_token))
        assert r.status_code == 200, r.text
        data = r.json()
        assert len(data["questions"]) == 5
        orig_qs = [q["q"] for q in TestDuelCreationAndFetch.original_questions]
        es_qs = [q["q"] for q in data["questions"]]
        assert orig_qs != es_qs, "ES text should differ from EN text (localization)"

    def test_get_duel_not_found(self, api_client, user_a_token):
        r = api_client.get(f"{BASE_URL}/api/duels/deadbeef?lang=en", headers=auth_headers(user_a_token))
        assert r.status_code == 404, r.text


class TestDuelCompletionFlow:
    """Full multi-user completion flow using a fresh duel."""
    duel_id = None

    def test_setup_new_duel(self, api_client, user_a_token):
        r = api_client.post(f"{BASE_URL}/api/duels?lang=en", headers=auth_headers(user_a_token))
        assert r.status_code == 200
        TestDuelCompletionFlow.duel_id = r.json()["duel_id"]

    def test_creator_completes(self, api_client, user_a_token):
        duel_id = TestDuelCompletionFlow.duel_id
        r = api_client.post(f"{BASE_URL}/api/duels/{duel_id}/complete",
                             json={"correct": 4, "total": 5}, headers=auth_headers(user_a_token))
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["creator_result"]["correct"] == 4
        assert data["creator_result"]["total"] == 5
        assert "completed_at" in data["creator_result"]
        assert data["opponent_result"] is None

    def test_creator_cannot_replay(self, api_client, user_a_token):
        duel_id = TestDuelCompletionFlow.duel_id
        r = api_client.post(f"{BASE_URL}/api/duels/{duel_id}/complete",
                             json={"correct": 5, "total": 5}, headers=auth_headers(user_a_token))
        assert r.status_code == 409, r.text
        # verify unchanged via GET
        r2 = api_client.get(f"{BASE_URL}/api/duels/{duel_id}?lang=en", headers=auth_headers(user_a_token))
        assert r2.json()["creator_result"]["correct"] == 4

    def test_opponent_b_completes(self, api_client, user_b_token):
        duel_id = TestDuelCompletionFlow.duel_id
        r = api_client.post(f"{BASE_URL}/api/duels/{duel_id}/complete",
                             json={"correct": 3, "total": 5}, headers=auth_headers(user_b_token))
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["opponent_result"]["correct"] == 3
        assert data["opponent_result"]["total"] == 5
        assert data["creator_result"]["correct"] == 4, "creator result must remain from earlier"
        assert data["opponent_user_id"] is not None

    def test_opponent_b_cannot_replay(self, api_client, user_b_token):
        duel_id = TestDuelCompletionFlow.duel_id
        r = api_client.post(f"{BASE_URL}/api/duels/{duel_id}/complete",
                             json={"correct": 1, "total": 5}, headers=auth_headers(user_b_token))
        assert r.status_code == 409, r.text

    def test_third_user_c_blocked(self, api_client, user_c_token):
        duel_id = TestDuelCompletionFlow.duel_id
        r = api_client.post(f"{BASE_URL}/api/duels/{duel_id}/complete",
                             json={"correct": 2, "total": 5}, headers=auth_headers(user_c_token))
        assert r.status_code == 409, r.text


class TestRegressionPracticeAndXp:
    def test_practice_endpoint_unchanged_shape(self, api_client, user_a_token):
        r = api_client.get(f"{BASE_URL}/api/practice?lang=en", headers=auth_headers(user_a_token))
        assert r.status_code == 200, r.text
        data = r.json()
        assert "questions" in data
        assert len(data["questions"]) > 0
        for q in data["questions"][:1]:
            assert set(["q", "options", "answer", "explain", "tier"]).issubset(q.keys())

    def test_xp_streak_unchanged_after_duel(self, api_client, user_a_token):
        # get user state before
        me_before = api_client.get(f"{BASE_URL}/api/auth/me", headers=auth_headers(user_a_token))
        if me_before.status_code != 200:
            pytest.skip("no /api/auth/me endpoint available")
        before = me_before.json()

        # create + complete a new duel as A
        create_r = api_client.post(f"{BASE_URL}/api/duels?lang=en", headers=auth_headers(user_a_token))
        assert create_r.status_code == 200
        duel_id = create_r.json()["duel_id"]
        complete_r = api_client.post(f"{BASE_URL}/api/duels/{duel_id}/complete",
                                      json={"correct": 5, "total": 5}, headers=auth_headers(user_a_token))
        assert complete_r.status_code == 200

        me_after = api_client.get(f"{BASE_URL}/api/auth/me", headers=auth_headers(user_a_token))
        after = me_after.json()

        before_user = before.get("user", before)
        after_user = after.get("user", after)
        assert before_user.get("xp") == after_user.get("xp"), "XP changed after duel completion (should not)"
        assert before_user.get("streak") == after_user.get("streak"), "Streak changed after duel completion"
        assert before_user.get("level") == after_user.get("level"), "Level changed after duel completion"
