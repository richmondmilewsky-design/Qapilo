"""Iteration 8 — GDPR endpoints tests

- GET /api/account/export : exported_at, data_controller='Qapilo', profile (no password),
  chat_history (array). Auth required.
- DELETE /api/account : deletes user + chat_messages; JWT invalidated; same email cannot log in.
"""
import os
import uuid
import time
import requests
import pytest

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL", "https://stock-learn-24.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"


def _throwaway():
    email = f"test_it8_{uuid.uuid4().hex[:10]}@qapilo.app"
    password = "testpass123"
    r = requests.post(f"{API}/auth/signup", json={"email": email, "password": password}, timeout=30)
    assert r.status_code == 200, f"signup failed: {r.status_code} {r.text}"
    j = r.json()
    return email, password, j["token"], j["user"]["user_id"]


# ---------------- /api/account/export ----------------
class TestAccountExport:
    def test_export_requires_auth(self):
        r = requests.get(f"{API}/account/export", timeout=15)
        assert r.status_code == 401

    def test_export_returns_expected_structure(self):
        email, pwd, token, uid = _throwaway()
        try:
            r = requests.get(
                f"{API}/account/export",
                headers={"Authorization": f"Bearer {token}"},
                timeout=20,
            )
            assert r.status_code == 200, r.text
            data = r.json()
            # Required top-level keys
            for k in ("exported_at", "data_controller", "profile", "chat_history"):
                assert k in data, f"missing key {k}"
            assert data["data_controller"] == "Qapilo"
            assert isinstance(data["chat_history"], list)
            assert isinstance(data["profile"], dict)
            # Profile must NOT contain 'password' key
            assert "password" not in data["profile"], "profile leaked 'password' field"
            # Profile should identify the user; hashed_password is different from 'password'
            assert data["profile"].get("email") == email
            assert data["profile"].get("user_id") == uid
            # exported_at should be an ISO date
            assert "T" in data["exported_at"]
        finally:
            # cleanup
            requests.delete(f"{API}/account", headers={"Authorization": f"Bearer {token}"}, timeout=15)

    def test_export_includes_chat_history_after_advice_refusal(self):
        """Trigger a hard-refusal tutor message (no LLM call) so chat_history is non-empty."""
        email, pwd, token, uid = _throwaway()
        try:
            # Advice-seeking prompt triggers ADVICE_REFUSAL — no LLM call needed
            r = requests.post(
                f"{API}/tutor/chat",
                headers={"Authorization": f"Bearer {token}"},
                json={"message": "what should I buy today", "lang": "en"},
                timeout=30,
            )
            assert r.status_code == 200, r.text
            # Now export
            r2 = requests.get(
                f"{API}/account/export",
                headers={"Authorization": f"Bearer {token}"},
                timeout=20,
            )
            assert r2.status_code == 200
            data = r2.json()
            assert len(data["chat_history"]) >= 2, "expected at least user + assistant message"
            roles = {m.get("role") for m in data["chat_history"]}
            assert {"user", "assistant"}.issubset(roles)
        finally:
            requests.delete(f"{API}/account", headers={"Authorization": f"Bearer {token}"}, timeout=15)


# ---------------- DELETE /api/account ----------------
class TestAccountDelete:
    def test_delete_requires_auth(self):
        r = requests.delete(f"{API}/account", timeout=15)
        assert r.status_code == 401

    def test_delete_removes_user_and_invalidates_token(self):
        email, pwd, token, uid = _throwaway()
        headers = {"Authorization": f"Bearer {token}"}

        # Sanity: token works before deletion
        r0 = requests.get(f"{API}/progress", headers=headers, timeout=15)
        assert r0.status_code == 200

        # Delete
        r1 = requests.delete(f"{API}/account", headers=headers, timeout=30)
        assert r1.status_code == 200, r1.text
        assert r1.json().get("deleted") is True

        # Token should be invalid (user_not_found -> 401)
        r2 = requests.get(f"{API}/progress", headers=headers, timeout=15)
        assert r2.status_code == 401, f"expected 401 after deletion, got {r2.status_code}"

        # Same email can no longer log in -> 401
        r3 = requests.post(f"{API}/auth/login", json={"email": email, "password": pwd}, timeout=15)
        assert r3.status_code == 401, f"expected 401 for deleted email login, got {r3.status_code}"

    def test_delete_removes_chat_messages(self):
        email, pwd, token, uid = _throwaway()
        headers = {"Authorization": f"Bearer {token}"}
        # Seed a chat message (refusal path, no LLM)
        requests.post(
            f"{API}/tutor/chat", headers=headers,
            json={"message": "what should I buy", "lang": "en"}, timeout=30,
        )
        # Confirm history non-empty
        r = requests.get(f"{API}/tutor/history", headers=headers, timeout=15)
        assert r.status_code == 200
        assert len(r.json().get("messages", [])) >= 1

        # Delete account
        rd = requests.delete(f"{API}/account", headers=headers, timeout=30)
        assert rd.status_code == 200

        # Re-signup same email — should be allowed (email freed) and history empty
        r2 = requests.post(f"{API}/auth/signup", json={"email": email, "password": pwd}, timeout=15)
        assert r2.status_code == 200, r2.text
        new_token = r2.json()["token"]
        rh = requests.get(f"{API}/tutor/history", headers={"Authorization": f"Bearer {new_token}"}, timeout=15)
        assert rh.status_code == 200
        assert rh.json().get("messages", []) == [], "chat_messages not cleared on delete"
        # cleanup
        requests.delete(f"{API}/account", headers={"Authorization": f"Bearer {new_token}"}, timeout=15)


# ---------------- Regression: pull-to-refresh endpoints still respond ----------------
class TestRefreshEndpoints:
    """These endpoints are hit by RefreshControl.onRefresh on the tabs/stock detail."""

    @pytest.fixture(scope="class")
    def token(self):
        email = f"TEST_it8refresh_{uuid.uuid4().hex[:8]}@qapilo.app"
        r = requests.post(f"{API}/auth/signup", json={"email": email, "password": "testpass123"}, timeout=15)
        assert r.status_code == 200
        tok = r.json()["token"]
        yield tok
        requests.delete(f"{API}/account", headers={"Authorization": f"Bearer {tok}"}, timeout=15)

    def test_progress(self, token):
        r = requests.get(f"{API}/progress", headers={"Authorization": f"Bearer {token}"}, timeout=15)
        assert r.status_code == 200

    def test_stocks(self, token):
        r = requests.get(f"{API}/stocks", headers={"Authorization": f"Bearer {token}"}, timeout=30)
        assert r.status_code == 200

    def test_stock_detail(self, token):
        r = requests.get(f"{API}/stocks/AAPL", headers={"Authorization": f"Bearer {token}"}, timeout=30)
        assert r.status_code == 200
        j = r.json()
        for k in ("symbol", "price", "history", "change_pct"):
            assert k in j

    def test_leaderboard(self, token):
        r = requests.get(f"{API}/leaderboard", headers={"Authorization": f"Bearer {token}"}, timeout=15)
        assert r.status_code == 200

    def test_curriculum(self, token):
        r = requests.get(f"{API}/curriculum", headers={"Authorization": f"Bearer {token}"}, timeout=15)
        assert r.status_code == 200
