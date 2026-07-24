"""TradeQuest backend regression tests."""
import os
import uuid
import pytest
import requests

BASE = os.environ.get("EXPO_BACKEND_URL", "").rstrip("/") or open("/app/frontend/.env").read().split("EXPO_PUBLIC_BACKEND_URL=")[-1].split("\n")[0].strip()
API = f"{BASE}/api"


@pytest.fixture(scope="module")
def s():
    return requests.Session()


@pytest.fixture(scope="module")
def token(s):
    email = f"test_{uuid.uuid4().hex[:8]}@tradequest.app"
    r = s.post(f"{API}/auth/signup", json={"email": email, "password": "test123", "name": "Tester"})
    assert r.status_code == 200, r.text
    d = r.json()
    assert "token" in d and d["user"]["email"] == email
    return d["token"], email, d["user"]


def auth(token):
    return {"Authorization": f"Bearer {token[0]}"}


# ------ Auth ------
def test_login_demo_or_create(s):
    r = s.post(f"{API}/auth/login", json={"email": "demo@tradequest.app", "password": "demo123"})
    if r.status_code == 401:
        r = s.post(f"{API}/auth/signup", json={"email": "demo@tradequest.app", "password": "demo123"})
    assert r.status_code == 200
    assert "token" in r.json()


def test_login_invalid(s):
    r = s.post(f"{API}/auth/login", json={"email": "nobody@x.com", "password": "wrong123"})
    assert r.status_code == 401


def test_duplicate_signup(s, token):
    r = s.post(f"{API}/auth/signup", json={"email": token[1], "password": "test123"})
    assert r.status_code == 400


def test_me(s, token):
    r = s.get(f"{API}/auth/me", headers=auth(token))
    assert r.status_code == 200
    assert r.json()["user"]["email"] == token[1]


def test_me_no_token(s):
    r = s.get(f"{API}/auth/me")
    assert r.status_code == 401


# ------ Curriculum ------
def test_curriculum(s, token):
    r = s.get(f"{API}/curriculum", headers=auth(token))
    assert r.status_code == 200
    d = r.json()
    assert len(d["units"]) >= 5
    l1 = d["units"][0]["lessons"][0]
    l2 = d["units"][0]["lessons"][1]
    assert l1["unlocked"] is True
    assert l2["unlocked"] is False and l2["completed"] is False


def test_lesson_content(s, token):
    r = s.get(f"{API}/lessons/l1", headers=auth(token))
    assert r.status_code == 200
    d = r.json()
    assert len(d["cards"]) >= 1 and len(d["questions"]) >= 1


def test_lesson_404(s, token):
    r = s.get(f"{API}/lessons/l999", headers=auth(token))
    assert r.status_code == 404


def test_complete_lesson_awards_xp_and_unlocks(s, token):
    r = s.post(f"{API}/lessons/l1/complete", json={"correct": 3, "total": 3}, headers=auth(token))
    assert r.status_code == 200
    d = r.json()
    assert d["earned_xp"] > 0 and d["perfect"] is True
    assert d["user"]["xp"] >= d["earned_xp"]
    assert d["user"]["streak"] >= 1
    badge_ids = [b["id"] for b in d["new_badges"]]
    assert "first_step" in badge_ids
    # verify unlock
    c = s.get(f"{API}/curriculum", headers=auth(token)).json()
    assert c["units"][0]["lessons"][1]["unlocked"] is True
    assert c["units"][0]["lessons"][0]["completed"] is True


# ------ Progress / Badges ------
def test_progress(s, token):
    r = s.get(f"{API}/progress", headers=auth(token))
    assert r.status_code == 200
    d = r.json()
    assert len(d["badges"]) >= 8
    assert any(b["earned"] for b in d["badges"])


# ------ Leaderboard ------
def test_leaderboard(s, token):
    r = s.get(f"{API}/leaderboard", headers=auth(token))
    assert r.status_code == 200
    d = r.json()
    assert len(d["leaderboard"]) >= 5
    assert any(row["is_me"] for row in d["leaderboard"])
    names = [row["name"] for row in d["leaderboard"]]
    assert "Ava Chen" in names


# ------ Stocks ------
def test_stocks_list(s, token):
    r = s.get(f"{API}/stocks", headers=auth(token))
    assert r.status_code == 200
    d = r.json()
    assert len(d["stocks"]) > 0 and len(d["categories"]) > 0
    assert d["stocks"][0]["price"] > 0


def test_stocks_category(s, token):
    r = s.get(f"{API}/stocks?category=Tech", headers=auth(token))
    assert r.status_code == 200
    for st in r.json()["stocks"]:
        assert st["category"] == "Tech"


def test_stock_detail(s, token):
    r = s.get(f"{API}/stocks/AAPL", headers=auth(token))
    assert r.status_code == 200
    d = r.json()
    assert d["symbol"] == "AAPL"
    assert d["price"] > 0
    assert len(d["history"]) > 0
    assert d["explain"]


def test_stock_404(s, token):
    r = s.get(f"{API}/stocks/ZZZZ", headers=auth(token))
    assert r.status_code == 404
