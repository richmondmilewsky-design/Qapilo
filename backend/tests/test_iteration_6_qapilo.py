"""
Iteration 6 — Qapilo rebrand + 50-unit curriculum + endless Practice + AI Tutor real-time context.

Covers:
- AUTH: signup / login (email/password) still work; disclaimer acceptance endpoint idempotent
- CURRICULUM: GET /api/curriculum returns 50 units / 150 lessons with tier per unit;
              units u21..u50 have pro=true (regardless of trial); localized DE/ES titles differ.
- LESSON:    GET /api/lessons/l1 returns 3 cards + 4 questions per language;
             DE/ES have same option count as EN; POST /api/lessons/l1/complete awards XP.
- PRACTICE:  GET /api/practice returns 5 questions with q/options(4)/answer/tier + reward_xp;
             POST /api/practice/complete awards XP, increments daily_xp + streak.
- TUTOR:     POST /api/tutor/chat with a live-price question mentions AAPL price and disclaimer.
             General (non-realtime) questions still work.
"""
import os
import secrets
import time

import pytest
import requests

BASE_URL = os.environ["EXPO_PUBLIC_BACKEND_URL"].rstrip("/")

PRO_UNIT_IDS = {f"u{i}" for i in range(21, 51)}
FREE_UNIT_IDS = {f"u{i}" for i in range(1, 21)}


# --------------------------- Fixtures ---------------------------
@pytest.fixture(scope="module")
def user_a():
    """Fresh user A — used across curriculum / lesson / practice tests."""
    s = requests.Session()
    s.headers["Content-Type"] = "application/json"
    email = f"TEST_it6a_{secrets.token_hex(4)}@qapilo.app"
    password = "demo123!"
    r = s.post(f"{BASE_URL}/api/auth/signup",
               json={"name": "TEST it6a", "email": email, "password": password})
    assert r.status_code == 200, r.text
    tok = r.json()["token"]
    s.headers["Authorization"] = f"Bearer {tok}"
    s.post(f"{BASE_URL}/api/auth/accept-terms")
    s.creds = {"email": email, "password": password}  # type: ignore[attr-defined]
    return s


@pytest.fixture(scope="module")
def user_b():
    """Fresh user B — for tutor tests (keeps quota isolated)."""
    s = requests.Session()
    s.headers["Content-Type"] = "application/json"
    email = f"TEST_it6b_{secrets.token_hex(4)}@qapilo.app"
    r = s.post(f"{BASE_URL}/api/auth/signup",
               json={"name": "TEST it6b", "email": email, "password": "demo123!"})
    assert r.status_code == 200, r.text
    s.headers["Authorization"] = f"Bearer {r.json()['token']}"
    s.post(f"{BASE_URL}/api/auth/accept-terms")
    return s


# --------------------------- AUTH ---------------------------
class TestAuth:
    def test_signup_login_flow(self):
        s = requests.Session()
        s.headers["Content-Type"] = "application/json"
        email = f"TEST_it6auth_{secrets.token_hex(4)}@qapilo.app"
        pw = "sekret6!"
        r = s.post(f"{BASE_URL}/api/auth/signup",
                   json={"name": "AuthTest", "email": email, "password": pw})
        assert r.status_code == 200
        j = r.json()
        assert "token" in j
        assert j["user"]["email"].lower() == email.lower()
        assert j["user"].get("is_pro") is True  # 7-day trial

        # login again returns a fresh token
        r2 = s.post(f"{BASE_URL}/api/auth/login",
                    json={"email": email, "password": pw})
        assert r2.status_code == 200
        assert r2.json()["token"]

    def test_login_wrong_password_fails(self):
        r = requests.post(f"{BASE_URL}/api/auth/login",
                          json={"email": "nobody@qapilo.app", "password": "wrong"})
        assert r.status_code in (400, 401, 404)

    def test_accept_terms_idempotent(self, user_a):
        r1 = user_a.post(f"{BASE_URL}/api/auth/accept-terms")
        assert r1.status_code == 200
        r2 = user_a.post(f"{BASE_URL}/api/auth/accept-terms")
        assert r2.status_code == 200


# --------------------------- CURRICULUM ---------------------------
class TestCurriculum:
    def test_returns_50_units_150_lessons_en(self, user_a):
        r = user_a.get(f"{BASE_URL}/api/curriculum", params={"lang": "en"})
        assert r.status_code == 200, r.text
        j = r.json()
        assert j["total_lessons"] == 150, f"expected 150 lessons, got {j['total_lessons']}"
        assert len(j["units"]) == 50, f"expected 50 units, got {len(j['units'])}"
        for u in j["units"]:
            assert 1 <= u["tier"] <= 5, f"bad tier on {u['id']}: {u['tier']}"
            assert len(u["lessons"]) == 3, f"unit {u['id']} has {len(u['lessons'])} lessons"

    def test_pro_flag_on_units_u21_to_u50(self, user_a):
        j = user_a.get(f"{BASE_URL}/api/curriculum", params={"lang": "en"}).json()
        by_id = {u["id"]: u for u in j["units"]}
        for uid in PRO_UNIT_IDS:
            assert uid in by_id, f"missing pro unit {uid}"
            assert by_id[uid]["pro"] is True, f"{uid} should be pro"
        for uid in FREE_UNIT_IDS:
            assert by_id[uid]["pro"] is False, f"{uid} should NOT be pro"

    def test_trial_user_can_access_pro_lessons(self, user_a):
        # New signup gets is_pro=true via trial → pro_locked must be false everywhere
        j = user_a.get(f"{BASE_URL}/api/curriculum", params={"lang": "en"}).json()
        assert j["is_pro"] is True
        for u in j["units"]:
            for l in u["lessons"]:
                assert l["pro_locked"] is False, f"trial user should not be pro_locked ({l['id']})"

    def test_localized_titles_de_es(self, user_a):
        en = user_a.get(f"{BASE_URL}/api/curriculum", params={"lang": "en"}).json()
        de = user_a.get(f"{BASE_URL}/api/curriculum", params={"lang": "de"}).json()
        es = user_a.get(f"{BASE_URL}/api/curriculum", params={"lang": "es"}).json()
        assert len(de["units"]) == 50 and len(es["units"]) == 50

        en_titles = {u["id"]: u["title"] for u in en["units"]}
        de_titles = {u["id"]: u["title"] for u in de["units"]}
        es_titles = {u["id"]: u["title"] for u in es["units"]}

        # At least half of the units must have a different title in DE / ES vs EN.
        diff_de = sum(1 for uid, t in en_titles.items() if de_titles[uid] != t)
        diff_es = sum(1 for uid, t in en_titles.items() if es_titles[uid] != t)
        assert diff_de >= 25, f"only {diff_de}/50 DE titles differ from EN"
        assert diff_es >= 25, f"only {diff_es}/50 ES titles differ from EN"


# --------------------------- LESSON ---------------------------
class TestLesson:
    def test_lesson_l1_en_shape(self, user_a):
        r = user_a.get(f"{BASE_URL}/api/lessons/l1", params={"lang": "en"})
        assert r.status_code == 200, r.text
        j = r.json()
        assert len(j["cards"]) == 3, f"expected 3 cards, got {len(j['cards'])}"
        assert len(j["questions"]) == 4, f"expected 4 questions, got {len(j['questions'])}"
        for q in j["questions"]:
            assert "options" in q and len(q["options"]) >= 2
            assert isinstance(q["answer"], int)
            assert 0 <= q["answer"] < len(q["options"])

    def test_lesson_l1_localized_same_option_count(self, user_a):
        en = user_a.get(f"{BASE_URL}/api/lessons/l1", params={"lang": "en"}).json()
        de = user_a.get(f"{BASE_URL}/api/lessons/l1", params={"lang": "de"}).json()
        es = user_a.get(f"{BASE_URL}/api/lessons/l1", params={"lang": "es"}).json()

        assert len(de["cards"]) == len(en["cards"]) == 3
        assert len(es["cards"]) == len(en["cards"]) == 3
        assert len(de["questions"]) == len(en["questions"]) == 4
        assert len(es["questions"]) == len(en["questions"]) == 4

        for i, q in enumerate(en["questions"]):
            assert len(de["questions"][i]["options"]) == len(q["options"]), \
                f"DE lesson q{i} option count mismatch"
            assert len(es["questions"][i]["options"]) == len(q["options"]), \
                f"ES lesson q{i} option count mismatch"

    def test_complete_lesson_awards_xp(self, user_b):
        before = user_b.get(f"{BASE_URL}/api/progress").json()["user"]
        r = user_b.post(f"{BASE_URL}/api/lessons/l1/complete",
                        json={"correct": 4, "total": 4})
        assert r.status_code == 200, r.text
        j = r.json()
        assert j["earned_xp"] > 0
        assert j["perfect"] is True
        after = j["user"]
        assert after["xp"] >= before["xp"] + j["earned_xp"]
        assert "l1" in after["completed_lessons"]


# --------------------------- PRACTICE ---------------------------
class TestPractice:
    def test_practice_returns_5_questions_shape(self, user_a):
        r = user_a.get(f"{BASE_URL}/api/practice", params={"lang": "en"})
        assert r.status_code == 200, r.text
        j = r.json()
        assert len(j["questions"]) == 5, f"expected 5 questions, got {len(j['questions'])}"
        for q in j["questions"]:
            assert set(["q", "options", "answer", "tier"]).issubset(q.keys())
            assert len(q["options"]) == 4, f"expected 4 options, got {len(q['options'])}"
            assert isinstance(q["answer"], int)
            assert 1 <= q["tier"] <= 5
        assert isinstance(j["reward_xp"], int) and j["reward_xp"] > 0
        assert 1 <= j["tier"] <= 5

    def test_practice_localized_de(self, user_a):
        r = user_a.get(f"{BASE_URL}/api/practice", params={"lang": "de"})
        assert r.status_code == 200
        j = r.json()
        assert len(j["questions"]) == 5
        for q in j["questions"]:
            assert len(q["options"]) == 4

    def test_practice_complete_awards_xp_and_streak(self, user_a):
        before = user_a.get(f"{BASE_URL}/api/progress").json()["user"]
        r = user_a.post(f"{BASE_URL}/api/practice/complete",
                        json={"correct": 4, "total": 5, "tier": 2, "lang": "en"})
        assert r.status_code == 200, r.text
        j = r.json()
        assert j["earned_xp"] >= 5
        assert j["user"]["xp"] >= before["xp"] + j["earned_xp"]
        # streak should have advanced to at least 1 (fresh user)
        assert j["user"]["streak"] >= 1
        # daily_xp bumped
        assert j["user"]["daily_xp"] >= j["earned_xp"]


# --------------------------- AI TUTOR ---------------------------
class TestTutor:
    def test_tutor_price_question_uses_finnhub_and_disclaimer(self, user_b):
        r = user_b.post(f"{BASE_URL}/api/tutor/chat",
                        json={"message": "What is the current price of Apple (AAPL) today?",
                              "lang": "en"},
                        timeout=90)
        assert r.status_code == 200, r.text
        reply = r.json()["reply"].lower()
        # Disclaimer must appear (as per system prompt)
        assert "not financial advice" in reply or "educational only" in reply, \
            f"expected disclaimer in reply, got: {reply[:400]}"
        # Should reference AAPL / Apple and mention a numeric price ($ or digits)
        assert ("apple" in reply) or ("aapl" in reply)
        assert any(ch.isdigit() for ch in reply), "expected numeric price content in reply"

    def test_tutor_general_question_works(self, user_b):
        # small sleep to be gentle to the model
        time.sleep(1)
        r = user_b.post(f"{BASE_URL}/api/tutor/chat",
                        json={"message": "In one sentence, what is a stock?",
                              "lang": "en"},
                        timeout=90)
        assert r.status_code == 200, r.text
        reply = r.json()["reply"]
        assert isinstance(reply, str) and len(reply) > 10
