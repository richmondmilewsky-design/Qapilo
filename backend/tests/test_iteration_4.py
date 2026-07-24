"""Iteration 4 — Finnhub migration + i18n backend tests + regression."""
import os
import uuid
import pytest
import requests

# Frontend env exposes the public URL for the app
_env = open("/app/frontend/.env").read()
BASE = os.environ.get("EXPO_PUBLIC_BACKEND_URL") or _env.split("EXPO_PUBLIC_BACKEND_URL=")[-1].split("\n")[0].strip()
BASE = BASE.rstrip("/")
API = f"{BASE}/api"


@pytest.fixture(scope="module")
def s():
    return requests.Session()


@pytest.fixture(scope="module")
def user(s):
    email = f"TEST_it4_{uuid.uuid4().hex[:8]}@tradequest.app"
    r = s.post(f"{API}/auth/signup", json={"email": email, "password": "test123", "name": "IT4"})
    assert r.status_code == 200, r.text
    return r.json()


def h(u):
    return {"Authorization": f"Bearer {u['token']}"}


# ----------------- Finnhub migration -----------------
def test_stocks_list_source_is_finnhub(s, user):
    r = s.get(f"{API}/stocks", headers=h(user), timeout=30)
    assert r.status_code == 200, r.text
    d = r.json()
    assert "stocks" in d and len(d["stocks"]) > 0
    sources = {item["source"] for item in d["stocks"]}
    # At least one item should be from finnhub. simulated is acceptable fallback per item.
    assert "finnhub" in sources, f"No finnhub-sourced quotes; sources={sources}"
    # Categories present
    assert "categories" in d and "All" in d["categories"]
    # Each item shape
    first = d["stocks"][0]
    for k in ("symbol", "name", "price", "change", "change_pct", "source", "explain", "logo"):
        assert k in first, f"missing {k} in {first}"
    assert isinstance(first["price"], (int, float)) and first["price"] > 0


def test_aapl_detail_history_matches_price(s, user):
    r = s.get(f"{API}/stocks/AAPL", headers=h(user), timeout=30)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["symbol"] == "AAPL"
    assert d["source"] in ("finnhub", "simulated")
    if d["source"] != "finnhub":
        pytest.skip("Finnhub unavailable this call — validated shape only")
    assert isinstance(d["history"], list) and len(d["history"]) == 30
    # LAST value should equal the live price
    assert abs(d["history"][-1] - d["price"]) < 0.01, \
        f"history[-1]={d['history'][-1]} vs price={d['price']}"
    assert d["price"] > 0


# ----------------- i18n backend -----------------
@pytest.mark.parametrize("lang,expected_u1_substr", [
    ("en", "Stock Market"),
    ("de", "Börsen"),
    ("es", "bolsa"),
])
def test_curriculum_localized(s, user, lang, expected_u1_substr):
    r = s.get(f"{API}/curriculum?lang={lang}", headers=h(user))
    assert r.status_code == 200, r.text
    d = r.json()
    u1 = next((u for u in d["units"] if u["id"] == "u1"), None)
    assert u1 is not None
    assert expected_u1_substr.lower() in u1["title"].lower(), \
        f"Expected '{expected_u1_substr}' in u1 title '{u1['title']}' for lang={lang}"


def test_stocks_explain_localized_de(s, user):
    r_en = s.get(f"{API}/stocks?lang=en", headers=h(user), timeout=30)
    r_de = s.get(f"{API}/stocks?lang=de", headers=h(user), timeout=30)
    assert r_en.status_code == 200 and r_de.status_code == 200
    aapl_en = next(x for x in r_en.json()["stocks"] if x["symbol"] == "AAPL")
    aapl_de = next(x for x in r_de.json()["stocks"] if x["symbol"] == "AAPL")
    assert aapl_en["explain"] != aapl_de["explain"]
    assert "iPhone" in aapl_de["explain"]
    assert "Welt" in aapl_de["explain"] or "wertvollsten" in aapl_de["explain"]


def test_stocks_explain_localized_es(s, user):
    r_es = s.get(f"{API}/stocks?lang=es", headers=h(user), timeout=30)
    assert r_es.status_code == 200
    aapl_es = next(x for x in r_es.json()["stocks"] if x["symbol"] == "AAPL")
    assert "mundo" in aapl_es["explain"].lower() or "valiosas" in aapl_es["explain"].lower()


def test_lesson_localized_de(s, user):
    r = s.get(f"{API}/lessons/l1?lang=de", headers=h(user))
    assert r.status_code == 200
    d = r.json()
    assert "Aktie" in d["title"]
    # Cards translated
    assert any("Aktie" in c["body"] or "Aktien" in c["body"] for c in d["cards"])
    # Questions translated but answer indices preserved
    assert len(d["questions"]) >= 3
    for q in d["questions"]:
        assert isinstance(q["answer"], int)


def test_lang_fallback_invalid(s, user):
    r = s.get(f"{API}/curriculum?lang=xx", headers=h(user))
    assert r.status_code == 200
    u1 = next(u for u in r.json()["units"] if u["id"] == "u1")
    # Falls back to EN
    assert "Stock" in u1["title"] or "Market" in u1["title"]


# ----------------- Regression -----------------
def test_auth_me(s, user):
    r = s.get(f"{API}/auth/me", headers=h(user))
    assert r.status_code == 200
    assert r.json()["user"]["email"] == user["user"]["email"]


def test_login_flow(s, user):
    r = s.post(f"{API}/auth/login", json={"email": user["user"]["email"], "password": "test123"})
    assert r.status_code == 200
    assert "token" in r.json()


def test_accept_terms(s, user):
    r = s.post(f"{API}/auth/accept-terms", headers=h(user))
    assert r.status_code == 200
    assert r.json()["user"]["accepted_terms"] is True


def test_leaderboard(s, user):
    r = s.get(f"{API}/leaderboard", headers=h(user))
    assert r.status_code == 200
    assert isinstance(r.json()["leaderboard"], list) and len(r.json()["leaderboard"]) > 0


def test_complete_lesson_awards_xp(s, user):
    r = s.post(f"{API}/lessons/l1/complete", json={"correct": 3, "total": 3}, headers=h(user))
    assert r.status_code == 200
    d = r.json()
    assert d["earned_xp"] > 0
    assert d["perfect"] is True
    assert d["user"]["xp"] >= d["earned_xp"]


def test_progress_endpoint(s, user):
    r = s.get(f"{API}/progress", headers=h(user))
    assert r.status_code == 200
    d = r.json()
    assert "badges" in d and len(d["badges"]) > 0


# ----------------- AI Tutor -----------------
def test_tutor_status(s, user):
    r = s.get(f"{API}/tutor/status", headers=h(user))
    assert r.status_code == 200
    d = r.json()
    assert d["configured"] is True
    assert d["is_pro"] is True  # trial


def test_tutor_chat_returns_reply(s, user):
    r = s.post(f"{API}/tutor/chat",
               json={"message": "What is a stock in one sentence?", "lang": "en"},
               headers=h(user), timeout=90)
    assert r.status_code == 200, r.text
    d = r.json()
    assert isinstance(d["reply"], str) and len(d["reply"].strip()) > 20
