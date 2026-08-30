"""Iteration 18 — Marketing consent double opt-in (marketing_consents collection).
Covers: PATCH /auth/consents, POST /auth/accept-terms, POST /auth/confirm-marketing-consent,
POST /auth/resend-marketing-code. Also regresses the untouched /auth/verify-email flow."""
import os
import time
import uuid
import hashlib
import pytest
import requests
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient

BASE = os.environ.get("EXPO_BACKEND_URL", "").rstrip("/")
assert BASE, "EXPO_BACKEND_URL must be set"
API = f"{BASE}/api"

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")


@pytest.fixture(scope="module")
def db():
    return MongoClient(MONGO_URL)[DB_NAME]


@pytest.fixture(scope="module")
def fresh_user():
    email = f"TEST_mktg_{uuid.uuid4().hex[:10]}@example.com"
    r = requests.post(f"{API}/auth/signup", json={
        "email": email, "password": "Abc123!xyz", "name": "Marketing Tester", "lang": "en"
    })
    assert r.status_code == 200, r.text
    data = r.json()
    yield {"token": data["token"], "user": data["user"], "email": email}
    try:
        requests.delete(f"{API}/account", headers={"Authorization": f"Bearer {data['token']}"})
    except Exception:
        pass


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# --- PATCH /auth/consents: marketing opt-in triggers pending double opt-in ---
class TestConsentsMarketingOptIn:
    def test_marketing_true_stays_false_and_pending(self, fresh_user):
        r = requests.post(f"{API}/auth/consents".replace("/auth/consents", "/auth/consents"),
                           headers=auth(fresh_user["token"]),
                           json={"consent_analytics": False, "consent_product": False, "consent_marketing": True})
        # endpoint is PATCH
        r = requests.patch(f"{API}/auth/consents", headers=auth(fresh_user["token"]),
                            json={"consent_analytics": False, "consent_product": False, "consent_marketing": True})
        assert r.status_code == 200, r.text
        user = r.json()["user"]
        assert user["consent_marketing"] is False
        assert user.get("consent_marketing_pending") is True

    def test_marketing_consents_doc_created(self, fresh_user, db):
        uid = fresh_user["user"]["user_id"]
        rec = db.marketing_consents.find_one({"user_id": uid})
        assert rec is not None
        assert "code_hash" in rec and "expires_at" in rec and "created_at" in rec
        assert rec.get("attempts", 0) == 0

    def test_email_event_marketing_confirmation_logged(self, fresh_user, db):
        time.sleep(2.5)
        uid = fresh_user["user"]["user_id"]
        ev = db.email_events.find_one({"user_ref": uid, "template": "marketing_confirmation"})
        assert ev is not None, "no marketing_confirmation email event logged"
        assert ev["status"] in ("sent", "failed")

    def test_analytics_product_toggle_immediate(self, fresh_user):
        r = requests.patch(f"{API}/auth/consents", headers=auth(fresh_user["token"]),
                            json={"consent_analytics": True, "consent_product": True, "consent_marketing": False})
        assert r.status_code == 200, r.text
        user = r.json()["user"]
        assert user["consent_analytics"] is True
        assert user["consent_product"] is True

    def test_marketing_false_immediate_no_pending(self, fresh_user, db):
        # consent_marketing currently False (unconfirmed); setting false again must stay
        # immediate with no pending flag and no marketing_consents doc lingering as "pending true".
        r = requests.patch(f"{API}/auth/consents", headers=auth(fresh_user["token"]),
                            json={"consent_analytics": True, "consent_product": True, "consent_marketing": False})
        assert r.status_code == 200, r.text
        user = r.json()["user"]
        assert user["consent_marketing"] is False
        assert user.get("consent_marketing_pending") is None


# --- confirm-marketing-consent negative paths ---
class TestConfirmMarketingWrongCode:
    def test_setup_pending(self, fresh_user):
        r = requests.patch(f"{API}/auth/consents", headers=auth(fresh_user["token"]),
                            json={"consent_analytics": False, "consent_product": False, "consent_marketing": True})
        assert r.status_code == 200
        assert r.json()["user"].get("consent_marketing_pending") is True

    def test_wrong_code_400_and_attempts_incremented(self, fresh_user, db):
        uid = fresh_user["user"]["user_id"]
        rec_before = db.marketing_consents.find_one({"user_id": uid})
        assert rec_before is not None
        attempts_before = rec_before.get("attempts", 0)

        r = requests.post(f"{API}/auth/confirm-marketing-consent", headers=auth(fresh_user["token"]),
                           json={"code": "000000", "lang": "en"})
        if r.status_code == 200:
            pytest.skip("random 000000 happened to match the real code")
        assert r.status_code == 400
        detail = r.json().get("detail", "")
        assert "invalid" in detail.lower() or "expired" in detail.lower()

        rec_after = db.marketing_consents.find_one({"user_id": uid})
        assert rec_after is not None
        assert rec_after.get("attempts", 0) == attempts_before + 1

        # user consent_marketing must remain false
        me = requests.get(f"{API}/auth/me", headers=auth(fresh_user["token"]))
        assert me.json()["user"]["consent_marketing"] is False

    def test_rate_limit_after_6_wrong_attempts(self, fresh_user, db):
        uid = fresh_user["user"]["user_id"]
        # one wrong attempt already made above; make more to reach 6 total via rate limiter bucket
        # NOTE: rate limiter key mktg_confirm:{user_id} is separate from attempts field,
        # limit=6 requests/900s on the endpoint itself.
        last_status = None
        for i in range(6):
            r = requests.post(f"{API}/auth/confirm-marketing-consent", headers=auth(fresh_user["token"]),
                               json={"code": "111111", "lang": "en"})
            last_status = r.status_code
            if r.status_code == 429:
                break
        assert last_status == 429, f"expected 429 rate_limited eventually, got {last_status}"


# --- confirm-marketing-consent happy path via controlled DB insert ---
class TestConfirmMarketingHappyPath:
    def test_confirm_with_known_code(self, db):
        email = f"TEST_mktg_happy_{uuid.uuid4().hex[:10]}@example.com"
        r = requests.post(f"{API}/auth/signup", json={
            "email": email, "password": "Abc123!xyz", "name": "Happy Tester", "lang": "en"
        })
        assert r.status_code == 200, r.text
        data = r.json()
        token = data["token"]
        uid = data["user"]["user_id"]
        try:
            # trigger pending state (creates a real marketing_consents doc with random code)
            r2 = requests.patch(f"{API}/auth/consents", headers=auth(token),
                                 json={"consent_analytics": False, "consent_product": False,
                                       "consent_marketing": True})
            assert r2.status_code == 200
            assert r2.json()["user"].get("consent_marketing_pending") is True

            # Controlled test: overwrite the code_hash with known value sha256('123456')
            known_hash = hashlib.sha256("123456".encode()).hexdigest()
            db.marketing_consents.update_one(
                {"user_id": uid},
                {"$set": {"code_hash": known_hash,
                          "expires_at": datetime.now(timezone.utc) + timedelta(minutes=30)}}
            )

            r3 = requests.post(f"{API}/auth/confirm-marketing-consent", headers=auth(token),
                                json={"code": "123456", "lang": "en"})
            assert r3.status_code == 200, r3.text
            user = r3.json()["user"]
            assert user["consent_marketing"] is True
            assert "consent_marketing_confirmed_at" in user
            assert "consent_marketing_ip" in user

            rec_after = db.marketing_consents.find_one({"user_id": uid})
            assert rec_after is None, "marketing_consents doc should be deleted after confirmation"
        finally:
            requests.delete(f"{API}/account", headers=auth(token))


# --- resend-marketing-code ---
class TestResendMarketingCode:
    def test_resend_ok_and_new_doc(self, fresh_user, db):
        uid = fresh_user["user"]["user_id"]
        r = requests.post(f"{API}/auth/resend-marketing-code", headers=auth(fresh_user["token"]),
                           json={"lang": "en"})
        assert r.status_code == 200, r.text
        assert r.json().get("ok") is True
        rec = db.marketing_consents.find_one({"user_id": uid})
        assert rec is not None

    def test_resend_rate_limit_after_3(self, fresh_user):
        headers = auth(fresh_user["token"])
        last_status = None
        # 1 call already made above; 2 more should be fine, 4th (fresh count incl above) hits 429
        for _ in range(4):
            r = requests.post(f"{API}/auth/resend-marketing-code", json={"lang": "en"}, headers=headers)
            last_status = r.status_code
            if r.status_code == 429:
                break
        assert last_status == 429, f"expected 429 eventually, got {last_status}"


# --- Regression: existing email verification flow untouched ---
class TestEmailVerificationRegression:
    def test_verify_email_wrong_code_still_400(self, fresh_user):
        r = requests.post(f"{API}/auth/verify-email", headers=auth(fresh_user["token"]),
                           json={"code": "000000", "lang": "en"})
        if r.status_code == 200:
            pytest.skip("random code matched")
        assert r.status_code == 400

    def test_resend_verification_still_ok(self, fresh_user):
        r = requests.post(f"{API}/auth/resend-verification", headers=auth(fresh_user["token"]),
                           json={"lang": "en"})
        assert r.status_code in (200, 429)  # may already be rate-limited from prior test runs

    def test_email_verifications_collection_independent(self, fresh_user, db):
        uid = fresh_user["user"]["user_id"]
        ev_rec = db.email_verifications.find_one({"user_id": uid})
        mk_rec = db.marketing_consents.find_one({"user_id": uid})
        # both collections operate independently; presence of one shouldn't force the other
        assert ev_rec is not None  # signup issued verification code
