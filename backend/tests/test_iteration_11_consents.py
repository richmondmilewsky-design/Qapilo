"""Tests for split consent flow: required (terms + disclaimer) vs optional (analytics/product/marketing)."""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL", "https://stock-learn-24.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def fresh_user():
    email = f"TEST_consent_{uuid.uuid4().hex[:8]}@example.com"
    pw = "testpass123"
    r = requests.post(f"{API}/auth/signup", json={"email": email, "password": pw, "name": "Consent Tester"})
    assert r.status_code == 200, f"signup failed: {r.status_code} {r.text}"
    body = r.json()
    token = body["token"]
    user = body["user"]
    yield {"email": email, "password": pw, "token": token, "user": user}
    # cleanup
    try:
        requests.delete(f"{API}/account", headers={"Authorization": f"Bearer {token}"})
    except Exception:
        pass


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# --- signup defaults ---
def test_signup_defaults_all_flags_false(fresh_user):
    u = fresh_user["user"]
    assert u["accepted_terms"] is False
    assert u.get("accepted_disclaimer", False) is False
    assert u["consent_analytics"] is False
    assert u["consent_product"] is False
    assert u["consent_marketing"] is False


# --- accept-terms: required flags gating ---
def test_accept_terms_400_when_terms_false(fresh_user):
    r = requests.post(
        f"{API}/auth/accept-terms",
        headers=auth(fresh_user["token"]),
        json={"accepted_terms": False, "accepted_disclaimer": True,
              "consent_analytics": False, "consent_product": False, "consent_marketing": False},
    )
    assert r.status_code == 400
    detail = r.json().get("detail", "")
    # Localized message; ensure it's non-empty
    assert isinstance(detail, str) and len(detail) > 0


def test_accept_terms_400_when_disclaimer_false(fresh_user):
    r = requests.post(
        f"{API}/auth/accept-terms",
        headers=auth(fresh_user["token"]),
        json={"accepted_terms": True, "accepted_disclaimer": False,
              "consent_analytics": True, "consent_product": True, "consent_marketing": True},
    )
    assert r.status_code == 400


def test_accept_terms_200_persists_all_flags(fresh_user):
    r = requests.post(
        f"{API}/auth/accept-terms",
        headers=auth(fresh_user["token"]),
        json={"accepted_terms": True, "accepted_disclaimer": True,
              "consent_analytics": True, "consent_product": False, "consent_marketing": True},
    )
    assert r.status_code == 200, r.text
    u = r.json()["user"]
    assert u["accepted_terms"] is True
    assert u["accepted_disclaimer"] is True
    assert u["consent_analytics"] is True
    assert u["consent_product"] is False
    assert u["consent_marketing"] is True

    # verify via /auth/me
    me = requests.get(f"{API}/auth/me", headers=auth(fresh_user["token"]))
    assert me.status_code == 200
    mu = me.json()["user"]
    assert mu["accepted_terms"] is True
    assert mu["consent_analytics"] is True
    assert mu["consent_product"] is False
    assert mu["consent_marketing"] is True


# --- PATCH /auth/consents (GDPR withdrawal) ---
def test_patch_consents_updates(fresh_user):
    r = requests.patch(
        f"{API}/auth/consents",
        headers=auth(fresh_user["token"]),
        json={"consent_analytics": False, "consent_product": True, "consent_marketing": False},
    )
    assert r.status_code == 200, r.text
    u = r.json()["user"]
    assert u["consent_analytics"] is False
    assert u["consent_product"] is True
    assert u["consent_marketing"] is False
    # required flags must remain true (unchanged)
    assert u["accepted_terms"] is True
    assert u["accepted_disclaimer"] is True

    # verify persistence
    me = requests.get(f"{API}/auth/me", headers=auth(fresh_user["token"])).json()["user"]
    assert me["consent_analytics"] is False
    assert me["consent_product"] is True
    assert me["consent_marketing"] is False


# --- /account/export includes consent flags in profile ---
def test_account_export_includes_consent_flags(fresh_user):
    r = requests.get(f"{API}/account/export", headers=auth(fresh_user["token"]))
    assert r.status_code == 200, r.text
    data = r.json()
    profile = data.get("profile", {})
    assert "consent_analytics" in profile
    assert "consent_product" in profile
    assert "consent_marketing" in profile
    # values should reflect latest patch
    assert profile["consent_analytics"] is False
    assert profile["consent_product"] is True
    assert profile["consent_marketing"] is False
