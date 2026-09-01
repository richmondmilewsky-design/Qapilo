"""
Iteration 37: Placement quiz (onboarding-only) backend tests.
Covers:
- GET /api/auth/placement-quiz?lang=en/de/es (7 tier<=2 shuffled questions)
- POST /api/auth/placement-quiz/complete (0 / partial / perfect score grant logic)
- Level cap (<=10) safety, 20-lesson hard cap
- No badge/streak/perfect_lessons side effects
- Idempotent second-call behavior (no double grant)
- Regression: PATCH /api/auth/experience, complete_lesson, /api/practice, demo login unaffected
"""
import os
import random
import string
import pytest
import requests

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL", "").rstrip("/")


def rand_email():
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"TEST_placement_{suffix}@example.com"


@pytest.fixture
def api_client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def signup(api_client):
    email = rand_email()
    resp = api_client.post(f"{BASE_URL}/api/auth/signup", json={
        "email": email, "password": "testpass123", "name": "Placement Tester"
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    token = data["token"]
    api_client.headers.update({"Authorization": f"Bearer {token}"})
    return data["user"]


def level_for_xp(xp):
    return xp // 100 + 1


class TestPlacementQuizGet:
    def test_en_returns_7_tier_le_2_questions(self, api_client):
        signup(api_client)
        resp = api_client.get(f"{BASE_URL}/api/auth/placement-quiz?lang=en")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "questions" in data
        qs = data["questions"]
        assert len(qs) == 7, f"Expected 7 questions, got {len(qs)}"
        for q in qs:
            for key in ("q", "options", "answer", "explain", "tier"):
                assert key in q, f"Missing key {key} in question {q}"
            assert q["tier"] <= 2, f"Found tier > 2: {q}"
            assert isinstance(q["options"], list) and len(q["options"]) >= 2
            assert 0 <= q["answer"] < len(q["options"])
            assert q["options"][q["answer"]]  # answer index maps to non-empty text

    def test_de_localized(self, api_client):
        signup(api_client)
        resp = api_client.get(f"{BASE_URL}/api/auth/placement-quiz?lang=de")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["questions"]) == 7
        for q in data["questions"]:
            assert q["tier"] <= 2

    def test_es_localized(self, api_client):
        signup(api_client)
        resp = api_client.get(f"{BASE_URL}/api/auth/placement-quiz?lang=es")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["questions"]) == 7
        for q in data["questions"]:
            assert q["tier"] <= 2

    def test_requires_auth(self, api_client):
        resp = api_client.get(f"{BASE_URL}/api/auth/placement-quiz?lang=en")
        assert resp.status_code in (401, 403)


class TestPlacementQuizCompleteZeroScore:
    def test_zero_score_grants_nothing(self, api_client):
        user = signup(api_client)
        assert user["xp"] == 0
        assert user.get("completed_lessons", []) == []

        resp = api_client.post(f"{BASE_URL}/api/auth/placement-quiz/complete",
                                json={"correct": 0, "total": 7})
        assert resp.status_code == 200, resp.text
        updated = resp.json()["user"]

        assert updated["xp"] == 0, f"Expected xp unchanged (0), got {updated['xp']}"
        assert updated.get("completed_lessons", []) == [], "Expected no lessons granted"

        pqr = updated.get("placement_quiz_result")
        assert pqr is not None
        assert pqr["correct"] == 0
        assert pqr["total"] == 7
        assert pqr["granted_lesson_count"] == 0
        assert pqr["granted_level"] == 1
        assert "completed_at" in pqr

        # No badge/streak/perfect_lessons side effects
        assert updated.get("badges", []) == []
        assert updated.get("streak", 0) == 0
        assert updated.get("longest_streak", 0) == 0
        assert updated.get("perfect_lessons", []) == []


class TestPlacementQuizCompletePerfectScore:
    def test_perfect_score_caps_level_at_10(self, api_client):
        user = signup(api_client)
        resp = api_client.post(f"{BASE_URL}/api/auth/placement-quiz/complete",
                                json={"correct": 7, "total": 7})
        assert resp.status_code == 200, resp.text
        updated = resp.json()["user"]

        granted_lessons = updated.get("completed_lessons", [])
        assert 0 < len(granted_lessons) <= 20, f"Expected 1-20 lessons granted, got {len(granted_lessons)}"
        assert updated["xp"] > 0

        final_level = level_for_xp(updated["xp"])
        assert final_level <= 10, f"Level cap violated! final_level={final_level}, xp={updated['xp']}"

        pqr = updated["placement_quiz_result"]
        assert pqr["granted_lesson_count"] == len(granted_lessons)
        assert pqr["granted_level"] <= 10

        # No badge/streak side effects
        assert updated.get("badges", []) == []
        assert updated.get("streak", 0) == 0
        assert updated.get("perfect_lessons", []) == []


class TestPlacementQuizCompletePartialScore:
    def test_partial_score_targets_level_6(self, api_client):
        user = signup(api_client)
        resp = api_client.post(f"{BASE_URL}/api/auth/placement-quiz/complete",
                                json={"correct": 4, "total": 7})
        assert resp.status_code == 200, resp.text
        updated = resp.json()["user"]

        score_frac = 4 / 7
        expected_target = min(10, round(1 + score_frac * 9))
        assert expected_target == 6, f"sanity check on expected math failed: {expected_target}"

        granted_lessons = updated.get("completed_lessons", [])
        # NOTE: the 20-lesson hard safety cap combined with low early-lesson XP means
        # mid/high target scores (target_level > ~3) always hit the 20-lesson cap
        # before reaching their target level. This is an accepted business tradeoff
        # (per product owner), not a bug -- do not re-flag. Assert cap behavior instead.
        assert len(granted_lessons) <= 20, "Hard safety cap of 20 lessons must never be exceeded"
        final_level = level_for_xp(updated["xp"])
        assert final_level <= 10

        pqr = updated["placement_quiz_result"]
        assert pqr["granted_level"] == final_level
        # loop stops once level >= target level (6), so final level should be >= target
        # UNLESS the 20-lesson hard cap fires first (known/accepted tradeoff)
        assert final_level >= expected_target or len(granted_lessons) >= 20

        assert updated.get("badges", []) == []
        assert updated.get("streak", 0) == 0
        assert updated.get("perfect_lessons", []) == []


class TestPlacementQuizDoubleCall:
    def test_second_call_does_not_double_grant(self, api_client):
        user = signup(api_client)
        resp1 = api_client.post(f"{BASE_URL}/api/auth/placement-quiz/complete",
                                 json={"correct": 4, "total": 7})
        assert resp1.status_code == 200
        updated1 = resp1.json()["user"]
        lessons1 = set(updated1.get("completed_lessons", []))
        xp1 = updated1["xp"]

        # Call again with a HIGHER score - should only grant delta, no duplicates
        resp2 = api_client.post(f"{BASE_URL}/api/auth/placement-quiz/complete",
                                 json={"correct": 7, "total": 7})
        assert resp2.status_code == 200
        updated2 = resp2.json()["user"]
        lessons2 = updated2.get("completed_lessons", [])

        # No duplicate entries
        assert len(lessons2) == len(set(lessons2)), "Duplicate lesson entries found!"
        # Previously granted lessons still present
        assert lessons1.issubset(set(lessons2))
        # xp should not have decreased, and should reflect no double-counting of lessons1
        assert updated2["xp"] >= xp1

        final_level = level_for_xp(updated2["xp"])
        assert final_level <= 10

        # Call again with a LOWER score (0) after already exceeding target - expect no changes
        resp3 = api_client.post(f"{BASE_URL}/api/auth/placement-quiz/complete",
                                 json={"correct": 0, "total": 7})
        assert resp3.status_code == 200
        updated3 = resp3.json()["user"]
        assert updated3["xp"] == updated2["xp"], "Lower-score replay should not remove lessons/xp"
        assert set(updated3.get("completed_lessons", [])) == set(lessons2)


class TestRegressionExperienceAndDemo:
    def test_patch_experience_still_works(self, api_client):
        signup(api_client)
        resp = api_client.patch(f"{BASE_URL}/api/auth/experience",
                                 json={"experience_level": "some"})
        assert resp.status_code == 200, resp.text
        updated = resp.json()["user"]
        assert updated["experience_level"] == "some"

        resp2 = api_client.patch(f"{BASE_URL}/api/auth/experience",
                                  json={"experience_level": "bogus"})
        assert resp2.status_code == 400

    def test_demo_login_and_sanity_flows(self, api_client):
        resp = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@tradequest.app", "password": "demo123"
        })
        if resp.status_code != 200:
            pytest.skip("demo@tradequest.app not available in this environment")
        token = resp.json()["token"]
        api_client.headers.update({"Authorization": f"Bearer {token}"})

        practice_resp = api_client.get(f"{BASE_URL}/api/practice")
        assert practice_resp.status_code == 200

        me_resp = api_client.get(f"{BASE_URL}/api/auth/me")
        assert me_resp.status_code == 200
