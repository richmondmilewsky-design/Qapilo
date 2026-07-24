"""TradeQuest — new-feature backend tests (AI Tutor, Pro/Trial, PayPal graceful)."""
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
def user(s):
    email = f"newtest_{uuid.uuid4().hex[:8]}@tradequest.app"
    r = s.post(f"{API}/auth/signup", json={"email": email, "password": "test123", "name": "New"})
    assert r.status_code == 200, r.text
    return r.json()


def h(user):
    return {"Authorization": f"Bearer {user['token']}"}


# ------ Pro/Trial on signup ------
def test_signup_grants_trial(user):
    u = user["user"]
    assert u["is_pro"] is True
    assert u["pro_source"] == "trial"
    assert u["trial_days_left"] == 7


def test_pro_plan_endpoint(s, user):
    r = s.get(f"{API}/pro/plan", headers=h(user))
    assert r.status_code == 200
    d = r.json()
    assert d["price"] == "4.99"
    assert d["trial_days"] == 7
    assert d["paypal_configured"] is False
    assert d["is_pro"] is True
    assert isinstance(d["features"], list) and len(d["features"]) >= 2


def test_curriculum_pro_units(s, user):
    r = s.get(f"{API}/curriculum", headers=h(user))
    assert r.status_code == 200
    d = r.json()
    assert d["is_pro"] is True
    ids = {u["id"]: u for u in d["units"]}
    assert ids["u4"]["pro"] is True
    assert ids["u5"]["pro"] is True
    # pro_locked should be False for trial user
    for l in ids["u4"]["lessons"] + ids["u5"]["lessons"]:
        assert l["pro_locked"] is False


def test_lesson_l10_accessible_for_trial(s, user):
    r = s.get(f"{API}/lessons/l10", headers=h(user))
    assert r.status_code == 200
    d = r.json()
    assert d["id"] == "l10"
    assert len(d["cards"]) >= 1


# ------ AI Tutor ------
def test_tutor_status_pro_user(s, user):
    r = s.get(f"{API}/tutor/status", headers=h(user))
    assert r.status_code == 200
    d = r.json()
    assert d["is_pro"] is True
    assert d["remaining"] is None  # unlimited for pro/trial
    assert d["limit"] is None
    assert d["configured"] is True


def test_tutor_chat_returns_reply(s, user):
    r = s.post(f"{API}/tutor/chat", json={"message": "What is a stock in simple terms?"},
               headers=h(user), timeout=90)
    assert r.status_code == 200, r.text
    d = r.json()
    assert "reply" in d
    assert isinstance(d["reply"], str) and len(d["reply"].strip()) > 20
    assert d["is_pro"] is True
    assert d["remaining"] is None


def test_tutor_chat_empty_message(s, user):
    r = s.post(f"{API}/tutor/chat", json={"message": "   "}, headers=h(user))
    assert r.status_code == 400


def test_tutor_history_after_chat(s, user):
    r = s.get(f"{API}/tutor/history", headers=h(user))
    assert r.status_code == 200
    msgs = r.json()["messages"]
    # We sent 1 chat above -> user + assistant messages
    assert len(msgs) >= 2
    # First two should be in order: user then assistant
    user_msgs = [m for m in msgs if m["role"] == "user"]
    asst_msgs = [m for m in msgs if m["role"] == "assistant"]
    assert len(user_msgs) >= 1 and len(asst_msgs) >= 1
    # Ordering: assistant appears after its user message
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"


# ------ PayPal graceful-not-configured ------
def test_subscription_create_503_when_unconfigured(s, user):
    r = s.post(f"{API}/subscription/create", json={}, headers=h(user))
    assert r.status_code == 503


def test_subscription_status_no_error(s, user):
    r = s.get(f"{API}/subscription/status", headers=h(user))
    assert r.status_code == 200
    assert "user" in r.json()
    assert r.json()["user"]["is_pro"] is True


def test_subscription_cancel_no_error(s, user):
    r = s.post(f"{API}/subscription/cancel", headers=h(user))
    assert r.status_code == 200
    d = r.json()
    assert d["user"]["pro_source"] in ("trial", "free")  # sub cancelled but trial still active
    # Subsequent status should show pro_active False (but is_pro still True from trial)
    r2 = s.get(f"{API}/auth/me", headers=h(user))
    assert r2.status_code == 200
