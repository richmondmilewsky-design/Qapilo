"""Iteration 3 tests: disclaimer/agreement gate, PayPal-configured flow, restore button."""
import os
import uuid
import requests
import pytest

BASE_URL = os.environ["EXPO_PUBLIC_BACKEND_URL"].rstrip("/") if os.environ.get("EXPO_PUBLIC_BACKEND_URL") else None
if not BASE_URL:
    # fall back to frontend env file
    from pathlib import Path
    env = Path("/app/frontend/.env").read_text()
    for line in env.splitlines():
        if line.startswith("EXPO_PUBLIC_BACKEND_URL="):
            BASE_URL = line.split("=", 1)[1].strip().rstrip("/")


@pytest.fixture(scope="module")
def signup_user():
    email = f"TEST_it3_{uuid.uuid4().hex[:8]}@tradequest.app"
    r = requests.post(f"{BASE_URL}/api/auth/signup",
                      json={"email": email, "password": "test1234", "name": "It3 User"}, timeout=20)
    assert r.status_code == 200, r.text
    data = r.json()
    return {"token": data["token"], "user": data["user"], "email": email}


@pytest.fixture(scope="module")
def auth_headers(signup_user):
    return {"Authorization": f"Bearer {signup_user['token']}"}


# --- Disclaimer / Agreement gate ---
class TestDisclaimerGate:
    def test_signup_defaults_accepted_terms_false(self, signup_user):
        assert signup_user["user"]["accepted_terms"] is False

    def test_me_shows_accepted_terms_false(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/auth/me", headers=auth_headers, timeout=20)
        assert r.status_code == 200
        assert r.json()["user"]["accepted_terms"] is False

    def test_accept_terms_sets_true(self, auth_headers):
        r = requests.post(f"{BASE_URL}/api/auth/accept-terms", headers=auth_headers, timeout=20)
        assert r.status_code == 200, r.text
        assert r.json()["user"]["accepted_terms"] is True

    def test_persistence_via_me(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/auth/me", headers=auth_headers, timeout=20)
        assert r.status_code == 200
        assert r.json()["user"]["accepted_terms"] is True

    def test_accept_terms_requires_auth(self):
        r = requests.post(f"{BASE_URL}/api/auth/accept-terms", timeout=20)
        assert r.status_code == 401


# --- PayPal configured ---
class TestPayPal:
    def test_plan_shows_paypal_configured_true(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/pro/plan", headers=auth_headers, timeout=20)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["paypal_configured"] is True
        assert d["price"] == "4.99"
        assert d["trial_days"] == 7

    def test_subscription_create_returns_approval_url(self, auth_headers):
        r = requests.post(f"{BASE_URL}/api/subscription/create",
                          headers=auth_headers, json={}, timeout=60)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("subscription_id"), d
        assert d.get("approval_url", "").startswith("https://www.sandbox.paypal.com/"), d

    def test_restore_via_subscription_status(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/subscription/status", headers=auth_headers, timeout=30)
        assert r.status_code == 200, r.text
        u = r.json()["user"]
        # Trial user should still be Pro
        assert u["is_pro"] is True
        assert u["pro_source"] in ("trial", "subscription")


# --- AI Tutor regression ---
class TestTutor:
    def test_tutor_status(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/tutor/status", headers=auth_headers, timeout=20)
        assert r.status_code == 200
        assert r.json()["configured"] is True

    def test_tutor_chat(self, auth_headers):
        r = requests.post(f"{BASE_URL}/api/tutor/chat", headers=auth_headers,
                          json={"message": "What is a stock in 1 sentence?"}, timeout=90)
        assert r.status_code == 200, r.text
        d = r.json()
        assert isinstance(d.get("reply"), str) and len(d["reply"]) > 20


# --- Regression: curriculum, stocks, leaderboard ---
class TestRegression:
    def test_curriculum(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/curriculum", headers=auth_headers, timeout=20)
        assert r.status_code == 200
        d = r.json()
        assert d["units"] and d["total_lessons"] > 0

    def test_stocks_list(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/stocks", headers=auth_headers, timeout=20)
        assert r.status_code == 200
        assert len(r.json()["stocks"]) > 0

    def test_stock_detail(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/stocks/AAPL", headers=auth_headers, timeout=30)
        assert r.status_code == 200
        d = r.json()
        assert d["symbol"] == "AAPL"
        assert d.get("source") in ("finnhub", "simulated")

    def test_leaderboard(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/leaderboard", headers=auth_headers, timeout=20)
        assert r.status_code == 200
        assert len(r.json()["leaderboard"]) > 0

    def test_lesson_complete_awards_xp(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/curriculum", headers=auth_headers, timeout=20)
        first_lesson = r.json()["units"][0]["lessons"][0]["id"]
        r2 = requests.post(f"{BASE_URL}/api/lessons/{first_lesson}/complete",
                           headers=auth_headers, json={"correct": 3, "total": 3}, timeout=20)
        assert r2.status_code == 200
        assert r2.json()["earned_xp"] > 0
