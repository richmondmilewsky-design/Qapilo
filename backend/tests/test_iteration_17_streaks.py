"""
Iteration 17 backend tests
- Verifies new streak_30 & streak_100 badges awarded by evaluate_badges via /lessons/{id}/complete
- Verifies public_user now returns 'created_at' on signup, login, /auth/me
- Regression: signup email_verified=false; verify-email wrong code=>400; resend rate limit; demo login
"""
import os
import re
import uuid
import time
import pytest
import requests
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import asyncio

load_dotenv("/app/backend/.env")

BASE = os.environ.get("EXPO_BACKEND_URL")
if not BASE:
    # fall back to frontend .env EXPO_PUBLIC_BACKEND_URL
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("EXPO_PUBLIC_BACKEND_URL="):
                BASE = line.split("=", 1)[1].strip().strip('"')
                break
BASE = (BASE or "").rstrip("/")
API = f"{BASE}/api"

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]


def _db():
    return AsyncIOMotorClient(MONGO_URL)[DB_NAME]


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.fixture(scope="module")
def s():
    return requests.Session()


@pytest.fixture(scope="module")
def fresh_user(s):
    email = f"TEST_streak_{uuid.uuid4().hex[:8]}@example.com"
    r = s.post(f"{API}/auth/signup", json={"email": email, "password": "Abc123!xyz", "name": "Streak Tester"})
    assert r.status_code == 200, r.text
    body = r.json()
    return {"email": email, "token": body["token"], "user": body["user"]}


def h(tok):
    return {"Authorization": f"Bearer {tok}"}


# ---------- public_user.created_at ----------
def test_signup_returns_created_at(fresh_user):
    u = fresh_user["user"]
    assert "created_at" in u and u["created_at"], "signup public_user missing created_at"
    # ISO parseable
    datetime.fromisoformat(u["created_at"].replace("Z", "+00:00"))


def test_login_returns_created_at(s):
    # login demo user
    r = s.post(f"{API}/auth/login", json={"email": "demo@tradequest.app", "password": "demo123"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert "created_at" in body["user"] and body["user"]["created_at"]


def test_me_returns_created_at(s, fresh_user):
    r = s.get(f"{API}/auth/me", headers=h(fresh_user["token"]))
    assert r.status_code == 200
    assert r.json()["user"].get("created_at")


# ---------- signup regression ----------
def test_signup_email_verified_false(fresh_user):
    assert fresh_user["user"]["email_verified"] is False


# ---------- verify-email wrong code returns 400 ----------
def test_verify_email_wrong_code_400(s, fresh_user):
    r = s.post(f"{API}/auth/verify-email",
               json={"code": "000000", "lang": "en"}, headers=h(fresh_user["token"]))
    assert r.status_code in (400, 429), r.text  # after too many attempts becomes 429


# ---------- resend-verification rate limit (3 per 15min) ----------
def test_resend_verification_rate_limit(s):
    # Create isolated user for rate limit test
    email = f"TEST_rl_{uuid.uuid4().hex[:8]}@example.com"
    r = s.post(f"{API}/auth/signup", json={"email": email, "password": "Abc123!xyz"})
    assert r.status_code == 200
    tok = r.json()["token"]
    # Signup already consumed 1 send (initial code). Resend 3 more times -> at least one should be 429.
    codes = []
    for _ in range(4):
        rr = s.post(f"{API}/auth/resend-verification", json={"lang": "en"}, headers=h(tok))
        codes.append(rr.status_code)
    # Expect at least one 429 among the resends (bucket includes initial issue if same key)
    assert 429 in codes or codes.count(200) <= 3, f"resend codes: {codes}"


# ---------- demo login still works ----------
def test_demo_login_works(s):
    r = s.post(f"{API}/auth/login", json={"email": "demo@tradequest.app", "password": "demo123"})
    assert r.status_code == 200
    u = r.json()["user"]
    assert u["email"] == "demo@tradequest.app"


# ---------- GET /api/badges lists streak_7, streak_30, streak_100 ----------
def test_badges_catalog_contains_streak_family(s, fresh_user):
    r = s.get(f"{API}/badges", headers=h(fresh_user["token"]))
    assert r.status_code == 200
    ids = {b["id"] for b in r.json()["badges"]}
    for bid in ("streak_7", "streak_30", "streak_100"):
        assert bid in ids, f"missing badge {bid}"


# ---------- Award streak badges via lesson complete ----------
async def _set_streak(user_id: str, streak: int):
    from datetime import datetime as _dt, timezone as _tz
    today = _dt.now(_tz.utc).strftime("%Y-%m-%d")
    db = _db()
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"streak": streak, "longest_streak": max(streak, 0), "last_active": today},
         "$pull": {"badges": {"$in": ["streak_7", "streak_30", "streak_100"]}}}
    )


async def _pop_completed(user_id: str, lesson_id: str):
    """Remove lesson from completed_lessons so we can re-complete idempotently for badge check."""
    db = _db()
    await db.users.update_one(
        {"user_id": user_id},
        {"$pull": {"completed_lessons": lesson_id, "perfect_lessons": lesson_id}}
    )


def _complete_lesson(s, tok, lesson_id="l1"):
    r = s.post(f"{API}/lessons/{lesson_id}/complete",
               json={"correct": 5, "total": 5}, headers=h(tok))
    assert r.status_code == 200, r.text
    return r.json()


def test_streak_7_badge_awarded(s, fresh_user):
    uid = fresh_user["user"]["user_id"]
    run(_set_streak(uid, 7))
    run(_pop_completed(uid, "l1"))
    resp = _complete_lesson(s, fresh_user["token"], "l1")
    badges = set(resp["user"]["badges"])
    assert "streak_7" in badges, f"streak_7 not awarded; badges={badges}, new={resp.get('new_badges')}"


def test_streak_30_badge_awarded(s, fresh_user):
    uid = fresh_user["user"]["user_id"]
    run(_set_streak(uid, 30))
    run(_pop_completed(uid, "l2"))
    resp = _complete_lesson(s, fresh_user["token"], "l2")
    badges = set(resp["user"]["badges"])
    assert "streak_30" in badges, f"streak_30 not awarded; badges={badges}, new={resp.get('new_badges')}"


def test_streak_100_badge_awarded(s, fresh_user):
    uid = fresh_user["user"]["user_id"]
    run(_set_streak(uid, 100))
    run(_pop_completed(uid, "l3"))
    resp = _complete_lesson(s, fresh_user["token"], "l3")
    badges = set(resp["user"]["badges"])
    assert "streak_100" in badges, f"streak_100 not awarded; badges={badges}, new={resp.get('new_badges')}"


def test_badges_earned_flag_after_awards(s, fresh_user):
    r = s.get(f"{API}/badges", headers=h(fresh_user["token"]))
    assert r.status_code == 200
    m = {b["id"]: b for b in r.json()["badges"]}
    for bid in ("streak_7", "streak_30", "streak_100"):
        assert m[bid]["earned"] is True, f"{bid} not marked earned"
