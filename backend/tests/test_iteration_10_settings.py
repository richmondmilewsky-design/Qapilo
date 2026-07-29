"""Backend tests for iteration 10 - Settings screen new endpoints.

Covers:
- PATCH /api/account (GDPR right to rectification - name)
- DELETE /api/tutor/history (clear AI chat history)
- Regression: /auth/me, /account/export chat_history, existing docs still 200.
"""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL") or os.environ.get("EXPO_BACKEND_URL")
if not BASE_URL:
    # Fallback to reading .env directly
    try:
        with open("/app/frontend/.env") as f:
            for ln in f:
                if ln.startswith("EXPO_PUBLIC_BACKEND_URL="):
                    BASE_URL = ln.split("=", 1)[1].strip()
                    break
    except Exception:
        pass
BASE_URL = (BASE_URL or "").rstrip("/")


def _signup():
    email = f"test_settings_{uuid.uuid4().hex[:10]}@example.com"
    pw = "Test1234!"
    r = requests.post(f"{BASE_URL}/api/auth/signup", json={"email": email, "password": pw, "name": "Test User"})
    assert r.status_code == 200, f"signup failed: {r.status_code} {r.text}"
    body = r.json()
    return body["token"], body["user"], email, pw


def _auth(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def user_ctx():
    token, user, email, pw = _signup()
    yield {"token": token, "user": user, "email": email, "pw": pw}
    # cleanup - delete account
    try:
        requests.delete(f"{BASE_URL}/api/account", headers=_auth(token))
    except Exception:
        pass


class TestPatchAccount:
    """PATCH /api/account - name rectification."""

    def test_patch_account_updates_name(self, user_ctx):
        token = user_ctx["token"]
        new_name = "TEST_Corrected Name"
        r = requests.patch(f"{BASE_URL}/api/account", headers=_auth(token), json={"name": new_name})
        assert r.status_code == 200, r.text
        data = r.json()
        assert "user" in data
        assert data["user"]["name"] == new_name

        # Verify via /auth/me (persistence)
        me = requests.get(f"{BASE_URL}/api/auth/me", headers=_auth(token))
        assert me.status_code == 200
        assert me.json()["user"]["name"] == new_name

    def test_patch_account_empty_name_rejected(self, user_ctx):
        token = user_ctx["token"]
        r = requests.patch(f"{BASE_URL}/api/account", headers=_auth(token), json={"name": "   "})
        assert r.status_code == 400, r.text

    def test_patch_account_missing_field_422(self, user_ctx):
        token = user_ctx["token"]
        r = requests.patch(f"{BASE_URL}/api/account", headers=_auth(token), json={})
        assert r.status_code in (400, 422)

    def test_patch_account_requires_auth(self):
        r = requests.patch(f"{BASE_URL}/api/account", json={"name": "x"})
        assert r.status_code in (401, 403)

    def test_patch_account_trims_and_truncates(self, user_ctx):
        token = user_ctx["token"]
        long_name = "TEST_" + "a" * 200
        r = requests.patch(f"{BASE_URL}/api/account", headers=_auth(token), json={"name": long_name})
        assert r.status_code == 200
        # Server truncates to 60
        assert len(r.json()["user"]["name"]) <= 60


class TestClearTutorHistory:
    """DELETE /api/tutor/history - clear AI chat messages."""

    def test_clear_history_empty_returns_zero(self, user_ctx):
        token = user_ctx["token"]
        r = requests.delete(f"{BASE_URL}/api/tutor/history", headers=_auth(token))
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("deleted") is True
        assert "count" in body
        assert isinstance(body["count"], int)

    def test_clear_history_after_chat(self, user_ctx):
        """Send a tutor message, then clear, then verify export chat_history empty."""
        token = user_ctx["token"]

        # Send a chat message (this may be slow — LLM call)
        try:
            chat = requests.post(
                f"{BASE_URL}/api/tutor/chat",
                headers=_auth(token),
                json={"message": "What is a stock?"},
                timeout=60,
            )
        except Exception as e:
            pytest.skip(f"tutor chat unreachable: {e}")

        if chat.status_code != 200:
            pytest.skip(f"tutor chat returned {chat.status_code} (LLM may be gated): {chat.text[:200]}")

        # Verify export has chat_history entries
        exp = requests.get(f"{BASE_URL}/api/account/export", headers=_auth(token))
        assert exp.status_code == 200
        history_before = exp.json().get("chat_history", [])
        assert len(history_before) >= 1, "expected at least 1 chat message after /tutor/chat"

        # Clear
        r = requests.delete(f"{BASE_URL}/api/tutor/history", headers=_auth(token))
        assert r.status_code == 200
        body = r.json()
        assert body["deleted"] is True
        assert body["count"] >= len(history_before)

        # Verify export chat_history now empty
        exp2 = requests.get(f"{BASE_URL}/api/account/export", headers=_auth(token))
        assert exp2.status_code == 200
        assert exp2.json().get("chat_history", []) == []

    def test_clear_history_requires_auth(self):
        r = requests.delete(f"{BASE_URL}/api/tutor/history")
        assert r.status_code in (401, 403)


class TestRegression:
    """Ensure new routes did not break existing endpoints."""

    def test_auth_me(self, user_ctx):
        r = requests.get(f"{BASE_URL}/api/auth/me", headers=_auth(user_ctx["token"]))
        assert r.status_code == 200
        u = r.json()["user"]
        assert u["email"] == user_ctx["email"]
        # trial should be active for new user
        assert u.get("is_pro") is True

    def test_account_export_still_works(self, user_ctx):
        r = requests.get(f"{BASE_URL}/api/account/export", headers=_auth(user_ctx["token"]))
        assert r.status_code == 200
        j = r.json()
        assert "profile" in j
        assert "chat_history" in j

    def test_progress_endpoint(self, user_ctx):
        r = requests.get(f"{BASE_URL}/api/progress", headers=_auth(user_ctx["token"]))
        assert r.status_code == 200
        j = r.json()
        assert "badges" in j
        assert "total_lessons" in j

    def test_stocks_endpoint(self, user_ctx):
        r = requests.get(f"{BASE_URL}/api/stocks", headers=_auth(user_ctx["token"]))
        assert r.status_code == 200
        assert "stocks" in r.json()


class TestDeleteAccountFlow:
    """Delete-account flow with a fresh throwaway user (isolated fixture)."""

    def test_delete_account_returns_and_invalidates(self):
        token, _, _, _ = _signup()
        r = requests.delete(f"{BASE_URL}/api/account", headers=_auth(token))
        assert r.status_code == 200
        assert r.json().get("deleted") is True
        # subsequent /auth/me should be 401
        me = requests.get(f"{BASE_URL}/api/auth/me", headers=_auth(token))
        assert me.status_code in (401, 403, 404)
