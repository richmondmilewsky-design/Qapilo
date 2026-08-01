"""Iteration 12 — Communications & privacy infrastructure.

Covers:
- POST /api/auth/forgot-password (neutral response, no enumeration, per-email rate limit)
- POST /api/auth/reset-password (invalid token, weak password, valid token, single-use)
- Session invalidation on password reset (old JWT rejected, old login fails, new login OK)
- POST /api/support/request (valid, missing fields, header-injection, per-IP rate limit)
- email_events log doc + password_resets hash-only storage

Run:
  pytest /app/backend/tests/test_iteration_12_comms.py -v \
    --junitxml=/app/test_reports/pytest/pytest_iteration_12.xml
"""
import hashlib
import os
import secrets as pysecrets
import time
from datetime import datetime, timedelta, timezone

import pytest
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path("/app/backend/.env"))

BASE_URL = os.environ["EXPO_PUBLIC_BACKEND_URL"].rstrip("/") if os.environ.get("EXPO_PUBLIC_BACKEND_URL") else None
# Fallback: read from frontend .env (test runs in same container)
if not BASE_URL:
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("EXPO_PUBLIC_BACKEND_URL="):
                BASE_URL = line.split("=", 1)[1].strip().strip('"').rstrip("/")
                break

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def db():
    c = MongoClient(MONGO_URL)
    yield c[DB_NAME]
    c.close()


@pytest.fixture()
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def _unique_email(prefix="test12"):
    return f"TEST_{prefix}_{pysecrets.token_hex(4)}@example.com"


def _signup(session, email, password="pass1234", name="Test User"):
    r = session.post(f"{API}/auth/signup",
                     json={"email": email, "password": password, "name": name})
    assert r.status_code == 200, f"signup failed: {r.status_code} {r.text}"
    return r.json()


def _cleanup_user(db, email):
    u = db.users.find_one({"email": email.lower()})
    if u:
        db.users.delete_one({"user_id": u["user_id"]})
        db.password_resets.delete_many({"user_id": u["user_id"]})


# ---------------------- forgot-password ----------------------

class TestForgotPassword:
    def test_unknown_email_returns_neutral_200(self, session):
        email = _unique_email("unk")
        r = session.post(f"{API}/auth/forgot-password", json={"email": email})
        assert r.status_code == 200
        j = r.json()
        assert j.get("ok") is True
        assert "message" in j and isinstance(j["message"], str) and len(j["message"]) > 0

    def test_known_email_returns_same_neutral_200(self, session, db):
        email = _unique_email("known")
        _signup(session, email)
        try:
            r = session.post(f"{API}/auth/forgot-password", json={"email": email})
            assert r.status_code == 200
            assert r.json().get("ok") is True
            # A password_resets doc should exist for this user (hash only).
            u = db.users.find_one({"email": email.lower()})
            rec = db.password_resets.find_one({"user_id": u["user_id"]})
            assert rec is not None
            assert "token_hash" in rec and len(rec["token_hash"]) == 64
            # Must NOT store the raw token.
            assert "token" not in rec
        finally:
            _cleanup_user(db, email)

    def test_rate_limit_per_email(self, session, db):
        email = _unique_email("rate")
        _signup(session, email)
        try:
            codes = []
            # Limit is 3/900s; 4th same-email call should be 429.
            for _ in range(4):
                codes.append(session.post(f"{API}/auth/forgot-password",
                                          json={"email": email}).status_code)
            assert codes[:3] == [200, 200, 200], f"first 3 not all 200: {codes}"
            assert codes[3] == 429, f"4th expected 429, got {codes[3]}"
        finally:
            _cleanup_user(db, email)


# ---------------------- reset-password ----------------------

class TestResetPassword:
    def _inject_token(self, db, user_id, ttl_min=30):
        raw = pysecrets.token_urlsafe(32)
        db.password_resets.delete_many({"user_id": user_id})
        db.password_resets.insert_one({
            "user_id": user_id,
            "token_hash": hashlib.sha256(raw.encode()).hexdigest(),
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=ttl_min),
            "used": False,
        })
        return raw

    def test_invalid_token(self, session):
        r = session.post(f"{API}/auth/reset-password",
                         json={"token": "not-a-real-token", "new_password": "abcdef123"})
        assert r.status_code == 400

    def test_weak_password(self, session, db):
        email = _unique_email("weak")
        _signup(session, email)
        try:
            u = db.users.find_one({"email": email.lower()})
            raw = self._inject_token(db, u["user_id"])
            r = session.post(f"{API}/auth/reset-password",
                             json={"token": raw, "new_password": "short"})
            assert r.status_code == 400
        finally:
            _cleanup_user(db, email)

    def test_valid_token_then_reuse_fails(self, session, db):
        email = _unique_email("valid")
        _signup(session, email, password="oldpass1")
        try:
            u = db.users.find_one({"email": email.lower()})
            raw = self._inject_token(db, u["user_id"])
            r1 = session.post(f"{API}/auth/reset-password",
                              json={"token": raw, "new_password": "newpass1234"})
            assert r1.status_code == 200, r1.text
            # Reusing same token should now fail.
            r2 = session.post(f"{API}/auth/reset-password",
                              json={"token": raw, "new_password": "anotherpw1234"})
            assert r2.status_code == 400
        finally:
            _cleanup_user(db, email)


# ---------------------- session invalidation ----------------------

class TestSessionInvalidation:
    def test_old_jwt_rejected_and_login_flip(self, session, db):
        email = _unique_email("sess")
        old_password = "oldpass1"
        new_password = "brandnew1234"
        sign = _signup(session, email, password=old_password)
        old_token = sign["token"]
        # Confirm old token works before reset.
        r_pre = session.get(f"{API}/account/export",
                            headers={"Authorization": f"Bearer {old_token}"})
        assert r_pre.status_code == 200, r_pre.text
        # Ensure sessions_invalid_before ticks past iat (JWT iat has 1-second granularity).
        time.sleep(1.2)
        try:
            u = db.users.find_one({"email": email.lower()})
            raw = pysecrets.token_urlsafe(32)
            db.password_resets.insert_one({
                "user_id": u["user_id"],
                "token_hash": hashlib.sha256(raw.encode()).hexdigest(),
                "created_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc) + timedelta(minutes=30),
                "used": False,
            })
            r = session.post(f"{API}/auth/reset-password",
                             json={"token": raw, "new_password": new_password})
            assert r.status_code == 200

            # Old JWT should now be rejected.
            r_old = session.get(f"{API}/account/export",
                                headers={"Authorization": f"Bearer {old_token}"})
            assert r_old.status_code == 401, f"old JWT still accepted: {r_old.status_code}"

            # Old password login must fail.
            r_login_old = session.post(f"{API}/auth/login",
                                       json={"email": email, "password": old_password})
            assert r_login_old.status_code == 401

            # New password login succeeds.
            r_login_new = session.post(f"{API}/auth/login",
                                       json={"email": email, "password": new_password})
            assert r_login_new.status_code == 200
            assert "token" in r_login_new.json()
        finally:
            _cleanup_user(db, email)


# ---------------------- support request ----------------------

class TestSupport:
    def test_valid_returns_ref(self, session):
        r = session.post(f"{API}/support/request", json={
            "category": "learning",
            "subject": "Question about lessons",
            "message": "I have a small question.",
            "reply_email": _unique_email("sup"),
            "lang": "en",
        })
        assert r.status_code == 200, r.text
        j = r.json()
        assert j.get("ok") is True
        assert isinstance(j.get("ref"), str) and j["ref"].startswith("QS-")
        assert len(j["ref"]) >= 6

    def test_missing_subject(self, session):
        r = session.post(f"{API}/support/request", json={
            "category": "learning", "subject": "", "message": "hi",
        })
        assert r.status_code == 400

    def test_missing_message(self, session):
        r = session.post(f"{API}/support/request", json={
            "category": "learning", "subject": "Hi", "message": "  ",
        })
        assert r.status_code == 400

    def test_header_injection_guard(self, session):
        r = session.post(f"{API}/support/request", json={
            "category": "learning",
            "subject": "Hello\r\nBcc: attacker@example.com",
            "message": "content",
        })
        assert r.status_code == 400


# ---------------------- email_events / hash-only storage ----------------------

class TestEmailEventsAndStorage:
    def test_password_resets_stores_hash_not_raw(self, session, db):
        email = _unique_email("hash")
        _signup(session, email)
        try:
            session.post(f"{API}/auth/forgot-password", json={"email": email})
            u = db.users.find_one({"email": email.lower()})
            rec = db.password_resets.find_one({"user_id": u["user_id"]})
            assert rec is not None
            assert "token_hash" in rec
            assert len(rec["token_hash"]) == 64  # sha256 hex
            for banned in ("token", "raw_token", "plain_token"):
                assert banned not in rec, f"raw token leak in password_resets: {banned}"
        finally:
            _cleanup_user(db, email)

    def test_email_events_minimal_shape(self, session, db):
        email = _unique_email("evt")
        _signup(session, email)
        try:
            session.post(f"{API}/auth/forgot-password", json={"email": email})
            u = db.users.find_one({"email": email.lower()})
            # Fire-and-forget task; poll briefly.
            evt = None
            for _ in range(20):
                evt = db.email_events.find_one(
                    {"template": "password_reset", "user_ref": u["user_id"]},
                    sort=[("created_at", -1)],
                )
                if evt:
                    break
                time.sleep(0.2)
            assert evt is not None, "email_event was not written"
            # Required minimal fields.
            for f in ("event_id", "template", "status", "language", "created_at"):
                assert f in evt
            assert evt["template"] == "password_reset"
            assert evt["status"] in ("sent", "failed", "pending")
            # Must NOT store raw token, body/html, or full email.
            for banned in ("token", "raw_token", "link", "html", "body", "to", "email"):
                assert banned not in evt, f"email_events leaked field: {banned}"
        finally:
            _cleanup_user(db, email)
